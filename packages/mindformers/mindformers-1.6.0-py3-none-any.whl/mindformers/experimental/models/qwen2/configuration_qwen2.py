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
"""Qwen2 Config API."""

from typing import Optional, Union

from mindspore._checkparam import args_type_check

from mindformers.modules.transformer.moe import MoEConfig
from mindformers.modules.transformer.transformer import default_transformer_config, \
    TransformerOpParallelConfig, default_moe_config
from mindformers.tools.register import MindFormerRegister, MindFormerModuleType
from mindformers.models.configuration_utils import PretrainedConfig
from mindformers.models.utils import convert_mstype

__all__ = ['Qwen2Config']


@MindFormerRegister.register(MindFormerModuleType.CONFIG)
class Qwen2Config(PretrainedConfig):

    """ Qwen2 Model Config """

    model_type = "Qwen2"

    @args_type_check(parallel_config=(dict, TransformerOpParallelConfig))
    def __init__(self,
                 vocab_size: int = 151936,
                 hidden_size: int = 4096,
                 intermediate_size: Optional[int] = 22016,
                 num_hidden_layers: int = 32,
                 num_attention_heads: int = 32,
                 num_key_value_heads: Optional[int] = 32,
                 hidden_act: str = "silu",
                 max_position_embedding: Optional[int] = 32768,
                 rms_norm_eps: float = 1e-6,
                 tie_word_embeddings: bool = False,
                 rope_theta: float = 10000.0,
                 batch_size: int = 1,
                 seq_length: int = 2048,
                 multiple_of: int = 256,
                 ffn_dim_multiplier: Optional[int] = None,
                 normalization: str = "RMSNorm",
                 compute_dtype: str = "float16",
                 layernorm_compute_type: str = "float32",
                 softmax_compute_type: str = "float32",
                 rotary_dtype: str = "float32",
                 param_init_type: str = "float16",
                 residual_dtype: str = None,
                 embedding_init_type=None,
                 qkv_has_bias: bool = False,
                 qkv_concat: bool = False,
                 attn_proj_has_bias: bool = False,
                 out_proj_has_bias: bool = False,
                 mlp_has_bias: bool = False,
                 parallel_config: Union[dict, TransformerOpParallelConfig] = default_transformer_config,
                 moe_config: Union[dict, MoEConfig] = default_moe_config,
                 extend_method: str = "None",
                 scaling_factor: float = 1.0,
                 use_flash_attention: bool = False,
                 block_size: int = 16,
                 num_blocks: int = 512,
                 quant_config: dict = None,
                 parallel_decoding_params: dict = None,
                 **kwargs):
        """
        Qwen2 config class which defines the model size.

        Args:
            vocab_size (int): Vocabulary size of the qwen2 model. Default: ``151936``.
            hidden_size (int): Dimensionality of the encoder layers and the pooler layer. Default: ``4096``.
            intermediate_size (int): Customize the number of dimension of the intermediate layer.
                Default: ``22016``.
            num_hidden_layers (int): Number of hidden layers in the Transformer decoder. Default: ``32``.
            num_attention_heads (int): Number of attention heads for each attention layer in the Transformer decoder.
                Default: ``32``.
            num_key_value_heads (int): Define multi group head attention heads number. Default: ``32``.
            hidden_act (str): Specifies the activation function for hidden layers. Default: ``silu``.
            max_position_embedding (int): Customize the maximum sequence length that the model can handle.
                Default: "32768".
            rms_norm_eps (float): The epsilon value of the denominator. Default: ``1e-6``.
            tie_word_embeddings (bool): Whether to tie input and output embeddings. Default: ``False``.
            rope_theta (float): Frequency factors for sine and cosine functions in RoPE. Default: ``10000.0``.
            batch_size (int): Batch size for input data, use in predict. Default: ``1``.
            seq_length (int): The sequence length of input_ids. Default: ``2048``.
            multiple_of (int): Define SwiGLU hidden layer size multiples. Default: ``256``.
            ffn_dim_multiplier (int): Define ffn layer dim multiples. Default: ``None``.
            bos_token_id (int): The id of the *beginning-of-sequence* token. Default: ``1``.
            eos_token_id (int): The id of the *end-of-sequence* token. Default: ``2``.
            pad_token_id (int): The id of the *padding* token. Default: ``0``.
            normalization (str): Defines the normalization layer type. Default: ``RMSNorm``.
            compute_dtype (str): Linear layer compute dtype. Default: ``float16``.
            layernorm_compute_type (str): Layernorm compute dtype. Default: ``float32``.
            softmax_compute_type (str): Softmax compute dtype. Default: ``float32``.
            rotary_dtype (str): RoPE compute dtype. Default: ``float32``.
            param_init_type (str): Parameter initial dtype. Default: ``float16``.
            residual_dtype (str): Residual compute dtype. Default: ``None``.
            embedding_init_type (str): Embedding weight initial dtype. Default: ``None``.
            qkv_has_bias (bool): Whether the Query, Key, and Value projection has bias. Default: ``False``.
            qkv_concat (bool): Whether concatenate the Query, Key, and Value projection. Default: ``False``.
            attn_proj_has_bias (bool): Whether the attn projection has bias. Default: ``False``.
            out_proj_has_bias (bool): Whether the wo projection has bias. Default: ``False``.
            mlp_has_bias (bool): Whether the attn mlp has bias. Default: ``False``.
            parallel_config (Union[dict, TransformerOpParallelConfig]): The parallel configuration.
            moe_config (Union[dict, MoEConfig]): The MoE configuration. Default: ``default_moe_config`` ,
                an instance of `MoEConfig` with default args.
            extend_method (str): The extent method of seq length in inference. Default: ``None``.
            scaling_factor (float): Scaling factor to adjust the weights of the frequency factors in the sine
                and cosine functions. Default: ``1.0``.
            use_flash_attention (bool): Whether to enable flash attention ops. Default: ``False``.
            repetition_penalty (float): The parameter for repetition penalty. 1.0 means no penalty.
                See `this paper <https://arxiv.org/pdf/1909.05858.pdf>`_ for more details. Default: ``1.0``.
            max_decode_length (int): The maximum length the generated tokens can have.
            block_size (int): The maximum number of tokens in one block can have when using paged attention.
                Default: ``16``.
            num_blocks (int): The maximum number of blocks when using paged attention. Default: ``512``.
            top_k (int): The number of highest probability vocabulary tokens to keep for top-k-filtering.
                Default: ``5``.
            top_p (float): If set to float < 1, only the smallest set of most probable tokens with probabilities
                that add up to `top_p` or higher are kept for generation. Default: ``1.0``.
            do_sample (bool): Whether to use sampling; use greedy decoding otherwise. Default: ``True``.
            quant_config (dict): Quantitative configuration. Default: ``None``.
            parallel_decoding_params (dict): Parallel decoding params. Default: ``None``.
            kwargs: Other arguments.

        """
        super(Qwen2Config, self).__init__(**kwargs)
        # hf params
        self.vocab_size = vocab_size
        self.max_position_embedding = max_position_embedding if max_position_embedding else seq_length
        self.intermediate_size = intermediate_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        if num_key_value_heads is None:
            num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.rms_norm_eps = rms_norm_eps
        self.rope_theta = rope_theta
        self.tie_word_embeddings = tie_word_embeddings
        # common params
        if isinstance(parallel_config, dict):
            parallel_config = TransformerOpParallelConfig(**parallel_config)
        if isinstance(moe_config, dict):
            moe_config = MoEConfig(**moe_config)
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.multiple_of = multiple_of
        self.ffn_dim_multiplier = ffn_dim_multiplier
        self.normalization = normalization
        self.compute_dtype = convert_mstype(compute_dtype)
        self.layernorm_compute_type = convert_mstype(layernorm_compute_type)
        self.softmax_compute_type = convert_mstype(softmax_compute_type)
        self.rotary_dtype = convert_mstype(rotary_dtype)
        self.param_init_type = convert_mstype(param_init_type)
        if residual_dtype is not None:
            self.residual_dtype = convert_mstype(residual_dtype)
        else:
            self.residual_dtype = self.compute_dtype
        if embedding_init_type is not None:
            self.embedding_init_type = convert_mstype(embedding_init_type)
        else:
            self.embedding_init_type = self.param_init_type
        self.qkv_has_bias = qkv_has_bias
        self.qkv_concat = qkv_concat
        self.attn_proj_has_bias = attn_proj_has_bias
        self.out_proj_has_bias = out_proj_has_bias
        self.mlp_has_bias = mlp_has_bias
        self.parallel_config = parallel_config
        self.moe_config = moe_config
        self.extend_method = extend_method
        self.scaling_factor = scaling_factor
        self.use_flash_attention = use_flash_attention
        # # infer params
        self.parallel_decoding_params = parallel_decoding_params
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.quant_config = quant_config
