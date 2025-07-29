from typing import Annotated

from pydantic import Field

from phylogenie.generators.alisim import AliSimDatasetGenerator
from phylogenie.generators.dataset import DatasetGenerator
from phylogenie.generators.trees import TreeDatasetGeneratorConfig

DatasetGeneratorConfig = Annotated[
    TreeDatasetGeneratorConfig | AliSimDatasetGenerator,
    Field(discriminator="data_type"),
]

__all__ = ["DatasetGeneratorConfig", "DatasetGenerator"]
