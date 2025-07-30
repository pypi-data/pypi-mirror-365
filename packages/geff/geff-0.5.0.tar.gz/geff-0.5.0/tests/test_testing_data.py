import numpy as np
import pytest

import geff
from geff.testing.data import (
    create_dummy_graph_props,
    create_memory_mock_geff,
    create_simple_2d_geff,
    create_simple_3d_geff,
    create_simple_temporal_geff,
)


def test_create_simple_2d_geff():
    """Test the create_simple_2d_geff convenience function"""

    # Test with defaults
    store, _ = create_simple_2d_geff()

    # Verify it creates a valid geff store
    graph, metadata = geff.read_nx(store)

    # Check basic properties
    assert len(graph.nodes) == 10  # default num_nodes
    assert len(graph.edges) == 15  # default num_edges
    assert not graph.is_directed()  # default directed=False

    # Check spatial dimensions (2D should have x, y, t but not z)
    for node in graph.nodes:
        node_data = graph.nodes[node]
        assert "x" in node_data
        assert "y" in node_data
        assert "t" in node_data
        assert "z" not in node_data  # 2D doesn't include z

    # Check metadata
    assert not metadata.directed
    axis_names = [axis.name for axis in metadata.axes]
    assert "x" in axis_names
    assert "y" in axis_names
    assert "t" in axis_names
    assert "z" not in axis_names


def test_create_simple_3d_geff():
    """Test the create_simple_3d_geff convenience function"""

    # Test with defaults
    store, _ = create_simple_3d_geff()

    # Verify it creates a valid geff store
    graph, metadata = geff.read_nx(store)

    # Check basic properties
    assert len(graph.nodes) == 10  # default num_nodes
    assert len(graph.edges) == 15  # default num_edges
    assert not graph.is_directed()  # default directed=False

    # Check spatial dimensions (3D should have x, y, z, t)
    for node in graph.nodes:
        node_data = graph.nodes[node]
        assert "x" in node_data
        assert "y" in node_data
        assert "z" in node_data  # 3D includes z
        assert "t" in node_data

    # Check metadata
    assert not metadata.directed
    axis_names = [axis.name for axis in metadata.axes]
    assert "x" in axis_names
    assert "y" in axis_names
    assert "z" in axis_names  # 3D includes z
    assert "t" in axis_names


def test_create_simple_temporal_geff():
    """Test the create_simple_temporal_geff convenience function"""

    # Test with defaults
    store, _ = create_simple_temporal_geff()

    # Verify it creates a valid geff store
    graph, metadata = geff.read_nx(store)

    # Check basic properties
    assert len(graph.nodes) == 10  # default num_nodes
    assert len(graph.edges) == 15  # default num_edges
    assert not graph.is_directed()  # default directed=False

    # Check temporal dimensions (should have only t, no spatial dimensions)
    for node in graph.nodes:
        node_data = graph.nodes[node]
        assert "t" in node_data
        assert "x" not in node_data  # No spatial dimensions
        assert "y" not in node_data  # No spatial dimensions
        assert "z" not in node_data  # No spatial dimensions

    # Check metadata
    assert not metadata.directed
    axis_names = [axis.name for axis in metadata.axes]
    assert "t" in axis_names
    assert "x" not in axis_names  # No spatial dimensions
    assert "y" not in axis_names  # No spatial dimensions
    assert "z" not in axis_names  # No spatial dimensions


def test_simple_geff_edge_properties():
    """Test that the simple functions create graphs with proper edge properties"""

    # Test 2D
    store_2d, _ = create_simple_2d_geff()
    graph_2d, _ = geff.read_nx(store_2d)

    # Check that edges have the expected properties
    for edge in graph_2d.edges:
        edge_data = graph_2d.edges[edge]
        assert "score" in edge_data
        assert "color" in edge_data
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)

    # Test 3D
    store_3d, _ = create_simple_3d_geff()
    graph_3d, _ = geff.read_nx(store_3d)

    # Check that edges have the expected properties
    for edge in graph_3d.edges:
        edge_data = graph_3d.edges[edge]
        assert "score" in edge_data
        assert "color" in edge_data
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)

    # Test temporal
    store_temporal, _ = create_simple_temporal_geff()
    graph_temporal, _ = geff.read_nx(store_temporal)

    # Check that edges have the expected properties
    for edge in graph_temporal.edges:
        edge_data = graph_temporal.edges[edge]
        assert "score" in edge_data
        assert "color" in edge_data
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)


def test_create_memory_mock_geff_with_extra_node_props():
    """Test create_memory_mock_geff with extra node properties"""

    # Test with mixed auto-generated and custom arrays for node properties
    custom_node_labels = np.array(["A", "B", "C", "D", "E"])
    custom_node_scores = np.array([0.1, 0.5, 0.8, 0.3, 0.9])

    extra_node_props = {
        "label": custom_node_labels,  # Custom array
        "confidence": "float64",  # Auto-generate
        "category": "int8",  # Auto-generate
        "priority": "uint16",  # Auto-generate
        "status": "str",  # Auto-generate
        "weight": "float32",  # Auto-generate
        "score": custom_node_scores,  # Custom array
    }

    # Test with mixed auto-generated and custom arrays for edge properties
    custom_edge_weights = np.array([0.1, 0.2, 0.3, 0.4])
    custom_edge_types = np.array(["type_A", "type_B", "type_C", "type_D"])

    extra_edge_props = {
        "weight": custom_edge_weights,  # Custom array
        "score": "float64",  # Auto-generate
        "color": "int",  # Auto-generate
        "type": custom_edge_types,  # Custom array
    }

    store, _ = create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=False,
        num_nodes=5,
        num_edges=4,
        extra_node_props=extra_node_props,
        extra_edge_props=extra_edge_props,
    )

    # Verify the graph was created correctly
    graph, _ = geff.read_nx(store)

    # Check that extra node properties are present
    for node in graph.nodes:
        node_data = graph.nodes[node]
        # Check that all extra properties are present
        assert "label" in node_data
        assert "confidence" in node_data
        assert "category" in node_data
        assert "priority" in node_data
        assert "status" in node_data
        assert "weight" in node_data
        assert "score" in node_data

        # Check data types
        assert isinstance(node_data["label"], str)
        assert isinstance(node_data["confidence"], float | np.floating)
        assert isinstance(node_data["category"], int | np.integer)
        assert isinstance(node_data["priority"], int | np.integer)
        assert isinstance(node_data["status"], str)
        assert isinstance(node_data["weight"], float | np.floating)
        assert isinstance(node_data["score"], float | np.floating)

    # Check that auto-generated properties match the expected patterns
    for i, node in enumerate(sorted(graph.nodes)):
        node_data = graph.nodes[node]
        assert node_data["status"] == f"status_{i}"
        assert node_data["category"] == i
        assert node_data["priority"] == i

    # Check that custom node properties match the provided arrays
    for i, node in enumerate(sorted(graph.nodes)):
        node_data = graph.nodes[node]
        assert node_data["label"] == custom_node_labels[i]
        assert node_data["score"] == custom_node_scores[i]

    # Check that extra edge properties are present
    for edge in graph.edges:
        edge_data = graph.edges[edge]
        assert "weight" in edge_data
        assert "score" in edge_data
        assert "color" in edge_data
        assert "type" in edge_data

        # Check data types
        assert isinstance(edge_data["weight"], float | np.floating)
        assert isinstance(edge_data["score"], float | np.floating)
        assert isinstance(edge_data["color"], int | np.integer)
        assert isinstance(edge_data["type"], str)

    # Check that auto-generated edge properties match the expected patterns
    for i, edge in enumerate(sorted(graph.edges)):
        edge_data = graph.edges[edge]
        assert edge_data["score"] == pytest.approx(0.1 + i * 0.9 / 3)  # linspace(0.1, 1.0, 4)
        assert edge_data["color"] == i

    # Check that custom edge properties match the provided arrays
    for i, edge in enumerate(sorted(graph.edges)):
        edge_data = graph.edges[edge]
        assert edge_data["weight"] == custom_edge_weights[i]
        assert edge_data["type"] == custom_edge_types[i]


def test_create_memory_mock_geff_with_no_extra_node_props():
    """Test create_memory_mock_geff with no extra node properties"""

    store, graph_props = create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        extra_edge_props={"score": "float64", "color": "int"},
        directed=False,
        num_nodes=5,
        num_edges=4,
        extra_node_props=None,  # Explicitly None
    )

    # Verify the graph was created correctly
    graph, metadata = geff.read_nx(store)

    # Check that no extra node properties are present
    for node in graph.nodes:
        node_data = graph.nodes[node]
        # Should only have spatial properties, not extra ones
        extra_props = {"label", "confidence", "category", "priority", "status", "weight"}

        for prop in extra_props:
            assert prop not in node_data


def test_create_memory_mock_geff_extra_node_props_validation():
    """Test validation of extra_node_props parameter"""

    # Test with invalid input types
    with pytest.raises(ValueError, match="extra_node_props must be a dict"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props="not_a_dict",  # Should be a dict
        )

    with pytest.raises(ValueError, match="extra_node_props keys must be strings"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props={123: "str"},  # Key should be string
        )

    with pytest.raises(ValueError, match="extra_node_props\\[label\\] must be a string dtype"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props={"label": 123},  # Value should be string dtype
        )

    with pytest.raises(ValueError, match="dtype 'invalid_dtype' not supported"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props={"label": "invalid_dtype"},  # Invalid dtype
        )

    # Test array length validation for node properties
    custom_node_labels = np.array(["A", "B", "C"])  # Only 3 elements, but 5 nodes

    with pytest.raises(
        ValueError,
        match="extra_node_props\\[label\\] array length 3 does not match num_nodes 5",
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            num_nodes=5,
            num_edges=4,
            extra_node_props={"label": custom_node_labels},
        )

    # Test array length validation for edge properties
    custom_edge_weights = np.array([0.1, 0.2])  # Only 2 elements, but 4 edges

    with pytest.raises(
        ValueError,
        match="extra_edge_props\\[weight\\] array length 2 does not match number of edges 4",
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            num_nodes=5,
            num_edges=4,
            extra_edge_props={"weight": custom_edge_weights},
        )

    # Test mixed case - one correct, one wrong
    custom_node_labels = np.array(["A", "B", "C", "D", "E"])  # Correct length
    custom_node_scores = np.array([0.1, 0.2])  # Wrong length

    with pytest.raises(
        ValueError, match="extra_node_props\\[score\\] array length 2 does not match num_nodes 5"
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            num_nodes=5,
            num_edges=4,
            extra_node_props={"label": custom_node_labels, "score": custom_node_scores},
        )

    # Test invalid type for node properties (non-string, non-array)
    with pytest.raises(
        ValueError, match="extra_node_props\\[label\\] must be a string dtype or numpy array"
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            extra_edge_props={"score": "float64", "color": "int"},
            directed=False,
            extra_node_props={"label": 123},  # Invalid type
        )

    # Test invalid type for edge properties (non-string, non-array)
    with pytest.raises(
        ValueError, match="extra_edge_props\\[weight\\] must be a string dtype or numpy array"
    ):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            extra_edge_props={"weight": [1, 2, 3, 4]},  # Invalid type
        )

    # Test extra_edge_props is not a dict
    with pytest.raises(ValueError, match="extra_edge_props must be a dict"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            extra_edge_props="not_a_dict",  # Should be a dict
        )

    # Test extra_edge_props property name is not a string
    with pytest.raises(ValueError, match="extra_edge_props keys must be strings"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            extra_edge_props={123: "str"},  # Key should be string
        )

    # Test extra_edge_props property dtype is not a valid dtype
    with pytest.raises(ValueError, match="dtype 'invalid_dtype' not supported"):
        create_memory_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=False,
            extra_edge_props={"weight": "invalid_dtype"},  # Invalid dtype
        )


def test_create_memory_mock_geff_extra_node_props_different_dtypes():
    """Test extra node properties with different data types"""

    # Test all supported dtypes
    extra_node_props = {
        "str_prop": "str",
        "int_prop": "int",
        "int8_prop": "int8",
        "uint8_prop": "uint8",
        "int16_prop": "int16",
        "uint16_prop": "uint16",
        "float32_prop": "float32",
        "float64_prop": "float64",
    }

    store, graph_props = create_memory_mock_geff(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        extra_edge_props={"score": "float64", "color": "int", "type": "str"},
        directed=False,
        num_nodes=3,
        num_edges=2,
        extra_node_props=extra_node_props,
    )

    # Verify the graph was created correctly
    graph, metadata = geff.read_nx(store)

    # Check that all properties are present with correct types
    for node in graph.nodes:
        node_data = graph.nodes[node]

        # String properties
        assert "str_prop" in node_data
        assert isinstance(node_data["str_prop"], str)

        # Integer properties
        for prop_name in ["int_prop", "int8_prop", "uint8_prop", "int16_prop", "uint16_prop"]:
            assert prop_name in node_data
            assert isinstance(node_data[prop_name], int | np.integer)

        # Float properties
        for prop_name in ["float32_prop", "float64_prop"]:
            assert prop_name in node_data
            assert isinstance(node_data[prop_name], float | np.floating)


def test_create_dummy_graph_props_extra_node_props():
    """Test create_dummy_graph_props with extra node properties"""

    extra_node_props = {
        "label": "str",
        "confidence": "float64",
        "category": "int8",
    }

    graph_props = create_dummy_graph_props(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        extra_edge_props={"score": "float64", "color": "int"},
        directed=True,
        num_nodes=10,
        num_edges=500,
        extra_node_props=extra_node_props,
    )

    # Check that extra_node_props_dict contains the expected properties
    extra_props = graph_props["extra_node_props"]
    assert "label" in extra_props
    assert "confidence" in extra_props
    assert "category" in extra_props

    # Check data types and values
    assert extra_props["label"].dtype.kind == "U"  # Unicode string
    assert extra_props["confidence"].dtype == "float64"
    assert extra_props["category"].dtype == "int8"

    # Check that arrays have the correct length
    assert len(extra_props["label"]) == 10
    assert len(extra_props["confidence"]) == 10
    assert len(extra_props["category"]) == 10

    # Check that string properties follow the expected pattern
    for i in range(5):
        assert extra_props["label"][i] == f"label_{i}"
        assert extra_props["category"][i] == i


def test_create_dummy_graph_props_empty_graph():
    """Test create_dummy_graph_props with empty graph (0 nodes, 0 edges)"""

    extra_node_props = {
        "label": "str",
        "confidence": "float64",
        "category": "int8",
    }

    graph_props = create_dummy_graph_props(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        extra_edge_props={"score": "float64", "color": "int"},
        directed=True,
        num_nodes=0,
        num_edges=0,
        extra_node_props=extra_node_props,
    )

    # Check every field of graph_props for empty graph
    # 1. Check nodes array
    assert len(graph_props["nodes"]) == 0
    assert graph_props["nodes"].dtype == "int"

    # 2. Check edges array
    assert len(graph_props["edges"]) == 0
    assert graph_props["edges"].dtype == "int"

    # 3. Check spatial and temporal coordinates
    assert len(graph_props["t"]) == 0
    assert len(graph_props["z"]) == 0
    assert len(graph_props["y"]) == 0
    assert len(graph_props["x"]) == 0

    # 4. Check extra node properties
    extra_props = graph_props["extra_node_props"]
    assert "label" in extra_props
    assert "confidence" in extra_props
    assert "category" in extra_props

    # Check data types
    assert extra_props["label"].dtype.kind == "U"  # Unicode string
    assert extra_props["confidence"].dtype == "float64"
    assert extra_props["category"].dtype == "int8"

    # Check that arrays have the correct length (0 for empty graph)
    assert len(extra_props["label"]) == 0
    assert len(extra_props["confidence"]) == 0
    assert len(extra_props["category"]) == 0

    # 5. Check extra edge properties
    edge_props = graph_props["extra_edge_props"]
    assert "score" in edge_props
    assert "color" in edge_props

    # Check data types
    assert edge_props["score"].dtype == "float64"
    assert edge_props["color"].dtype == "int"

    # Check that arrays have the correct length (0 for empty graph)
    assert len(edge_props["score"]) == 0
    assert len(edge_props["color"]) == 0

    # 6. Check graph metadata
    assert graph_props["directed"] is True

    # 7. Check axis information
    assert len(graph_props["axis_names"]) == 4  # t, z, y, x
    assert graph_props["axis_names"] == ("t", "z", "y", "x")

    assert len(graph_props["axis_units"]) == 4
    assert graph_props["axis_units"] == ("second", "nanometer", "nanometer", "nanometer")

    assert len(graph_props["axis_types"]) == 4
    assert graph_props["axis_types"] == ("time", "space", "space", "space")


def test_create_dummy_graph_props_empty_graph_no_extra_props():
    """Test create_dummy_graph_props with empty graph and no extra properties"""

    graph_props = create_dummy_graph_props(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=False,
        num_nodes=0,
        num_edges=0,
        extra_node_props=None,
        extra_edge_props=None,
    )

    # Check every field of graph_props for empty graph
    # 1. Check nodes array
    assert len(graph_props["nodes"]) == 0
    assert graph_props["nodes"].dtype == "int"

    # 2. Check edges array
    assert len(graph_props["edges"]) == 0
    assert graph_props["edges"].dtype == "int"

    # 3. Check spatial and temporal coordinates
    assert len(graph_props["t"]) == 0
    assert len(graph_props["z"]) == 0
    assert len(graph_props["y"]) == 0
    assert len(graph_props["x"]) == 0

    # 4. Check extra node properties (should be empty dict)
    assert graph_props["extra_node_props"] == {}

    # 5. Check extra edge properties (should be empty dict)
    assert graph_props["extra_edge_props"] == {}

    # 6. Check graph metadata
    assert graph_props["directed"] is False

    # 7. Check axis information
    assert len(graph_props["axis_names"]) == 4  # t, z, y, x
    assert graph_props["axis_names"] == ("t", "z", "y", "x")

    assert len(graph_props["axis_units"]) == 4
    assert graph_props["axis_units"] == ("second", "nanometer", "nanometer", "nanometer")

    assert len(graph_props["axis_types"]) == 4
    assert graph_props["axis_types"] == ("time", "space", "space", "space")


def test_create_dummy_graph_props_empty_graph_partial_dimensions():
    """Test create_dummy_graph_props with empty graph and partial dimensions"""

    graph_props = create_dummy_graph_props(
        node_id_dtype="int",
        node_axis_dtypes={"position": "float64", "time": "float64"},
        directed=True,
        num_nodes=0,
        num_edges=0,
        extra_node_props=None,
        extra_edge_props=None,
        include_t=True,
        include_z=False,  # No z dimension
        include_y=True,
        include_x=False,  # No x dimension
    )

    # Check every field of graph_props for empty graph
    # 1. Check nodes array
    assert len(graph_props["nodes"]) == 0
    assert graph_props["nodes"].dtype == "int"

    # 2. Check edges array
    assert len(graph_props["edges"]) == 0
    assert graph_props["edges"].dtype == "int"

    # 3. Check spatial and temporal coordinates
    assert len(graph_props["t"]) == 0
    assert len(graph_props["z"]) == 0  # Should be empty since include_z=False
    assert len(graph_props["y"]) == 0
    assert len(graph_props["x"]) == 0  # Should be empty since include_x=False

    # 4. Check extra node properties (should be empty dict)
    assert graph_props["extra_node_props"] == {}

    # 5. Check extra edge properties (should be empty dict)
    assert graph_props["extra_edge_props"] == {}

    # 6. Check graph metadata
    assert graph_props["directed"] is True

    # 7. Check axis information (only t and y dimensions)
    assert len(graph_props["axis_names"]) == 2  # t, y only
    assert graph_props["axis_names"] == ("t", "y")

    assert len(graph_props["axis_units"]) == 2
    assert graph_props["axis_units"] == ("second", "nanometer")

    assert len(graph_props["axis_types"]) == 2
    assert graph_props["axis_types"] == ("time", "space")
