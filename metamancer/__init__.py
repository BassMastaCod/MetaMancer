import math
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Optional, Any, Iterable, Union

import folium
import networkx
from cachetools import TTLCache

from apparatus import extract_date
from scholia import Scholia


Coordinate = tuple[float, float]
MediaCoordinates = dict[Path, Coordinate]


class SpatialStrata:
    def __init__(self, name: Optional[str] = 'root'):
        self.name = name
        self._direct_files: list[Path] = []
        self._nested_files: dict[str, SpatialStrata] = {}

    @property
    def files(self) -> list[Path]:
        all_files = self._direct_files.copy()
        for nested in self._nested_files.values():
            all_files.extend(nested.files)
        return all_files

    def __getitem__(self, key: str) -> Optional['SpatialStrata']:
        if not key:
            return self

        first = key.split('::')[0]
        rest = key[len(first) + 2 :]
        return self._nested_files[first][rest]

    def add(self, key: str, file) -> None:
        if not key:
            self.add_files(file)
            return

        first = key.split('::')[0]
        rest = key[len(first) + 2:]

        if first not in self._nested_files:
            self.nest_stratum(SpatialStrata(first))

        self._nested_files[first].add(rest, file)

    def add_files(self, *files: Union[Path, str]) -> None:
        self._direct_files.extend(files)

    def nest_stratum(self, stratum: 'SpatialStrata') -> None:
        if stratum.name in self._nested_files:
            raise ValueError(f'Stratum with name "{stratum.name}" already exists within "{self.name}"')
        self._nested_files[stratum.name] = stratum


class TerraSage:
    EARTH_RADIUS_KM = 6371

    @classmethod
    def generate_map(cls, markers: dict[Any, Coordinate], output: Union[Path, str]):
        points = list(markers.values())
        avg_lat = sum(lat for lat, lon in points) / len(points)
        avg_lon = sum(lon for lat, lon in points) / len(points)
        photo_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

        for label, (lat, lon) in markers.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                popup=str(label),
                color='#FF0000',
                fill=True,
                fill_opacity=0.7,
            ).add_to(photo_map)
        photo_map.save(output)

    @classmethod
    def haversine_distance(cls, coord1: Coordinate, coord2: Coordinate) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        lat1, lon1, lat2, lon2 = (math.radians(deg) for deg in (*coord1, *coord2))

        lat_delta = lat2 - lat1
        lon_delta = lon2 - lon1

        lat_term = math.sin(lat_delta / 2) ** 2
        lon_term = math.cos(lat1) * math.cos(lat2) * math.sin(lon_delta / 2) ** 2

        haversine_value = lat_term + lon_term
        central_angle = 2 * math.asin(math.sqrt(haversine_value))

        return cls.EARTH_RADIUS_KM * central_angle

    @classmethod
    def build_strata(cls,
                     coords: MediaCoordinates,
                     min_distance_threshold: float = 0.015,
                     min_subcluster_size: int = 5) -> SpatialStrata:
        """
        Build a location taxonomy using a minimum spanning tree approach.

        Args:
            coords: Dictionary mapping file paths to (latitude, longitude) coordinates
            min_distance_threshold: Minimum distance threshold in km (default: 0.015 km ≈ 50 ft)
                                   Groups closer than this won't be divided
            min_subcluster_size: Minimum number of files required to create a subcluster (default: 5)
                                Subclusters with fewer files will be added directly to the parent cluster

        Returns:
            A SpatialStratum object organizing the files by location
        """
        stratum = SpatialStrata(apparatus.random_label())

        graph = networkx.Graph()
        graph.add_nodes_from(coords)
        for (path_a, coord_a), (path_b, coord_b) in combinations(coords.items(), 2):
            graph.add_edge(path_a, path_b, weight=cls.haversine_distance(coord_a, coord_b))

        mst = networkx.minimum_spanning_tree(graph, weight='weight')

        def farthest_node_from(start):
            lengths, _ = networkx.single_source_dijkstra(mst, start, weight='weight')
            return max(lengths.items(), key=lambda x: x[1])[0]

        diameter_start = farthest_node_from(next(iter(mst.nodes)))
        diameter_end = farthest_node_from(diameter_start)

        # Get the path between the two farthest nodes
        diameter_path = networkx.shortest_path(mst, diameter_start, diameter_end, weight='weight')

        # Extract the edges and their weights from the longest path
        diameter_edges = [(a, b, mst[a][b]['weight']) for a, b in zip(diameter_path, diameter_path[1:])]

        # Find the maximum edge length in the longest path
        max_edge_length = max((dist for _, _, dist in diameter_edges), default=0)

        # Cut threshold is half the maximum edge length, but not less than min_distance_threshold
        cut_threshold = max(max_edge_length / 2, min_distance_threshold)

        # Remove edges from the MST that are longer than the cut threshold, dividing the graph into subclusters
        for a, b, data in list(mst.edges(data=True)):
            if data['weight'] > cut_threshold:
                mst.remove_edge(a, b)

        subclusters = list(networkx.connected_components(mst))
        if len(subclusters) == 1:
            stratum.add_files(*subclusters[0])
        else:
            for cluster in subclusters:
                if len(cluster) <= min_subcluster_size:
                    stratum.add_files(*cluster)
                else:
                    cluster_coords = {path: coords[path] for path in cluster}
                    sub_stratum = cls.build_strata(cluster_coords, min_distance_threshold, min_subcluster_size)
                    stratum.nest_stratum(sub_stratum)

        return stratum


class MetaMancer:
    codex = TTLCache(maxsize=1024, ttl=5 * 60)

    @classmethod
    def get_metadata(cls, file: Union[Path, str]) -> Scholia:
        """Returns metadata for the given file, whether cached or fresh."""
        if isinstance(file, str):
            file = Path(file)
        file = file.resolve()
        if not cls.is_cached(file):
            cls.cache(file)
        return cls.codex[file]

    @classmethod
    def is_cached(cls, file: Path) -> bool:
        """Returns whether the Metadata of the given File is cached in memory."""
        return file.resolve() in cls.codex

    @classmethod
    def cache(cls, file: Path) -> None:
        """Updates the cache with the current metadata of the given file."""
        file = file.resolve()
        cls.codex[file] = Scholia(file)

    @classmethod
    def clear(cls, file: Optional[Path] = None) -> None:
        """Clears cached metadata.

        :param file: An optional path to only clear cache for a specific file
        """
        if file:
            cls.codex.pop(file.resolve(), None)
        else:
            cls.codex.clear()

    @classmethod
    def determine_date(cls, file: Path) -> datetime:
        """Returns the most likely date for the given the specified file."""
        meta = cls.get_metadata(file)
        return meta.date or extract_date(file.stem) or meta.earliest_recorded_date()

    @classmethod
    def determine_camera(cls, file: Path) -> Optional[str]:
        """Returns the camera used to capture the specified photo/video.

        :param file: The File to analyze
        :return: The Camera make and model, 'conflict', or 'missing'
        """
        meta = cls.get_metadata(file)
        make = meta['Image.Make']
        model = meta['Image.Model']
        return f'{make} {model}' if make and model else None

    @classmethod
    def cluster(cls, files: Iterable[Path]) -> SpatialStrata:
        loci, nullius_loci = cls.get_loci(files)
        stratum = TerraSage.build_strata(loci)
        for file in nullius_loci:
            stratum.add('Nullius Loci', file)
        return stratum

    @classmethod
    def generate_photo_map(cls, files: Iterable[Path], output: Optional[Union[Path, str]] = 'photo_map.html'):
        TerraSage.generate_map(cls.get_loci(files)[0], output)

    @classmethod
    def get_loci(cls, files: Iterable[Path]) -> tuple[MediaCoordinates, set[Path]]:
        nullius_loci = set()
        loci = {}
        for file in files:
            try:
                lat, lon = cls.get_metadata(file).get_gps_coords()
                if lat and lon:
                    loci[file] = (lat, lon)
                else:
                    raise ValueError('Invalid GPS coordinates')
            except:
                nullius_loci.add(file)
        return loci, nullius_loci
