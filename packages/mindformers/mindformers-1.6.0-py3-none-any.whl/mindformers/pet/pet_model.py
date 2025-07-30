# Copyright 2023 Huawei Technologies Co., Ltd
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
"""Pet model for llm model."""
from typing import Union

from mindspore._checkparam import args_type_check

from mindformers.models.modeling_utils import PreTrainedModel
from mindformers.pet.constants import PetType
from mindformers.pet.models.lora import LoraModel
from mindformers.pet.models.ptuning2 import Ptuning2Model
from mindformers.pet.models.prefix_tuning import PrefixTuningModel
from mindformers.pet.models.slora import SLoraModel
from mindformers.pet.pet_config import LoraConfig, PetConfig, Ptuning2Config, PrefixTuningConfig
from mindformers.pet.tuners.pet_adapter import PetAdapter
from mindformers.pet.tuners.slora_adapter import SLoraAdapter
from mindformers.tools.logger import logger
from mindformers.parallel_core.utils.model_mixin import TrainModelMixin

# Mapping of pet models.
PET_TYPE_TO_MODEL_MAPPING = {
    PetType.LORA.value: LoraModel,
    PetType.PREFIX_TUNING.value: PrefixTuningModel,
    PetType.P_TUNING_V2.value: Ptuning2Model
}

# Mapping of pet configs.
PET_TYPE_TO_CONFIG_MAPPING = {
    PetType.LORA.value: LoraConfig,
    PetType.PREFIX_TUNING.value: PrefixTuningConfig,
    PetType.P_TUNING_V2.value: Ptuning2Config
}


class PetModel(PreTrainedModel):
    """
    PetModel define parameter efficient tuning model for LLM model.
    Args:
        config(PetConfig): pet config,define parameters efficient tuning algorithm.
        base_model(PreTrainedModel): pretrained model for tuning.
    """

    @args_type_check(config=(dict, PetConfig))
    def __init__(self, config: Union[dict, PetConfig], base_model: PreTrainedModel):
        super().__init__(base_model.config, auto_prefix=False)
        if not isinstance(config, PetConfig):
            pet_type = config.pop("pet_type")
            pet_config = PET_TYPE_TO_CONFIG_MAPPING[pet_type](**config)
        else:
            pet_type = config.pet_type
            pet_config = config
        self.config.pet_config = pet_config
        # pylint: disable=W0212
        self._support_list = base_model._support_list
        self.network = PET_TYPE_TO_MODEL_MAPPING[pet_type](pet_config, base_model)
        self.load_checkpoint(self.config)
        if isinstance(base_model, TrainModelMixin):
            PetAdapter.freeze_mcore_pretrained_model(self.network, pet_config.freeze_include,
                                                     pet_config.freeze_exclude)
        else:
            PetAdapter.freeze_pretrained_model(self.network, pet_type, pet_config.freeze_include,
                                               pet_config.freeze_exclude)

    def update_model_kwargs_before_generate(self, input_ids, model_kwargs: dict):
        return self.network.update_model_kwargs_before_generate(input_ids, model_kwargs)

    def prepare_inputs_for_generation(self, input_ids, **kwargs):
        return self.network.prepare_inputs_for_generation(input_ids, **kwargs)

    def prepare_inputs_for_predict_layout(self, input_ids, **kwargs):
        return self.network.prepare_inputs_for_predict_layout(input_ids, **kwargs)

    def slice_incremental_inputs(self, model_inputs: dict, current_index):
        return self.network.slice_incremental_inputs(model_inputs, current_index)

    def set_dynamic_inputs(self, **kwargs):
        return self.network.set_dynamic_inputs(**kwargs)

    def add_flags_custom(self, is_first_iteration):
        return self.network.add_flags_custom(is_first_iteration)

    def to_embeddings(self, tokens):
        return self.network.to_embeddings(tokens)

    def convert_name(self, weight_name):
        return self.network.convert_name(weight_name)

    def convert_weight_dict(self, source_dict, **kwargs):
        return self.network.convert_weight_dict(source_dict, **kwargs)

    def convert_map_dict(self, source_dict, **kwargs):
        return self.network.convert_map_dict(source_dict, **kwargs)

    def obtain_name_map(self, load_checkpoint_files):
        return self.network.obtain_name_map(load_checkpoint_files)

    def construct(self, *inputs, **kwargs):
        return self.network(*inputs, **kwargs)


@args_type_check(config=(dict, PetConfig))
def get_pet_model(base_model: PreTrainedModel, config: Union[dict, PetConfig]):
    """
    Get model with pet model.

    Args:
        base_model (PreTrainedModel): The pretrained model for tuning.
        config (PetConfig): The config of parameter efficient tuning algrithm.

    Return:
        model(PreTrainedModel)
    """
    pet_type = config.get("pet_type")
    if pet_type == "slora":
        logger.info("Apply S-LoRA to model.")
        pet_config = SLoraAdapter.init_slora_config(config)
        return SLoraModel(pet_config, base_model)

    if not PET_TYPE_TO_MODEL_MAPPING.get(pet_type):
        logger.warning("%s doesn't have pet model currently.", pet_type)
        return base_model

    if type(base_model).__name__ == "ChatGLM2WithPtuning2":
        return base_model
    # return pet model.
    return PetModel(config=config, base_model=base_model)


def is_supported_pet_type(pet_type: str):
    """
    Return `pet_type` is supported or not.
    """

    return pet_type in PET_TYPE_TO_MODEL_MAPPING
