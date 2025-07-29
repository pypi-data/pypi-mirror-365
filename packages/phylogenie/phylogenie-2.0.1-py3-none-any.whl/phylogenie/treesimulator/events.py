from abc import ABC, abstractmethod

from numpy.random import Generator

from phylogenie.skyline import (
    SkylineMatrixCoercible,
    SkylineParameterLike,
    SkylineVectorCoercible,
    skyline_matrix,
    skyline_parameter,
    skyline_vector,
)
from phylogenie.treesimulator.model import Model

INFECTIOUS_STATE = "I"
EXPOSED_STATE = "E"
SUPERSPREADER_STATE = "S"


class Event(ABC):
    def __init__(
        self,
        rate: SkylineParameterLike,
        state: str | None = None,
    ):
        self.rate = skyline_parameter(rate)
        self.state = state

    def get_propensity(self, model: Model, time: float) -> float:
        return self.rate.get_value_at_time(time) * model.count_leaves(self.state)

    @abstractmethod
    def apply(self, rng: Generator, model: Model, time: float) -> None: ...


class BirthEvent(Event):
    def __init__(
        self,
        rate: SkylineParameterLike,
        state: str | None = None,
        child_state: str | None = None,
    ):
        super().__init__(rate, state)
        self.child_state = child_state

    def apply(self, rng: Generator, model: Model, time: float) -> None:
        node = model.get_random_leaf(self.state, rng)
        model.add_child(node, time, True, self.child_state)


class DeathEvent(Event):
    def apply(self, rng: Generator, model: Model, time: float) -> None:
        node = model.get_random_leaf(self.state, rng)
        model.remove(node)


class MigrationEvent(Event):
    def __init__(self, state: str, target_state: str, rate: SkylineParameterLike):
        super().__init__(rate, state)
        self.target_state = target_state

    def apply(self, rng: Generator, model: Model, time: float) -> None:
        node = model.get_random_leaf(self.state, rng)
        model.add_child(node, time, False, self.target_state)


class SamplingEvent(Event):
    def __init__(
        self,
        rate: SkylineParameterLike,
        removal_probability: SkylineParameterLike,
        state: str | None = None,
    ):
        super().__init__(rate, state)
        self.removal_probability = skyline_parameter(removal_probability)

    def apply(self, rng: Generator, model: Model, time: float) -> None:
        node = model.get_random_leaf(self.state, rng)
        remove = rng.random() < self.removal_probability.get_value_at_time(time)
        model.sample(node, time, remove)


def get_canonical_events(
    sampling_rates: SkylineVectorCoercible,
    birth_rates: SkylineVectorCoercible = 0,
    death_rates: SkylineVectorCoercible = 0,
    removal_probabilities: SkylineVectorCoercible = 0,
    migration_rates: SkylineMatrixCoercible = 0,
    birth_rates_among_states: SkylineMatrixCoercible = 0,
    states: list[str] | None = None,
) -> list[Event]:
    N = 1 if states is None else len(states)

    birth_rates = skyline_vector(birth_rates, N)
    death_rates = skyline_vector(death_rates, N)
    sampling_rates = skyline_vector(sampling_rates, N)
    removal_probabilities = skyline_vector(removal_probabilities, N)
    if migration_rates and N == 1:
        raise ValueError(f"Migration rates require multiple states (got {states}).")
    if birth_rates_among_states and N == 1:
        raise ValueError(
            f"Birth rates among states require multiple states (got {states})."
        )

    events: list[Event] = []
    for i in range(N):
        state = None if states is None else states[i]
        events.append(BirthEvent(birth_rates[i], state, state))
        events.append(DeathEvent(death_rates[i], state))
        events.append(SamplingEvent(sampling_rates[i], removal_probabilities[i], state))
        if N > 1:
            migration_rates = skyline_matrix(migration_rates, N, N - 1)
            birth_rates_among_states = skyline_matrix(
                birth_rates_among_states, N, N - 1
            )
            assert states is not None
            assert state is not None
            for j, other_state in enumerate([s for s in states if s != state]):
                events.append(MigrationEvent(state, other_state, migration_rates[i][j]))
                events.append(
                    BirthEvent(birth_rates_among_states[i][j], state, other_state)
                )
    return [event for event in events if event.rate]


def get_epidemiological_events(
    sampling_proportions: SkylineVectorCoercible = 1,
    reproduction_numbers: SkylineVectorCoercible = 0,
    become_uninfectious_rates: SkylineVectorCoercible = 0,
    removal_probabilities: SkylineVectorCoercible = 1,
    migration_rates: SkylineMatrixCoercible = 0,
    reproduction_numbers_among_states: SkylineMatrixCoercible = 0,
    states: list[str] | None = None,
) -> list[Event]:
    N = 1 if states is None else len(states)

    reproduction_numbers = skyline_vector(reproduction_numbers, N)
    become_uninfectious_rates = skyline_vector(become_uninfectious_rates, N)
    sampling_proportions = skyline_vector(sampling_proportions, N)
    removal_probabilities = skyline_vector(removal_probabilities, N)
    if N == 1 and reproduction_numbers_among_states:
        raise ValueError(
            f"Reproduction numbers among states require multiple states (got {states})."
        )
    reproduction_numbers_among_states = (
        skyline_matrix(reproduction_numbers_among_states, N, N - 1) if N > 1 else 0
    )

    birth_rates = reproduction_numbers * become_uninfectious_rates
    sampling_rates = become_uninfectious_rates * sampling_proportions
    birth_rates_among_states = (
        reproduction_numbers_among_states * become_uninfectious_rates
    )
    death_rates = become_uninfectious_rates - removal_probabilities * sampling_rates

    return get_canonical_events(
        states=states,
        birth_rates=birth_rates,
        death_rates=death_rates,
        sampling_rates=sampling_rates,
        removal_probabilities=removal_probabilities,
        migration_rates=migration_rates,
        birth_rates_among_states=birth_rates_among_states,
    )


def get_FBD_events(
    diversification: SkylineVectorCoercible = 0,
    turnover: SkylineVectorCoercible = 0,
    sampling_proportions: SkylineVectorCoercible = 1,
    removal_probabilities: SkylineVectorCoercible = 0,
    migration_rates: SkylineMatrixCoercible = 0,
    diversification_between_types: SkylineMatrixCoercible = 0,
    states: list[str] | None = None,
):
    N = 1 if states is None else len(states)

    diversification = skyline_vector(diversification, N)
    turnover = skyline_vector(turnover, N)
    sampling_proportions = skyline_vector(sampling_proportions, N)
    removal_probabilities = skyline_vector(removal_probabilities, N)
    if N == 1 and diversification_between_types:
        raise ValueError(
            f"Diversification rates among states require multiple states (got {states})."
        )
    diversification_between_types = (
        skyline_matrix(diversification_between_types, N, N - 1) if N > 1 else 0
    )

    birth_rates = diversification / (1 - turnover)
    death_rates = turnover * birth_rates
    sampling_rates = (
        sampling_proportions
        * death_rates
        / (1 - removal_probabilities * sampling_proportions)
    )
    birth_rates_among_states = diversification_between_types + death_rates

    return get_canonical_events(
        states=states,
        birth_rates=birth_rates,
        death_rates=death_rates,
        sampling_rates=sampling_rates,
        removal_probabilities=removal_probabilities,
        migration_rates=migration_rates,
        birth_rates_among_states=birth_rates_among_states,
    )


def get_BD_events(
    reproduction_number: SkylineParameterLike,
    infectious_period: SkylineParameterLike,
    sampling_proportion: SkylineParameterLike = 1,
) -> list[Event]:
    return get_epidemiological_events(
        reproduction_numbers=reproduction_number,
        become_uninfectious_rates=1 / infectious_period,
        sampling_proportions=sampling_proportion,
    )


def get_BDEI_events(
    reproduction_number: SkylineParameterLike,
    infectious_period: SkylineParameterLike,
    incubation_period: SkylineParameterLike,
    sampling_proportion: SkylineParameterLike = 1,
) -> list[Event]:
    return get_epidemiological_events(
        states=[EXPOSED_STATE, INFECTIOUS_STATE],
        sampling_proportions=[0, sampling_proportion],
        become_uninfectious_rates=[0, 1 / infectious_period],
        reproduction_numbers_among_states=[[0], [reproduction_number]],
        migration_rates=[[1 / incubation_period], [0]],
    )


def get_BDSS_events(
    reproduction_number: SkylineParameterLike,
    infectious_period: SkylineParameterLike,
    superspreading_ratio: SkylineParameterLike,
    superspreaders_proportion: SkylineParameterLike,
    sampling_proportion: SkylineParameterLike = 1,
) -> list[Event]:
    f_SS = superspreaders_proportion
    r_SS = superspreading_ratio
    R_0_IS = reproduction_number * f_SS / (1 + r_SS * f_SS - f_SS)
    R_0_SI = (reproduction_number - r_SS * R_0_IS) * r_SS
    R_0_S = r_SS * R_0_IS
    R_0_I = R_0_SI / r_SS
    return get_epidemiological_events(
        states=[INFECTIOUS_STATE, SUPERSPREADER_STATE],
        reproduction_numbers=[R_0_I, R_0_S],
        reproduction_numbers_among_states=[[R_0_IS], [R_0_SI]],
        become_uninfectious_rates=1 / infectious_period,
        sampling_proportions=sampling_proportion,
    )
