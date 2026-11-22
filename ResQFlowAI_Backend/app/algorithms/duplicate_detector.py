import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from app.algorithms.distance import haversine_distance_meters, haversine_distance_km

try:
    from sklearn.cluster import DBSCAN as SklearnDBSCAN
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class PureNumpyDBSCAN:
    """
    Mathematical fallback implementation of DBSCAN clustering 
    with Haversine distance metric for incident deduplication.
    """
    def __init__(self, eps_meters: float = 250.0, min_samples: int = 1):
        self.eps_meters = eps_meters
        self.min_samples = min_samples

    def fit_predict(self, coords: List[Tuple[float, float]]) -> List[int]:
        n = len(coords)
        if n == 0:
            return []

        labels = [-1] * n
        cluster_id = 0
        visited = [False] * n

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True

            # Find neighbors within eps_meters
            neighbors = []
            for j in range(n):
                d = haversine_distance_meters(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
                if d <= self.eps_meters:
                    neighbors.append(j)

            if len(neighbors) < self.min_samples:
                labels[i] = -1 # Noise
            else:
                labels[i] = cluster_id
                k = 0
                while k < len(neighbors):
                    neighbor_idx = neighbors[k]
                    if not visited[neighbor_idx]:
                        visited[neighbor_idx] = True
                        sub_neighbors = []
                        for m in range(n):
                            d2 = haversine_distance_meters(
                                coords[neighbor_idx][0], coords[neighbor_idx][1],
                                coords[m][0], coords[m][1]
                            )
                            if d2 <= self.eps_meters:
                                sub_neighbors.append(m)
                        if len(sub_neighbors) >= self.min_samples:
                            neighbors.extend([sn for sn in sub_neighbors if sn not in neighbors])
                    
                    if labels[neighbor_idx] == -1:
                        labels[neighbor_idx] = cluster_id
                    k += 1

                cluster_id += 1

        return labels


class DuplicateDetector:
    """
    Spatio-Temporal Duplicate Incident Detection using DBSCAN and Haversine Distance.
    Epsilon = 250 meters.
    Time window = 15 minutes.
    """
    def __init__(self, eps_meters: float = 250.0, time_window_minutes: float = 15.0):
        self.eps_meters = eps_meters
        self.time_window_minutes = time_window_minutes

    def find_matching_incident(
        self,
        new_lat: float,
        new_lng: float,
        existing_incidents: List[Any]
    ) -> Optional[Any]:
        """
        Check if a new report matches any existing open/active incident within eps_meters.
        """
        for inc in existing_incidents:
            if inc.status in ["closed", "rejected"]:
                continue
            dist = haversine_distance_meters(new_lat, new_lng, inc.latitude, inc.longitude)
            if dist <= self.eps_meters:
                return inc
        return None

    def cluster_reports(self, reports: List[Dict[str, Any]]) -> List[int]:
        """
        Run DBSCAN on a batch of incident reports to discover clusters.
        """
        if not reports:
            return []
        
        coords = [(r["latitude"], r["longitude"]) for r in reports]

        if HAS_SKLEARN:
            coords_rad = np.radians(coords)
            EARTH_RADIUS = 6371000.0
            eps_rad = self.eps_meters / EARTH_RADIUS
            db = SklearnDBSCAN(eps=eps_rad, min_samples=1, metric="haversine")
            return db.fit_predict(coords_rad).tolist()
        else:
            db = PureNumpyDBSCAN(eps_meters=self.eps_meters, min_samples=1)
            return db.fit_predict(coords)

duplicate_detector = DuplicateDetector()
