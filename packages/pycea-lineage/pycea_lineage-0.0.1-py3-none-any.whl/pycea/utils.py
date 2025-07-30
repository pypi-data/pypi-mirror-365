from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from typing import Any, cast

import networkx as nx
import numpy as np
import pandas as pd
import scipy as sp
import treedata as td


def get_root(tree: nx.DiGraph):
    """Finds the root of a tree"""
    if not tree.nodes():
        return None  # Handle empty graph case.
    node = next(iter(tree.nodes))
    while True:
        parent = list(tree.predecessors(node))
        if not parent:
            return node  # No predecessors, this is the root
        node = parent[0]


def get_leaves(tree: nx.DiGraph):
    """Finds the leaves of a tree"""
    return [node for node in nx.dfs_postorder_nodes(tree, get_root(tree)) if tree.out_degree(node) == 0]


def get_subtree_leaves(tree: nx.DiGraph, node: str):
    """Finds the leaves of a subtree"""
    return [node for node in nx.dfs_postorder_nodes(tree, node) if tree.out_degree(node) == 0]


def check_tree_has_key(tree: nx.DiGraph, key: str):
    """Checks that tree nodes have a given key."""
    # sample 10 nodes to check if the key is present
    sampled_nodes = random.sample(list(tree.nodes), min(10, len(tree.nodes)))
    for node in sampled_nodes:
        if key not in tree.nodes[node]:
            message = f"One or more nodes do not have {key} attribute."
            if key == "depth":
                message += " You can run `pycea.pp.add_depth` to add depth attribute."
            raise ValueError(message)


def get_keyed_edge_data(
    tdata: td.TreeData, keys: str | Sequence[str], tree: str | Sequence[str] | None = None
) -> pd.DataFrame:
    """Gets edge data for a given key from a tree or set of trees."""
    tree_keys = tree
    if isinstance(tree_keys, str):
        tree_keys = [tree_keys]
    if isinstance(keys, str):
        keys = [keys]
    trees = get_trees(tdata, tree_keys)
    data = []
    for name, value in trees.items():
        edge_data = {key: nx.get_edge_attributes(value, key) for key in keys}
        edge_data = pd.DataFrame(edge_data)
        edge_data["tree"] = name
        edge_data["edge"] = edge_data.index
        data.append(edge_data)
    data = pd.concat(data)
    data = data.set_index(["tree", "edge"])
    return data


def get_keyed_node_data(
    tdata: td.TreeData, keys: str | Sequence[str], tree: str | Sequence[str] | None = None
) -> pd.DataFrame:
    """Gets node data for a given key from a tree or set of trees."""
    tree_keys = tree
    if isinstance(tree_keys, str):
        tree_keys = [tree_keys]
    if isinstance(keys, str):
        keys = [keys]
    trees = get_trees(tdata, tree_keys)
    data = []
    for name, value in trees.items():
        tree_data = {key: nx.get_node_attributes(value, key) for key in keys}
        tree_data = pd.DataFrame(tree_data)
        tree_data["tree"] = name
        data.append(tree_data)
    data = pd.concat(data)
    data["node"] = data.index
    data = data.set_index(["tree", "node"])
    return data


def get_keyed_leaf_data(
    tdata: td.TreeData, keys: str | Sequence[str], tree: str | Sequence[str] | None = None
) -> pd.DataFrame:
    """Gets node data for a given key from a tree or set of trees."""
    tree_keys = tree
    if isinstance(tree_keys, str):
        tree_keys = [tree_keys]
    if isinstance(keys, str):
        keys = [keys]
    trees = get_trees(tdata, tree_keys)
    data = []
    for _, value in trees.items():
        tree_data = {key: nx.get_node_attributes(value, key) for key in keys}
        tree_data = pd.DataFrame(tree_data)
        tree_data = tree_data.loc[list(set(get_leaves(value)).intersection(tree_data.index))]
        data.append(tree_data)
    data = pd.concat(data)
    return data


def _get_categories(data: pd.Series, sort: str | None) -> list[Any]:
    """Gets the categories for a given data series."""
    if sort == "alphabetical":
        categories = sorted(data.drop_duplicates().tolist())
    elif sort == "frequency":
        categories = data.value_counts().index.tolist()
    elif sort == "random":
        categories = data.drop_duplicates().sample(frac=1).tolist()
    elif sort is None:
        categories = data.drop_duplicates().tolist()
    else:
        raise ValueError(f"Unknown sort type: {sort}. Must be 'alphabetical', 'frequency', or 'random'.")
    categories = [cat for cat in categories if pd.notna(cat)]
    return categories


def get_keyed_obs_data(
    tdata: td.TreeData, keys: str | Sequence[str], layer: str | None = None, sort: str | None = None
) -> tuple[pd.DataFrame, bool]:
    """Gets observation data for a given key from a tree."""
    if isinstance(keys, str):
        keys = [keys]
    data = []
    column_keys = False
    array_keys = False
    for key in keys:
        if key in tdata.obs_keys():
            if tdata.obs[key].dtype.kind in ["b", "O", "S"]:
                categories = _get_categories(tdata.obs[key], sort)
                tdata.obs[key] = pd.Categorical(tdata.obs[key], categories=categories, ordered=True)
            data.append(tdata.obs[key])
            column_keys = True
        elif key in tdata.var_names:
            data.append(pd.Series(tdata.obs_vector(key, layer=layer), index=tdata.obs_names))
            column_keys = True
        elif "obsm" in dir(tdata) and key in tdata.obsm.keys():
            if sp.sparse.issparse(tdata.obsm[key]):
                data.append(pd.DataFrame(tdata.obsm[key].toarray(), index=tdata.obs_names))  # type: ignore
            else:
                data.append(pd.DataFrame(tdata.obsm[key], index=tdata.obs_names))  # type: ignore
            array_keys = True
        elif "obsp" in dir(tdata) and key in tdata.obsp.keys():
            if sp.sparse.issparse(tdata.obsp[key]):
                data.append(pd.DataFrame(tdata.obsp[key].toarray(), index=tdata.obs_names, columns=tdata.obs_names))  # type: ignore
            else:
                data.append(pd.DataFrame(tdata.obsp[key], index=tdata.obs_names, columns=tdata.obs_names))  # type: ignore
            array_keys = True
        else:
            raise ValueError(
                f"Key {key!r} is invalid! You must pass a valid observation annotation. "
                f"One of obs_keys, var_names, obsm_keys, obsp_keys."
            )
    if column_keys and array_keys:
        raise ValueError("Cannot mix column and matrix keys.")
    if array_keys and len(keys) > 1:
        raise ValueError("Cannot request multiple matrix keys.")
    if not column_keys and not array_keys:
        raise ValueError("No valid keys found.")
    if column_keys:
        data = pd.concat(data, axis=1)
        data.columns = keys  # type: ignore
    elif array_keys:
        data = data[0]
    data = cast(pd.DataFrame, data)
    if array_keys and len(set(data.dtypes)) > 1:
        raise ValueError("Cannot use arrays with mixed dtypes.")
    if array_keys and data.iloc[:, 0].dtype.kind in ["b", "O", "S"]:
        long_data = data.values.ravel()
        categories = _get_categories(pd.Series(long_data), sort)
        categorical_type = pd.CategoricalDtype(categories=categories)
        data = data.apply(lambda col: col.astype(categorical_type))
    return data, array_keys


def get_keyed_obsm_data(tdata: td.TreeData, key: str) -> sp.sparse.csr_matrix | pd.DataFrame | np.ndarray:
    """Gets observation matrix data for a given key from a tree."""
    if key == "X":
        X = tdata.X
    elif key in tdata.obsm:
        X = tdata.obsm[key]
    else:
        raise ValueError(f"Key {key} not found in `tdata.obsm`.")
    return X


def get_trees(tdata: td.TreeData, tree: str | Sequence[str] | None) -> Mapping[str, nx.DiGraph]:
    """Gets tree data for a given key from a tree."""
    trees = {}
    tree_keys = tree
    if tree_keys is None:
        tree_keys = tdata.obst.keys()
    elif isinstance(tree_keys, str):
        tree_keys = [tree_keys]
    elif isinstance(tree_keys, Sequence):
        tree_keys = list(tree_keys)
    else:
        raise ValueError("Tree keys must be a string, list of strings, or None.")
    for key in tree_keys:
        if key not in tdata.obst.keys():
            raise ValueError(f"Key {key!r} is not present in obst.")
        if tdata.obst[key].number_of_nodes() != 0:
            trees[key] = tdata.obst[key]
    return trees
