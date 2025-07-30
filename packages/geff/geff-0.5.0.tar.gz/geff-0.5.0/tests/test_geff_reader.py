import numpy as np
import pytest

from geff.geff_reader import GeffReader
from geff.networkx.io import construct_nx
from geff.testing.data import create_memory_mock_geff

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
node_axis_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_nodes(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )

    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    in_memory_geff = file_reader.build(node_mask=node_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(graph_props["nodes"][node_mask], in_memory_geff["node_ids"])

    # assert no edges that reference non existing nodes
    assert np.isin(in_memory_geff["node_ids"], in_memory_geff["edge_ids"]).all()

    # make sure graph dict can be ingested
    _ = construct_nx(**in_memory_geff)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_edges(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    file_reader = GeffReader(store)

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(edge_mask=edge_mask)

    np.testing.assert_array_equal(graph_props["edges"][edge_mask], in_memory_geff["edge_ids"])

    # make sure graph dict can be ingested
    _ = construct_nx(**in_memory_geff)


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_build_w_masked_nodes_edges(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
):
    store, graph_props = create_memory_mock_geff(
        node_id_dtype=node_id_dtype,
        node_axis_dtypes=node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
    )
    file_reader = GeffReader(store)

    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(node_mask=node_mask, edge_mask=edge_mask)

    # make sure nodes and edges are masked as expected
    np.testing.assert_array_equal(graph_props["nodes"][node_mask], in_memory_geff["node_ids"])

    # assert no edges that reference non existing nodes
    assert np.isin(in_memory_geff["node_ids"], in_memory_geff["edge_ids"]).all()

    # assert all the output edges are in the naively masked edges
    output_edges = in_memory_geff["edge_ids"]
    masked_edges = graph_props["edges"][edge_mask]
    # Adding a new axis allows comparing each element
    assert (output_edges[:, :, np.newaxis] == masked_edges).all(axis=1).any(axis=1).all()

    # make sure graph dict can be ingested
    _ = construct_nx(**in_memory_geff)


def test_read_node_props():
    store, graph_props = create_memory_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "double", "time": "double"},
        extra_edge_props={"score": "float64", "color": "uint8"},
        directed=True,
    )

    file_reader = GeffReader(store)

    # make sure the node props are also masked
    n_nodes = file_reader.nodes.shape[0]
    node_mask = np.zeros(n_nodes, dtype=bool)
    node_mask[: n_nodes // 2] = True  # mask half the nodes

    in_memory_geff = file_reader.build(node_mask=node_mask)
    assert len(in_memory_geff["node_props"]) == 0

    file_reader.read_node_props(["t"])
    in_memory_geff = file_reader.build(node_mask=node_mask)
    assert "t" in in_memory_geff["node_props"]
    np.testing.assert_allclose(
        graph_props["t"][node_mask],
        in_memory_geff["node_props"]["t"]["values"],
    )

    _ = construct_nx(**in_memory_geff)


def test_read_edge_props():
    store, graph_props = create_memory_mock_geff(
        node_id_dtype="uint8",
        node_axis_dtypes={"position": "double", "time": "double"},
        extra_edge_props={"score": "float64", "color": "uint8"},
        directed=True,
    )

    file_reader = GeffReader(store)

    # make sure props are also masked
    n_edges = file_reader.edges.shape[0]
    edge_mask = np.zeros(n_edges, dtype=bool)
    edge_mask[: n_edges // 2] = True  # mask half the edges

    in_memory_geff = file_reader.build(edge_mask=edge_mask)
    assert len(in_memory_geff["edge_props"]) == 0

    file_reader.read_edge_props(["score"])
    in_memory_geff = file_reader.build(edge_mask=edge_mask)
    np.testing.assert_allclose(
        graph_props["extra_edge_props"]["score"][edge_mask],
        in_memory_geff["edge_props"]["score"]["values"],
    )

    _ = construct_nx(**in_memory_geff)
