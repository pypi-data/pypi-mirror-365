from abc import abstractmethod
from enum import Enum
from typing import Annotated, Any, Literal

import numpy as np
from numpy.random import Generator
from pydantic import Field

import phylogenie.generators.configs as cfg
from phylogenie.generators.dataset import DatasetGenerator, DataType
from phylogenie.generators.factories import (
    integer,
    scalar,
    skyline_matrix,
    skyline_parameter,
    skyline_vector,
)
from phylogenie.io import dump_newick
from phylogenie.tree import Tree
from phylogenie.treesimulator import (
    Event,
    get_BD_events,
    get_BDEI_events,
    get_BDSS_events,
    get_canonical_events,
    get_epidemiological_events,
    get_FBD_events,
    simulate_tree,
)


class ParameterizationType(str, Enum):
    CANONICAL = "canonical"
    EPIDEMIOLOGICAL = "epidemiological"
    FBD = "FBD"
    BD = "BD"
    BDEI = "BDEI"
    BDSS = "BDSS"


class TreeDatasetGenerator(DatasetGenerator):
    data_type: Literal[DataType.TREES] = DataType.TREES
    min_tips: cfg.IntegerConfig = 1
    max_tips: cfg.IntegerConfig | None = None
    max_time: cfg.ScalarConfig = np.inf
    init_state: str | None = None
    sampling_probability_at_present: cfg.ScalarConfig = 0.0
    max_tries: int | None = None

    def simulate_one(self, rng: Generator, data: dict[str, Any]) -> Tree | None:
        events = self._get_events(rng, data)
        init_state = (
            self.init_state
            if self.init_state is None
            else self.init_state.format(**data)
        )
        max_tips = (
            self.max_tips if self.max_tips is None else integer(self.max_tips, data)
        )
        return simulate_tree(
            events=events,
            min_tips=integer(self.min_tips, data),
            max_tips=max_tips,
            max_time=scalar(self.max_time, data),
            init_state=init_state,
            sampling_probability_at_present=scalar(
                self.sampling_probability_at_present, data
            ),
            max_tries=self.max_tries,
            seed=int(rng.integers(2**32)),
        )

    @abstractmethod
    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]: ...

    def _generate_one(
        self, filename: str, rng: Generator, data: dict[str, Any]
    ) -> None:
        tree = self.simulate_one(rng, data)
        if tree is not None:
            dump_newick(tree, f"{filename}.nwk")


class CanonicalTreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.CANONICAL] = (
        ParameterizationType.CANONICAL
    )
    sampling_rates: cfg.SkylineVectorConfig
    birth_rates: cfg.SkylineVectorConfig = 0
    death_rates: cfg.SkylineVectorConfig = 0
    removal_probabilities: cfg.SkylineVectorConfig = 0
    migration_rates: cfg.SkylineMatrixConfig = 0
    birth_rates_among_states: cfg.SkylineMatrixConfig = 0
    states: list[str] | None = None

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_canonical_events(
            states=self.states,
            sampling_rates=skyline_vector(self.sampling_rates, data),
            birth_rates=skyline_vector(self.birth_rates, data),
            death_rates=skyline_vector(self.death_rates, data),
            removal_probabilities=skyline_vector(self.removal_probabilities, data),
            migration_rates=skyline_matrix(self.migration_rates, data),
            birth_rates_among_states=skyline_matrix(
                self.birth_rates_among_states, data
            ),
        )


class EpidemiologicalTreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.EPIDEMIOLOGICAL] = (
        ParameterizationType.EPIDEMIOLOGICAL
    )
    states: list[str] | None = None
    reproduction_numbers: cfg.SkylineVectorConfig = 0
    become_uninfectious_rates: cfg.SkylineVectorConfig = 0
    sampling_proportions: cfg.SkylineVectorConfig = 1
    removal_probabilities: cfg.SkylineVectorConfig = 1
    migration_rates: cfg.SkylineMatrixConfig = 0
    reproduction_numbers_among_states: cfg.SkylineMatrixConfig = 0

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_epidemiological_events(
            states=self.states,
            reproduction_numbers=skyline_vector(self.reproduction_numbers, data),
            become_uninfectious_rates=skyline_vector(
                self.become_uninfectious_rates, data
            ),
            sampling_proportions=skyline_vector(self.sampling_proportions, data),
            removal_probabilities=skyline_vector(self.removal_probabilities, data),
            migration_rates=skyline_matrix(self.migration_rates, data),
            reproduction_numbers_among_states=skyline_matrix(
                self.reproduction_numbers_among_states, data
            ),
        )


class FBDTreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.FBD] = ParameterizationType.FBD
    states: list[str] | None = None
    diversification: cfg.SkylineVectorConfig = 0
    turnover: cfg.SkylineVectorConfig = 0
    sampling_proportions: cfg.SkylineVectorConfig = 1
    removal_probabilities: cfg.SkylineVectorConfig = 0
    migration_rates: cfg.SkylineMatrixConfig = 0
    diversification_between_types: cfg.SkylineMatrixConfig = 0

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_FBD_events(
            states=self.states,
            diversification=skyline_vector(self.diversification, data),
            turnover=skyline_vector(self.turnover, data),
            sampling_proportions=skyline_vector(self.sampling_proportions, data),
            removal_probabilities=skyline_vector(self.removal_probabilities, data),
            migration_rates=skyline_matrix(self.migration_rates, data),
            diversification_between_types=skyline_matrix(
                self.diversification_between_types, data
            ),
        )


class BDTreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.BD] = ParameterizationType.BD
    reproduction_number: cfg.SkylineParameterConfig
    infectious_period: cfg.SkylineParameterConfig
    sampling_proportion: cfg.SkylineParameterConfig = 1

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_BD_events(
            reproduction_number=skyline_parameter(self.reproduction_number, data),
            infectious_period=skyline_parameter(self.infectious_period, data),
            sampling_proportion=skyline_parameter(self.sampling_proportion, data),
        )


class BDEITreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.BDEI] = ParameterizationType.BDEI
    reproduction_number: cfg.SkylineParameterConfig
    infectious_period: cfg.SkylineParameterConfig
    incubation_period: cfg.SkylineParameterConfig
    sampling_proportion: cfg.SkylineParameterConfig = 1

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_BDEI_events(
            reproduction_number=skyline_parameter(self.reproduction_number, data),
            infectious_period=skyline_parameter(self.infectious_period, data),
            incubation_period=skyline_parameter(self.incubation_period, data),
            sampling_proportion=skyline_parameter(self.sampling_proportion, data),
        )


class BDSSTreeDatasetGenerator(TreeDatasetGenerator):
    parameterization: Literal[ParameterizationType.BDSS] = ParameterizationType.BDSS
    reproduction_number: cfg.SkylineParameterConfig
    infectious_period: cfg.SkylineParameterConfig
    superspreading_ratio: cfg.SkylineParameterConfig
    superspreaders_proportion: cfg.SkylineParameterConfig
    sampling_proportion: cfg.SkylineParameterConfig = 1

    def _get_events(self, rng: Generator, data: dict[str, Any]) -> list[Event]:
        return get_BDSS_events(
            reproduction_number=skyline_parameter(self.reproduction_number, data),
            infectious_period=skyline_parameter(self.infectious_period, data),
            superspreading_ratio=skyline_parameter(self.superspreading_ratio, data),
            superspreaders_proportion=skyline_parameter(
                self.superspreaders_proportion, data
            ),
            sampling_proportion=skyline_parameter(self.sampling_proportion, data),
        )


TreeDatasetGeneratorConfig = Annotated[
    CanonicalTreeDatasetGenerator
    | EpidemiologicalTreeDatasetGenerator
    | FBDTreeDatasetGenerator
    | BDTreeDatasetGenerator
    | BDEITreeDatasetGenerator
    | BDSSTreeDatasetGenerator,
    Field(discriminator="parameterization"),
]
