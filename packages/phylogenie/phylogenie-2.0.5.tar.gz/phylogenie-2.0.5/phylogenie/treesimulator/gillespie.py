from collections.abc import Sequence

import numpy as np
from numpy.random import default_rng

from phylogenie.tree import Tree
from phylogenie.treesimulator.events import Event
from phylogenie.treesimulator.model import Model


def simulate_tree(
    events: Sequence[Event],
    min_tips: int = 1,
    max_tips: int | None = None,
    max_time: float = np.inf,
    init_state: str | None = None,
    sampling_probability_at_present: float = 0.0,
    max_tries: int | None = None,
    seed: int | None = None,
) -> Tree | None:
    rng = default_rng(seed)

    if max_tips is None and max_time == np.inf:
        raise ValueError("Either max_tips or max_time must be specified.")

    n_tries = 0
    states = [e.state for e in events if e.state is not None]
    init_state = (
        init_state
        if init_state is not None
        else str(rng.choice(states)) if states else None
    )
    while max_tries is None or n_tries < max_tries:
        model = Model(init_state)
        current_time = 0.0
        change_times = sorted(set(t for e in events for t in e.rate.change_times))
        next_change_time = change_times.pop(0) if change_times else np.inf
        n_tips = None if max_tips is None else rng.integers(min_tips, max_tips + 1)

        while current_time < max_time and (n_tips is None or model.n_sampled < n_tips):
            rates = [e.get_propensity(model, current_time) for e in events]
            if not any(rates):
                break

            current_time += rng.exponential(1 / sum(rates))
            if current_time >= max_time:
                break

            if current_time >= next_change_time:
                current_time = next_change_time
                next_change_time = change_times.pop(0) if change_times else np.inf
                continue

            event_idx = np.searchsorted(np.cumsum(rates) / sum(rates), rng.random())
            events[int(event_idx)].apply(rng, model, current_time)

        for leaf in model.get_leaves():
            if rng.random() < sampling_probability_at_present:
                model.sample(leaf, current_time, True)

        if model.n_sampled >= min_tips and (
            max_tips is None or model.n_sampled <= max_tips
        ):
            return model.get_sampled_tree()

        n_tries += 1
