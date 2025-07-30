"""Convert shapefile data to SWIFT JSON catchment structure."""

import json
from typing import Any, Dict, List, Tuple  # noqa: UP035

import geopandas as gpd


class ShapefileToSwiftConverter:
    """Converts shapefile data to SWIFT JSON catchment structure."""

    def __init__(self, gdf: gpd.GeoDataFrame, include_coordinates: bool = False):  # noqa: FBT001, FBT002
        """Initialize converter with geopandas dataframe.

        Args:
            gdf: GeoDataFrame loaded from shapefile containing link data
            include_coordinates: Whether to include lat/lon in node definitions
        """
        self.gdf = gdf
        self.include_coordinates = include_coordinates
        self._check_geodf()

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """The geodataframe from which we build the json file."""
        return self._gdf
    @gdf.setter
    def gdf(self, value: gpd.GeoDataFrame) -> None:
        self._gdf = value

    @property
    def include_coordinates(self) -> bool:
        """Should the Latitude/Longitude coordinates be derived from the geometry and written in the json file."""
        return self._include_coordinates
    @include_coordinates.setter
    def include_coordinates(self, value: bool) -> None:
        self._include_coordinates = value

    def _check_geodf(self) -> None:
        """Check the GeoDataFrame for required columns and types."""
        required_columns_names = [
            "LinkID",
            "FromNodeID",
            "ToNodeID",
            "SPathLen",
            "DArea2",
            "geometry",
        ]

        if set(required_columns_names).intersection(set(self.gdf.columns)) != set(required_columns_names):
            raise ValueError(f"The GeoDataFrame does not contain all the required columns: {required_columns_names}")

        # IDs should be strings, even if legacy are ints.
        self.gdf["LinkID"] = self.gdf["LinkID"].astype(str)
        self.gdf["FromNodeID"] = self.gdf["FromNodeID"].astype(str)
        self.gdf["ToNodeID"] = self.gdf["ToNodeID"].astype(str)

        required_columns = {
            # "LinkID": "int64",
            # "FromNodeID": "int64",
            # "ToNodeID": "int64",
            "SPathLen": "float64",
            "DArea2": "float64",
            # TODO test geometry column, but I could not figure out how.
            # "geometry": gpd.array.GeometryDtype,
        }
        for column, expected_type in required_columns.items():
            if self.gdf[column].dtype != expected_type:
                raise TypeError(f"Column '{column}' must be of type {expected_type}.")

        # Check for duplicate LinkID values
        link_id_counts = self.gdf["LinkID"].value_counts()
        duplicates = link_id_counts[link_id_counts > 1]
        if not duplicates.empty:
            duplicate_indices = self.gdf[self.gdf["LinkID"].isin(duplicates.index)].index.tolist()
            raise ValueError(f"Column 'LinkID' contains duplicate values: {duplicates.index.tolist()} at indices {duplicate_indices}.")


    def convert(self) -> Dict[str, Any]:
        """Convert shapefile data to SWIFT JSON format.

        Returns:
            Dictionary containing Links, Nodes, and SubAreas sections
        """
        return {"Links": self._create_links(), "Nodes": self._create_nodes(), "SubAreas": self._create_subareas()}

    def save_to_file(self, filepath: str, indent: int = 2) -> None:
        """Save converted data to JSON file.

        Args:
            filepath: Path where to save the JSON file
            indent: Number of spaces for JSON indentation (default: 2)
        """
        with open(filepath, "w") as f:
            json.dump(self.convert(), f, indent=indent)

    def _create_links(self) -> List[Dict[str, Any]]:
        """Create links section of JSON from dataframe."""
        links = []
        for _, row in self.gdf.iterrows():
            link = {
                "ChannelRouting": {"ChannelRoutingType": "NoRouting"},
                "DownstreamNodeID": str(row["ToNodeID"]),
                "ID": str(row["LinkID"]),
                "Length": float(row["SPathLen"]),
                "ManningsN": 1.0,
                "Name": str(row["LinkID"]),
                "Slope": 1.0,
                "UpstreamNodeID": str(row["FromNodeID"]),
                "f": 1.0,
            }
            links.append(link)
        return links

    def _get_node_coordinates(self) -> Dict[int, Tuple[float, float]]:
        """Extract node coordinates from geometry data.

        Returns:
            Dictionary mapping node_id to (longitude, latitude) tuple
        """
        node_coords = {}
        for _, row in self.gdf.iterrows():
            geom = row["geometry"]
            coords = list(geom.coords)

            # Start point for FromNodeID
            start_lon, start_lat = coords[0]
            node_coords[row["FromNodeID"]] = (start_lon, start_lat)

            # End point for ToNodeID
            end_lon, end_lat = coords[-1]
            node_coords[row["ToNodeID"]] = (end_lon, end_lat)

        return node_coords

    def _create_nodes(self) -> List[Dict[str, Any]]:
        """Create nodes section of JSON from dataframe."""
        from_nodes = set(self.gdf["FromNodeID"])
        to_nodes = set(self.gdf["ToNodeID"])
        unique_nodes = from_nodes.union(to_nodes)

        # Get coordinates if requested
        node_coords = self._get_node_coordinates() if self.include_coordinates else {}

        nodes = []
        for node_id in sorted(unique_nodes):
            node:Dict[str,Any] = {
                "ErrorCorrection": {"ErrorCorrectionType": "NoErrorCorrection"},
                "ID": str(node_id),
                "Name": f"Node_{node_id}",
                "Reservoir": {"ReservoirType": "NoReservoir"},
            }

            # Add coordinates if available
            if self.include_coordinates and node_id in node_coords:
                lon, lat = node_coords[node_id]
                node["Longitude"] = lon
                node["Latitude"] = lat

            nodes.append(node)
        return nodes

    def _create_subareas(self) -> List[Dict[str, Any]]:
        """Create subareas section of JSON from dataframe."""
        subareas = []
        for _, row in self.gdf.iterrows():
            if row["DArea2"] > 0:
                subarea = {
                    "AreaKm2": float(row["DArea2"]) / 1_000_000,
                    "ID": str(row["LinkID"]),
                    "LinkID": str(row["LinkID"]),
                    "Name": f"Subarea_{row['LinkID']}",
                    "RunoffModel": {
                        "PercFactor": 2.25,
                        "R": 0.0,
                        "RunoffModelType": "GR4J",
                        "S": 0.0,
                        "SurfaceRunoffRouting": {"SurfaceRunoffRoutingType": "NoRouting"},
                        "UHExponent": 2.5,
                        "x1": 350.0,
                        "x2": 0.0,
                        "x3": 40.0,
                        "x4": 0.5,
                    },
                }
                subareas.append(subarea)
        return subareas
