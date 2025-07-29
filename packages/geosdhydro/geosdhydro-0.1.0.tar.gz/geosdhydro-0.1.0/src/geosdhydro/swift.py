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
            node = {
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
