# Copyright 2025 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Router For MoE."""
from abc import ABC, abstractmethod

from mindspore import nn
from mindspore.common import dtype as mstype, Parameter, Tensor
from mindspore.common.initializer import initializer
from mindspore.context import ParallelMode
from mindspore.mint.nn.functional import linear
from mindspore.ops.auto_generate import AddExt, AssignAdd, Cast, Div, Mul, Reshape, Sigmoid, Softmax, TopkExt
# these ops are not supported in auto_generate
from mindspore.ops.operations import Shape, Gather, ReduceSum, ReduceMean, OneHot
from mindspore.parallel._utils import _get_parallel_mode

from mindformers.parallel_core.transformer_config import TransformerConfig

GATING_ACTIVATION = {
    "softmax": Softmax(axis=-1),
    "sigmoid": Sigmoid(),
}


class Router(ABC, nn.Cell):
    """Base Router class"""

    def __init__(
            self,
            config: TransformerConfig,
    ):
        """Initialize the Router module.

        Args:
            config (TransformerConfig): Configuration object for the Transformer model.
        """
        super(Router, self).__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.expert_dim = config.num_moe_experts
        self.num_experts_chosen = config.moe_router_topk
        self.moe_router_dtype = config.moe_router_dtype

        weight_shape = (self.expert_dim, self.hidden_size)
        self.weight = Parameter(config.init_method(weight_shape), name='weight')

    @abstractmethod
    def shard(self, config: TransformerConfig):
        pass

    def gating(self, inputs):
        """Forward pass of the router gate.

        Args:
            inputs (Tensor): Input tensor.

        Returns:
            Tensor: Logits tensor.
        """
        # (dp, N, E) fp32 <-- (dp, N, h)
        # seems good for no sharding
        weight = self.weight.astype(self.moe_router_dtype)
        router_logits = linear(inputs.astype(self.moe_router_dtype), weight)
        return router_logits


class TopKRouter(Router):
    """Route each token to the top-k experts."""

    def __init__(self, config: TransformerConfig):
        """Initialize the zero token dropping router.

        Args:
            config (TransformerConfig): The configuration for the transformer model.
        """
        super(TopKRouter, self).__init__(config)
        self.shape = Shape()
        self.reshape = Reshape()
        self.cast = Cast()
        # constant values for mask
        self.on_value = Tensor(1.0, dtype=mstype.float32)
        self.off_value = Tensor(0.0, dtype=mstype.float32)
        # for scaling factor
        self.mul = Mul()
        # normalize
        self.reduce_sum_keep = ReduceSum(keep_dims=True)
        self.add_eps = AddExt()
        self.div_3d = Div()
        # gating activation, softmax or sigmoid
        gating_type = config.moe_router_score_function
        self.use_gating_sigmoid = (gating_type == "sigmoid")
        self.gating_activation = GATING_ACTIVATION[gating_type]
        # topk
        self.topk = TopkExt()
        self.topk.recompute(False)
        # topk_with_bias
        self.moe_router_enable_expert_bias = config.moe_router_enable_expert_bias
        if self.moe_router_enable_expert_bias:
            self.expert_bias = Parameter(initializer('zeros', (self.expert_dim), mstype.float32),
                                         requires_grad=False, parallel_optimizer=False)
            self.gate_gather = Gather(batch_dims=2)
            self.expert_load = Parameter(initializer('zeros', (self.expert_dim), mstype.float32),
                                         requires_grad=False, parallel_optimizer=False)
            self.assign_add = AssignAdd()
            self.assign_add.recompute(False)
            self.onehot_2d = OneHot()
            self.reduce_mean = ReduceMean(keep_dims=False)
            self.afb_reduce_mean = ReduceMean(keep_dims=False)
            self.afb_topk = TopkExt()
            self.afb_topk.recompute(False)
            self.afb_add_topk_bias = AddExt()
            self.afb_add_topk_bias.recompute(False)

        # for aux loss
        self.dp = config.data_parallel_size * config.tensor_model_parallel_size * config.context_parallel_size
        self.reduce_mean_aux_3d = ReduceMean(keep_dims=False)
        self.reduce_mean_aux_2d = ReduceMean(keep_dims=False)
        self.mul_aux_2d = Mul()
        self.onehot_aux = OneHot()
        self.mul_noshard = Mul()
        self.add_loss = AddExt()
        self.aux_loss_config = dict(zip(config.aux_loss_types, config.aux_loss_factors))
        self.aux_loss_factor = self.aux_loss_config.get("expert", 0.0)

        # shard all the ops
        if _get_parallel_mode() in (ParallelMode.SEMI_AUTO_PARALLEL,):
            self.shard(config)

    def routing(self, logits: Tensor):
        """Top-k routing function

        Args:
            logits (Tensor): Logits tensor after gating.

        Returns:
            probs (Tensor): The probabilities of token to experts assignment.
            expert_index (Tensor): The mapping of token to experts assignment,
                with shape [num_tokens, num_experts_chosen].
            router_prob_for_aux (Tensor): The probabilities of token to compute aux loss.
        """
        # (dp, N, E) fp32 <-- (dp, N, E) fp32
        router_prob = self.gating_activation(logits)
        # (dp, N, E) fp32 <-- (dp, N, E) fp32
        router_prob_for_aux = self._normalize(router_prob) if self.use_gating_sigmoid else router_prob
        # (dp, N, k) fp32,  (dp, N, k) int32 <-- (dp, N, E) fp32
        expert_gate, expert_index = self._topk(router_prob)
        if self.num_experts_chosen > 1 and self.config.norm_topk_prob:
            # (dp, N, k) fp32 <-- (dp, N, k) fp32
            probs = self._normalize(expert_gate)
        else:
            probs = expert_gate
        probs = self.mul(self.config.moe_router_topk_scaling_factor, probs)
        return probs, expert_index, router_prob_for_aux

    def _normalize(self, x):
        """Forward of normalization."""
        # The shape change is: (dp, N, 1) <-- (dp, N, k)
        y = self.reduce_sum_keep(x, 2)
        # The shape change is: (dp, N, k) <-- (dp, N, k) (dp, N, 1)
        x = self.div_3d(x, self.add_eps(y, 1e-20))
        # The shape change is: (dp, N, k)
        return x

    def _topk(self, router_prob):
        """Forward of topk routing."""
        # topk with bias
        if self.moe_router_enable_expert_bias:
            return self._topk_with_bias(router_prob)
        # normal topk
        expert_gate, expert_index = self.topk(router_prob, self.num_experts_chosen)
        expert_index = self.cast(expert_index, mstype.int32)
        return expert_gate, expert_index

    def _topk_with_bias(self, router_prob):
        """compute topk with bias."""
        _, expert_index = self.afb_topk(
            self.afb_add_topk_bias(router_prob, self.expert_bias),
            self.num_experts_chosen
        )
        # expert_index will be int64 without this cast,
        # and compile fails for the grad ReduceScatter don't support int64
        expert_index = self.cast(expert_index, mstype.int32)
        expert_gate = self.gate_gather(router_prob, expert_index, 2)
        self._update_expert_load(expert_index)
        return expert_gate, expert_index

    def _update_expert_load(self, expert_index):
        """update experts load balance."""
        expert_index = self.reshape(expert_index, (expert_index.shape[0], -1))
        expert_mask = self.onehot_2d(expert_index, self.expert_dim, self.on_value, self.off_value)
        expert_load_data = self.reduce_mean(expert_mask, 1)
        expert_load_data = self.afb_reduce_mean(expert_load_data, 0)
        self.assign_add(self.expert_load, expert_load_data)

    def _expert_load_balancing(self, scores, top_indices, alpha):
        """Apply sequence-auxiliary loss-based load balancing to the logits tensor."""
        scores = self.reshape(scores, (self.dp, -1, scores.shape[2]))
        top_indices = self.reshape(top_indices, (self.dp, -1, top_indices.shape[2]))
        # The shape change is: p  (dp, E) <- (dp, N, E) fp32
        pi = self.reduce_mean_aux_3d(scores, 1)

        # f  (dp, Nk)int32, (dp, N, k)int32
        top_indices = self.reshape(top_indices, (top_indices.shape[0], -1))
        # (dp, kN, E)fp32 <-- (dp, kN)int32
        mask = self.onehot_aux(top_indices, self.expert_dim, self.on_value, self.off_value)
        # The shape change is: (dp, E) <- (dp, kN, E)
        fi = self.reduce_mean_aux_3d(mask, 1)
        # The shape change is: p*f  (dp) <- (dp, E)
        expert_load_loss = self.reduce_mean_aux_2d(self.mul_aux_2d(pi, fi))
        # alpha*E \sum_i^E (f_i * P_i)
        expert_load_loss = self.mul_noshard(expert_load_loss, alpha * self.expert_dim ** 2)
        return expert_load_loss

    def construct(self, inputs):
        """Construct function of TopKRouter."""
        # 1. gating
        router_logits = self.gating(inputs)
        # 2. topk & norm
        router_coeff, expert_index, router_prob_for_aux = self.routing(router_logits)
        # 3. expert load balancing
        # float32 <-- (dp, N, E) fp32, (dp, N, k) int32, float32
        router_aux_loss = self._expert_load_balancing(router_prob_for_aux, expert_index, self.aux_loss_factor)

        return expert_index, router_coeff, router_aux_loss

    def shard(self, config: TransformerConfig):
        """
        Handles the sharding configuration for the model's parallelism settings.
        """
        dp = config.data_parallel_size * config.tensor_model_parallel_size * config.context_parallel_size
        # for scaling factor
        self.mul.shard(((), (dp, 1, 1)))
        # normalize
        self.reduce_sum_keep.shard(((dp, 1, 1),))
        self.add_eps.shard(((dp, 1, 1), ()))
        self.div_3d.shard(((dp, 1, 1), (dp, 1, 1)))
        # gating activation, softmax or sigmoid
        self.gating_activation.shard(((dp, 1, 1,),))
        # topk
        self.topk.shard(((dp, 1, 1),))
        # topk_with_bias
        if self.moe_router_enable_expert_bias:
            self.gate_gather.shard(((dp, 1, 1), (dp, 1, 1)))
            self.assign_add.shard(((1,), (1,)))
            self.onehot_2d.shard(((dp, 1, 1), (), ()))
            self.reduce_mean.shard(((dp, 1, 1),))
            self.afb_reduce_mean.shard(((dp, 1),))
            self.afb_topk.shard(((dp, 1, 1),))
            self.afb_add_topk_bias.shard(((dp, 1, 1), (1,)))
        # for aux loss
        self.reduce_mean_aux_3d.shard(((dp, 1, 1),))
        self.reduce_mean_aux_2d.shard(((dp, 1),))
        self.mul_aux_2d.shard(((dp, 1), (dp, 1)))
        self.onehot_aux.shard(((dp, 1, 1), (), ()))
        self.mul_noshard.shard(((), ()))
        self.add_loss.shard(((1,), ()))
