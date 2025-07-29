from pydantic import BaseModel, ConfigDict

import phylogenie.typings as pgt


class DistributionConfig(BaseModel):
    type: str
    model_config = ConfigDict(extra="allow")


IntegerConfig = str | int
ScalarConfig = str | pgt.Scalar
ManyScalarsConfig = str | list[ScalarConfig]
OneOrManyScalarsConfig = ScalarConfig | list[ScalarConfig]
OneOrMany2DScalarsConfig = ScalarConfig | list[list[ScalarConfig]]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SkylineParameterModel(StrictBaseModel):
    value: ManyScalarsConfig
    change_times: ManyScalarsConfig


class SkylineVectorModel(StrictBaseModel):
    value: str | list[OneOrManyScalarsConfig]
    change_times: ManyScalarsConfig


class SkylineMatrixModel(StrictBaseModel):
    value: str | list[OneOrMany2DScalarsConfig]
    change_times: ManyScalarsConfig


SkylineParameterConfig = ScalarConfig | SkylineParameterModel
SkylineVectorConfig = (
    str | pgt.Scalar | list[SkylineParameterConfig] | SkylineVectorModel
)
SkylineMatrixConfig = (
    str | pgt.Scalar | list[SkylineVectorConfig] | SkylineMatrixModel | None
)
