# Copyright 2024 Huawei Technologies Co., Ltd
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
"""PTQ Quantizer."""

from mindformers.utils.quantization_config import PTQConfig
from mindformers.modules.quantizers import Quantizer
from mindformers.version_control import check_valid_mindspore_gs


__all__ = ["PtqQuantizer"]


class PtqQuantizer(Quantizer):
    """
    Quantizer of the PTQ method - for PTQ the quantizer support calibration of the model through
    `mindspore_gs` package.
    """

    requires_calibration = False
    required_packages = ["mindspore_gs"]

    def __init__(self, quantization_config: PTQConfig, **kwargs):
        super().__init__(quantization_config, **kwargs)
        self.quant_config = quantization_config
        self.layer_policies = self.quant_config.layer_policies
        self.check_version()

    def check_version(self):
        r"""
        Safety checker
        """
        if self.quant_config is not None and not check_valid_mindspore_gs:
            raise ValueError(
                "PtqQuantizer doesn't support convert quant model with this mindspore_gs version."
            )

    def _dequantize(self, model):
        pass

    def _process_model_before_weight_loading(
            self, model: "PreTrainedModel", **kwargs
    ):
        from mindspore_gs.ptq import PTQ
        ptq = PTQ(config=self.quant_config, layer_policies=self.layer_policies)
        model = ptq.apply(model)
        model = ptq.convert(model)
        return model

    def _process_model_after_weight_loading(self, model, **kwargs):
        return model

    @property
    def is_serializable(self):
        return False

    @property
    def is_trainable(self):
        return False
