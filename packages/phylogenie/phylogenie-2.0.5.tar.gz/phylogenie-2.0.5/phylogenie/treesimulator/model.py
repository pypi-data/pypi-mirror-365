from collections import defaultdict

from numpy.random import Generator, default_rng

from phylogenie.tree import Tree


class Model:
    def __init__(self, init_state: str | None = None):
        self._next_id = 0
        self._n_sampled = 0
        self._leaves: dict[str, Tree] = {}
        self._leaf2state: dict[str, str | None] = {}
        self._state2leaves: dict[str | None, set[str]] = defaultdict(set)
        self._tree = self._get_new_node(init_state, None)

    @property
    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    @property
    def n_sampled(self) -> int:
        return self._n_sampled

    def _get_new_node(self, state: str | None, branch_length: float | None) -> Tree:
        id = str(self.next_id) if state is None else f"{self.next_id}|{state}"
        node = Tree(id, branch_length)
        if branch_length is None:
            self._leaves[id] = node
            self._leaf2state[id] = state
            self._state2leaves[state].add(id)
        return node

    def remove(self, node_id: str) -> None:
        self._state2leaves[self._leaf2state[node_id]].remove(node_id)
        self._leaf2state.pop(node_id, None)
        self._leaves.pop(node_id)

    def add_child(
        self,
        node_id: str,
        time: float,
        stem: bool,
        state: str | None,
        branch_length: float | None = None,
    ) -> None:
        node = self._leaves[node_id]
        if node.branch_length is not None:
            raise ValueError("Cannot add a child to a node with a set branch length.")
        node.add_child(self._get_new_node(state, branch_length))
        if stem:
            node.add_child(self._get_new_node(self._leaf2state[node.id], None))
        node.branch_length = (
            time if node.parent is None else time - node.parent.get_time()
        )
        self.remove(node_id)

    def sample(self, node_id: str, time: float, remove: bool) -> None:
        self.add_child(node_id, time, not remove, self._leaf2state[node_id], 0.0)
        self._n_sampled += 1

    def get_sampled_tree(self) -> Tree:
        tree = self._tree.copy()
        for node in list(tree.postorder_traversal()):
            if node.branch_length is None or (
                node.branch_length > 0 and not node.children
            ):
                if node.parent is None:
                    raise ValueError("No samples in the tree.")
                else:
                    node.parent.children.remove(node)
            elif len(node.children) == 1:
                (child,) = node.children
                child.parent = node.parent
                assert child.branch_length is not None
                assert node.branch_length is not None
                child.branch_length += node.branch_length
                if node.parent is None:
                    return child
                else:
                    node.parent.children.append(child)
                    node.parent.children.remove(node)
        return tree

    def get_random_leaf(
        self, state: str | None = None, rng: int | Generator | None = None
    ) -> str:
        rng = rng if isinstance(rng, Generator) else default_rng(rng)
        if state is None:
            return rng.choice(list(self._leaves))
        return rng.choice(list(self._state2leaves[state]))

    def get_leaves(self) -> list[str]:
        return list(self._leaves)

    def count_leaves(self, state: str | None = None) -> int:
        if state is None:
            return len(self._leaves)
        return len(self._state2leaves[state])
