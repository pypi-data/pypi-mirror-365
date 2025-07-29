from typing import TypeGuard

import phylogenie.generators.configs as cfg
import phylogenie.typings as pgt


def is_list(x: object) -> TypeGuard[list[object]]:
    return isinstance(x, list)


def is_list_of_scalar_configs(x: object) -> TypeGuard[list[cfg.ScalarConfig]]:
    return is_list(x) and all(isinstance(v, cfg.ScalarConfig) for v in x)


def is_list_of_skyline_parameter_configs(
    x: object,
) -> TypeGuard[list[cfg.SkylineParameterConfig]]:
    return is_list(x) and all(isinstance(v, cfg.SkylineParameterConfig) for v in x)


def is_skyline_vector_config(
    x: object,
) -> TypeGuard[cfg.SkylineVectorConfig]:
    return isinstance(
        x, str | pgt.Scalar | cfg.SkylineVectorModel
    ) or is_list_of_skyline_parameter_configs(x)


def is_list_of_skyline_vector_configs(
    x: object,
) -> TypeGuard[list[cfg.SkylineVectorConfig]]:
    return is_list(x) and all(is_skyline_vector_config(v) for v in x)
