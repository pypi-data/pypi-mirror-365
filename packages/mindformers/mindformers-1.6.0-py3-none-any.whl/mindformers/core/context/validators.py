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
"""The validators of config."""

import inspect
from enum import Enum

from mindformers.tools import MODE, PARALLEL_MODE
from mindformers.version_control import check_tft_valid


class RunMode(Enum):
    TRAIN = 'train'
    PREDICT = 'predict'
    FINETUNE = 'finetune'
    EVAL = 'eval'


def validate_mf_ctx_run_mode(config):
    """Validate run_mode in mindformers context."""
    members = [k.lower() for k, _ in RunMode.__members__.items()]
    run_mode = config.run_mode
    if run_mode is not None and run_mode not in members:
        raise ValueError(
            f'Invalid run_mode. Expected one of {members}, got {run_mode}'
        )


def validate_ms_ctx_mode(config):
    """Validate mode in context."""
    mode = config.get_value('context.mode', 0)
    if mode not in MODE.keys():
        raise ValueError(
            f'Invalid mode. Expected one of {MODE.keys()}, got {mode}'
        )
    config.set_value('context.mode', mode)


def validate_parallel_mode(config):
    """Validate parallel mode in parallel."""
    parallel_mode = config.get_value('parallel.parallel_mode', 0)
    if parallel_mode not in PARALLEL_MODE:
        raise ValueError(
            'Invalid parallel mode. Expected one of '
            f'{PARALLEL_MODE.keys()}, got {parallel_mode}'
        )
    config.set_value('parallel.parallel_mode', PARALLEL_MODE.get(parallel_mode))


def validate_sink_size(config):
    """Validate sink size."""
    if check_tft_valid():
        sink_size = config.get_value('runner_config.sink_size')
        if sink_size != 1:
            raise ValueError(f'sink_size should be 1, got {sink_size}')


def validate_precision_sync(config):
    """Validate train_percision_sync and infer_percision_sync."""
    train_precision_sync = config.get_value('train_precision_sync')
    infer_percision_sync = config.get_value('train_precision_sync')
    if train_precision_sync is not None and not isinstance(
            train_precision_sync, bool):
        raise ValueError(
            f'train_percision_sync should be bool, got {train_precision_sync}')
    if infer_percision_sync is not None and not isinstance(
            infer_percision_sync, bool):
        raise ValueError(
            f'train_percision_sync should be bool, got {infer_percision_sync}')


def validate_invalid_predict_mode(config):
    """Validate invalid predict mode when using FA but use_past is False."""
    run_mode = config.get_value('run_mode')
    use_past = config.get_value('model.model_config.use_past')
    use_flash_attention = config.get_value('model.model_config.use_flash_attention')
    if run_mode == RunMode.PREDICT.value and use_past is False and use_flash_attention is True:
        raise ValueError("Conflict detected in predict mode: "
                         "Flash Attention is incompatible when use_past=False")


def execute_validator(config):
    """Execute all validate function."""
    current_module = inspect.getmodule(inspect.currentframe())
    functions = inspect.getmembers(current_module, inspect.isfunction)
    for func_name, func in functions:
        if func_name.startswith('validate'):
            func(config)
