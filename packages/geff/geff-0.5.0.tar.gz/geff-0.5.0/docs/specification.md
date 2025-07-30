# Geff specification

The graph exchange file format is `zarr` based. A graph is stored in a zarr group, which can have any name. This allows storing multiple `geff` graphs inside the same zarr root directory. A `geff` group is identified by the presence of a `geff` key in the `.zattrs`. Other `geff` metadata is also stored in the `.zattrs` file of the `geff` group, nested under the `geff` key. The `geff` group must contain a `nodes` group and an `edges` group (albeit both can be empty). `geff` graphs have the option to provide properties for `nodes` and `edges`.

`geff` graphs have the option to provide time and spatial dimensions as special attributes. These attributes are specified in the `axes` section of the metadata, inspired by the OME-zarr `axes` specification. 

## Zarr specification

Currently, `geff` supports zarr specifications [2](https://zarr-specs.readthedocs.io/en/latest/v2/v2.0.html) and [3](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html). However, `geff` will default to writing specification 2 because graphs written to the zarr v3 spec will not be compatible with all applications. When zarr 3 is more fully adopted by other libraries and tools, we will move to a zarr spec 3 default.

## Geff metadata

<!-- GEFF-SCHEMA -->

!!! note

    The axes dictionary is modeled after the [OME-zarr](https://ngff.openmicroscopy.org/0.5/index.html#axes-md) specifications and is used to identify spatio-temporal properties on the graph nodes. If the same names are used in the axes metadata of the related image or segmentation data, applications can use this information to align graph node locations with image data. 

    ::: geff.units.VALID_AXIS_TYPES  

    ::: geff.units.VALID_SPACE_UNITS    

    ::: geff.units.VALID_TIME_UNITS  

### Affine transformations
The optional `affine` field allows specifying a global affine transformation that maps the graph coordinates stored in the node properties to a physical coordinate system. The value **matrix** is stored as a `(N + 1) × (N + 1)` homogeneous matrix following the `scipy.ndimage.affine_transform` convention, where **N** equals the number of spatio-temporal axes declared in `axes`.

### Extra attributes 

The optional `extra` object is a free-form dictionary that can hold any additional, application-specific metadata that is **not** covered by the core geff schema. Users may place arbitrary keys and values inside `extra` without fear of clashing with future reserved fields. Although the core `geff` reader makes these attributes available, their meaning and use are left entirely to downstream applications. 

## The `nodes` group
The nodes group will contain an `ids` array and optionally a `props` group. 
### The `ids` array
The `nodes\ids` array is a 1D array of node IDs of length `N` >= 0, where `N` is the number of nodes in the graph. Node ids must be unique. Node IDs can have any type supported by zarr (except floats), but we recommend integer dtypes. For large graphs, `uint64` might be necessary to provide enough range for every node to have a unique ID. In the minimal case of an empty graph, the `ids` array will be present but empty. 


### The `props` group and `node property` groups
The `nodes\props` group is optional and will contain one or more `node property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the node `ids` array, such that each row of the property `values` array stores the property for the node at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all nodes. A `1` at an index in the `missing` array indicates that the `value` of that property for the node at that index is None, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all nodes have values for the property.

-  Geff provides special support for spatio-temporal properties, although they are not required. When `axes` are specified in the `geff` metadata, each axis name identifies a spatio-temporal property. Spatio-temporal properties are not allowed to have missing arrays. Otherwise, they are identical to other properties from a storage specification perspective.

- The `seg_id` property is an optional, special node property that stores the segmenatation label for each node. The `seg_id` values do not need to be unique, in case labels are repeated between time points. If the `seg_id` property is not present, it is assumed that the graph is not associated with a segmentation. 

-  Geff provides special support for predefined shape properties, although they are not required. These currently include: `sphere`, `ellipsoid`. Values can be marked as `missing`, and a geff graph may contain multiple different shape properties. Units of shapes are assumed to be the same as the units on the spatial axes. Otherwise, shape properties are identical to other properties from a storage specification perspective.
    - `sphere`: Hypersphere in n spatial dimensions, defined by a scalar radius.
    - `ellipsoid`: Defined by a symmetric positive-definite covariance matrix, whose dimensionality is assumed to match the spatial axes.
<!-- Perhaps we just let the user specify the seg id property in the metadata instead? Then you can point it to the node ids if you wanted to -->

!!! note

    When writing a graph with missing properties to the geff format, you must fill in a dummy value in the `values` array for the nodes that are missing the property, in order to keep the indices aligned with the node ids. 

## The `edges` group
Similar to the `nodes` group, the `edges` group will contain an `ids` array and an optional `props` group.

### The `ids` array
The `edges\ids` array is a 2D array with the same dtype as the `nodes\ids` array. It has shape `(E, 2)`, where `E` is the number of edges in the graph. If there are no edges in the graph, the edge group and `ids` array must be present with shape `(0, 2)`.  All elements in the `edges\ids` array must also be present in the `nodes\ids` array, and the data types of the two id arrays must match.
Each row represents an edge between two nodes. For directed graphs, the first column is the source nodes and the second column holds the target nodes. For undirected graphs, the order is arbitrary.
Edges should be unique (no multiple edges between the same two nodes) and edges from a node to itself are not supported.

### The `props` group and `edge property` groups
The `edges\props` group will contain zero or more `edge property` groups, each with a `values` array and an optional `missing` array.

- `values` arrays can be any zarr supported dtype, and can be N-dimensional. The first dimension of the `values` array must have the same length as the `edges\ids` array, such that each row of the property `values` array stores the property for the edge at that index in the ids array.
- The `missing` array is an optional, a one dimensional boolean array to support properties that are not present on all edges. A `1` at an index in the `missing` array indicates that the `value` of that property for the edge at that index is missing, and the value in the `values` array at that index should be ignored. If the `missing` array is not present, that means that all edges have values for the property.

The `edges/props` is optional. If you do not have any edge properties, the `edges\props` can be absent. 

## Example file structure and metadata
Here is a schematic of the expected file structure.
``` python
/path/to.zarr
    /tracking_graph
	    .zattrs  # graph metadata with `geff_version`
	    nodes/
            ids  # shape: (N,)  dtype: uint64
            props/
                t/
                    values # shape: (N,) dtype: uint16
                z/
                    values # shape: (N,) dtype: float32
                y/
                    values # shape: (N,) dtype: float32
                x/
                    values # shape: (N,) dtype: float32
                radius/
                    values # shape: (N,) dtype: int | float
                    missing # shape: (N,) dtype: bool
                covariance3d/
                    values # shape: (N, 3, 3) dtype: float
                    missing # shape: (N,) dtype: bool
                color/
                    values # shape: (N, 4) dtype: float16
                    missing # shape: (N,) dtype: bool
	    edges/
            ids  # shape: (E, 2) dtype: uint64
            props/
                distance/
                    values # shape: (E,) dtype: float16
                score/
                    values # shape: (E,) dtype: float16
                    missing # shape: (E,) dtype: bool
    # optional:
    /segmentation 
    
    # unspecified, but totally okay:
    /raw 
```
This is a geff metadata zattrs file that matches the above example structure.
```json
# /path/to.zarr/tracking_graph/.zattrs
{   
    "geff": {
        "directed": true,
        "geff_version": "0.1.3.dev4+gd5d1132.d20250616",
        "axes": [ # optional
            {'name': 't', 'type': "time", 'unit': "seconds", 'min': 0, 'max': 125},
            {'name': 'z', 'type': "space", 'unit': "micrometers", 'min': 1523.36, 'max': 4398.1},
            {'name': 'y', 'type': "space", 'unit': "micrometers", 'min': 81.667, 'max': 1877.7},
            {'name': 'x', 'type': "space", 'unit': "micrometers", 'min': 764.42, 'max': 2152.3},
        ],
        # predefined node attributes for storing detections as spheres or ellipsoids
        "sphere": "radius", # optional
        "ellipsoid": "covariance3d", # optional
        "display_hints": {
            "display_horizontal": "x",
            "display_vertical": "y",
            "display_depth": "z",
            "display_time": "t",
        },
        # node attributes corresponding to tracklet and/or lineage IDs
        "track_node_props": {
            "lineage": "ultrack_lineage_id",
            "tracklet": "ultrack_id"
        },
        "related_objects": {
            {
                "type":"labels", "path":"../segmentation/", "label_prop": "seg_id",
            },
            {
                "type":"image", "path":"../raw/",
            },
        },
        # optional coordinate transformation is defined as homogeneous coordinates
        # It is expected to be a (D+1)x(D+1) matrix where D is the number of axes
        "affine": [
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
        # custom other things must be placed **inside** the extra attribute
        "extra": {
            ...
        }
    }
}
```
