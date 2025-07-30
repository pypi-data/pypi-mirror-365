import numpy as np
import pytest
import zarr

import geff
from geff.metadata_schema import GeffMetadata, axes_from_lists
from geff.testing.data import create_memory_mock_geff

rx = pytest.importorskip("rustworkx")

node_id_dtypes = ["int8", "uint8", "int16", "uint16"]
node_axis_dtypes = [
    {"position": "double", "time": "double"},
    {"position": "int", "time": "int"},
]
extra_edge_props = [
    {"score": "float64", "color": "uint8"},
    {"score": "float32", "color": "int16"},
]


def create_rustworkx_graph(directed=False, include_t=True, include_z=False):
    """Create a simple rustworkx graph for testing."""
    graph = rx.PyDiGraph() if directed else rx.PyGraph()

    # Add nodes with properties
    node_data = []
    if include_t and include_z:
        node_data = [
            {"t": 0, "y": 1, "x": 2, "z": 0},
            {"t": 1, "y": 3, "x": 4, "z": 1},
            {"t": 2, "y": 5, "x": 6, "z": 2},
        ]
    elif include_t:
        node_data = [
            {"t": 0, "y": 1, "x": 2},
            {"t": 1, "y": 3, "x": 4},
            {"t": 2, "y": 5, "x": 6},
        ]
    elif include_z:
        node_data = [
            {"y": 1, "x": 2, "z": 0},
            {"y": 3, "x": 4, "z": 1},
            {"y": 5, "x": 6, "z": 2},
        ]
    else:
        node_data = [
            {"y": 1, "x": 2},
            {"y": 3, "x": 4},
            {"y": 5, "x": 6},
        ]

    node_indices = graph.add_nodes_from(node_data)

    # Add edges with properties
    edges = [
        (node_indices[0], node_indices[1], {"score": 0.5, "color": 1}),
        (node_indices[1], node_indices[2], {"score": 0.7, "color": 2}),
    ]
    graph.add_edges_from(edges)

    return graph, node_indices


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read_write_consistency(
    node_id_dtype,
    node_axis_dtypes,
    extra_edge_props,
    directed,
    include_t,
    include_z,
):
    """Test rustworkx read/write consistency using create_memory_mock_geff like networkx tests."""
    store, graph_props = create_memory_mock_geff(
        node_id_dtype,
        node_axis_dtypes,
        extra_edge_props=extra_edge_props,
        directed=directed,
        include_t=include_t,
        include_z=include_z,
    )

    # Read with rustworkx backend
    graph, _ = geff.read_rx(store)

    # Verify basic structure matches the mock data
    assert graph.num_nodes() == len(graph_props["nodes"])
    assert graph.num_edges() == len(graph_props["edges"])
    assert isinstance(graph, rx.PyDiGraph) == directed

    # Test that nodes and edges have proper structure
    # Note: exact node/edge ID mapping is complex in rustworkx, so we test structure
    node_count = 0
    for rx_idx in graph.node_indices():
        node_data = graph[rx_idx]
        assert isinstance(node_data, dict)
        node_count += 1
    assert node_count == len(graph_props["nodes"])

    edge_count = 0
    for edge_idx in graph.edge_indices():
        edge_data = graph.get_edge_data_by_index(edge_idx)
        assert isinstance(edge_data, dict)
        edge_count += 1
    assert edge_count == len(graph_props["edges"])


@pytest.mark.parametrize("node_id_dtype", node_id_dtypes)
@pytest.mark.parametrize("node_axis_dtypes", node_axis_dtypes)
@pytest.mark.parametrize("extra_edge_props", extra_edge_props)
@pytest.mark.parametrize("directed", [True, False])
def test_read_write_no_spatial_rx(
    tmp_path, node_id_dtype, node_axis_dtypes, extra_edge_props, directed
):
    """Test rustworkx graphs with no spatial properties."""
    graph = rx.PyDiGraph() if directed else rx.PyGraph()

    nodes = np.array([10, 2, 127, 4, 5], dtype=node_id_dtype)
    props = np.array([4, 9, 10, 2, 8], dtype=node_axis_dtypes["position"])

    # Create node data with properties
    node_data = [{"attr": pos} for pos in props.tolist()]

    rx_node_ids = graph.add_nodes_from(node_data)
    node_id_dict = {
        rx_idx: node_id.item() for rx_idx, node_id in zip(rx_node_ids, nodes, strict=False)
    }

    # Add edges with properties
    edges = np.array(
        [
            [rx_node_ids[0], rx_node_ids[1]],
            [rx_node_ids[1], rx_node_ids[2]],
            [rx_node_ids[1], rx_node_ids[3]],
            [rx_node_ids[3], rx_node_ids[4]],
        ]
    )
    scores = np.array([0.1, 0.2, 0.3, 0.4], dtype=extra_edge_props["score"])
    colors = np.array([1, 2, 3, 4], dtype=extra_edge_props["color"])

    edges_with_data = []
    for edge, score, color in zip(edges, scores, colors, strict=False):
        edges_with_data.append((edge[0], edge[1], {"score": score.item(), "color": color.item()}))

    graph.add_edges_from(edges_with_data)

    path = tmp_path / "rw_consistency.zarr/graph"

    geff.write_rx(graph, path, node_id_dict=node_id_dict, axis_names=[])

    compare, _ = geff.read_rx(path)

    assert compare.num_nodes() == graph.num_nodes()
    assert compare.num_edges() == graph.num_edges()
    assert isinstance(compare, rx.PyDiGraph) == isinstance(graph, rx.PyDiGraph)


@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("include_t", [True, False])
@pytest.mark.parametrize("include_z", [True, False])
def test_read_write_consistency_rx(tmp_path, directed, include_t, include_z):
    """Test that rustworkx graphs can be written and read back consistently."""

    graph, node_indices = create_rustworkx_graph(directed, include_t, include_z)

    # Define axis names based on what's included
    axis_names = ["y", "x"]
    if include_t:
        axis_names = ["t", *axis_names]
    if include_z:
        axis_names = [*axis_names, "z"]

    path = tmp_path / "rw_consistency.zarr"

    # Create node_id_dict to map rx indices to arbitrary ids
    node_id_dict = {idx: idx + 10 for idx in node_indices}

    # Write the graph
    geff.write_rx(graph, path, node_id_dict=node_id_dict, axis_names=axis_names)

    # Read it back
    read_graph, metadata = geff.read_rx(path)

    assert rx.is_isomorphic(graph, read_graph)

    # Check basic structure
    assert read_graph.num_nodes() == graph.num_nodes()
    assert read_graph.num_edges() == graph.num_edges()
    assert isinstance(read_graph, rx.PyDiGraph) == isinstance(graph, rx.PyDiGraph)

    # Check metadata
    assert metadata.directed == directed
    assert len(metadata.axes) == len(axis_names)


def test_write_empty_graph_rx(tmp_path):
    """Test writing an empty rustworkx graph."""
    graph = rx.PyDiGraph()
    path = tmp_path / "empty.zarr"

    with pytest.warns(UserWarning, match="Graph is empty - only writing metadata"):
        geff.write_rx(graph, path, axis_names=["t", "y", "x"])

    # Should be able to read it back
    read_graph, metadata = geff.read_rx(path)
    assert read_graph.num_nodes() == 0
    assert read_graph.num_edges() == 0


def test_write_rx_with_metadata(tmp_path):
    """Test write_rx with explicit metadata parameter."""

    graph, node_indices = create_rustworkx_graph(directed=False, include_t=False, include_z=False)

    # Create metadata object
    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
        roi_min=(1.0, 2.0),
        roi_max=(3.0, 4.0),
    )
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "metadata_test.zarr"
    with pytest.warns(UserWarning, match="Both axis lists and metadata provided"):
        geff.write_rx(graph, path, metadata=metadata, axis_names=["x", "y"])

    # Read it back and verify metadata is preserved
    _, read_metadata = geff.read_rx(path)

    assert not read_metadata.directed
    assert len(read_metadata.axes) == 2
    assert read_metadata.axes[0].name == "x"
    assert read_metadata.axes[1].name == "y"
    assert read_metadata.axes[0].unit == "micrometer"
    assert read_metadata.axes[1].unit == "micrometer"


def test_write_rx_metadata_extra_properties(tmp_path):
    """Test writing rustworkx graph with extra metadata properties."""

    graph, node_indices = create_rustworkx_graph(directed=False, include_t=False, include_z=False)

    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(
        geff_version="0.3.0",
        directed=False,
        axes=axes,
        extra={"foo": "bar", "bar": {"baz": "qux"}},
    )
    path = tmp_path / "extra_properties_test.zarr"

    with pytest.warns(UserWarning, match="Both axis lists and metadata provided"):
        geff.write_rx(graph, path, metadata=metadata, axis_names=["x", "y"])
    _, read_metadata = geff.read_rx(path)
    assert read_metadata.extra["foo"] == "bar"
    assert read_metadata.extra["bar"]["baz"] == "qux"


def test_write_rx_metadata_override_precedence(tmp_path):
    """Test that explicit axis parameters override metadata for rustworkx."""

    graph, node_indices = create_rustworkx_graph(directed=False, include_t=True, include_z=True)

    # Create metadata with one set of axes
    axes = axes_from_lists(
        axis_names=["x", "y"],
        axis_units=["micrometer", "micrometer"],
        axis_types=["space", "space"],
    )
    metadata = GeffMetadata(geff_version="0.3.0", directed=False, axes=axes)

    path = tmp_path / "override_test.zarr"

    # Should log warning when both metadata and axis lists are provided
    with pytest.warns(UserWarning):
        geff.write_rx(
            graph,
            store=path,
            metadata=metadata,
            axis_names=["t", "y", "x", "z"],  # Override with different axes
            axis_units=["second", "meter", "meter", "meter"],
            axis_types=["time", "space", "space", "space"],
        )

    # Verify that axis lists took precedence
    _, read_metadata = geff.read_rx(path)
    assert len(read_metadata.axes) == 4
    axis_names = [axis.name for axis in read_metadata.axes]
    axis_units = [axis.unit for axis in read_metadata.axes]
    axis_types = [axis.type for axis in read_metadata.axes]
    assert axis_names == ["t", "y", "x", "z"]
    assert axis_units == ["second", "meter", "meter", "meter"]
    assert axis_types == ["time", "space", "space", "space"]


def test_write_rx_different_store_types(tmp_path):
    """Test write_rx with different store types: path, string, and zarr.store."""

    # Create a simple test graph
    graph, node_indices = create_rustworkx_graph(directed=False, include_t=False, include_z=False)

    # Test 1: Path object
    path_store = tmp_path / "test_path.zarr"
    geff.write_rx(graph, path_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_rx(path_store)
    assert graph_read.num_nodes() == 3
    assert graph_read.num_edges() == 2

    # Test 2: String path
    string_store = str(tmp_path / "test_string.zarr")
    geff.write_rx(graph, string_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_rx(string_store)
    assert graph_read.num_nodes() == 3
    assert graph_read.num_edges() == 2

    # Test 3: Zarr MemoryStore
    memory_store = zarr.storage.MemoryStore()
    geff.write_rx(graph, memory_store, axis_names=["x", "y"])

    # Verify it was written correctly
    graph_read, _ = geff.read_rx(memory_store)
    assert graph_read.num_nodes() == 3
    assert graph_read.num_edges() == 2
