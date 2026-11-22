import heapq
import math
from typing import List, Dict, Tuple, Optional
from app.algorithms.distance import haversine_distance_km

class RoadNetworkGraph:
    """
    Graph representation of the city road grid for A* routing.
    Contains vertices (intersections) and edges (road segments).
    Supports dynamic edge blockage and real-time rerouting.
    """
    def __init__(self):
        # Nodes: id -> {"name": str, "lat": float, "lng": float}
        self.nodes: Dict[str, Dict] = {}
        # Adjacency list: node_id -> [ {"target": str, "weight_km": float, "road_name": str, "speed_limit": float, "blocked": bool} ]
        self.edges: Dict[str, List[Dict]] = {}
        self._build_default_city_grid()

    def add_node(self, node_id: str, name: str, lat: float, lng: float):
        self.nodes[node_id] = {"name": name, "lat": lat, "lng": lng}
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, u: str, v: str, road_name: str, speed_limit: float = 60.0):
        lat1, lon1 = self.nodes[u]["lat"], self.nodes[u]["lng"]
        lat2, lon2 = self.nodes[v]["lat"], self.nodes[v]["lng"]
        dist = haversine_distance_km(lat1, lon1, lat2, lon2)
        
        # Bi-directional road
        self.edges[u].append({
            "target": v,
            "weight_km": dist,
            "road_name": road_name,
            "speed_limit": speed_limit,
            "blocked": False
        })
        self.edges[v].append({
            "target": u,
            "weight_km": dist,
            "road_name": road_name,
            "speed_limit": speed_limit,
            "blocked": False
        })

    def _build_default_city_grid(self):
        # Realistic urban road grid around lat: 12.9719, lng: 77.5937
        center_lat = 12.9719
        center_lng = 77.5937

        # Key intersection nodes
        nodes_def = [
            ("N1", "North Ring Interchange", center_lat + 0.040, center_lng - 0.030),
            ("N2", "Central Expressway Overpass", center_lat + 0.025, center_lng + 0.000),
            ("N3", "East Tech Corridor", center_lat + 0.030, center_lng + 0.035),
            ("N4", "West Metro Junction", center_lat + 0.005, center_lng - 0.035),
            ("N5", "Central Plaza Hub", center_lat + 0.000, center_lng + 0.000),
            ("N6", "Grand Commercial Square", center_lat + 0.005, center_lng + 0.030),
            ("N7", "Southwest Bypass", center_lat - 0.030, center_lng - 0.030),
            ("N8", "Hospital Way Junction", center_lat - 0.025, center_lng + 0.005),
            ("N9", "South Ring Terminal", center_lat - 0.035, center_lng + 0.035),
            # Auxiliary bypass nodes to guarantee realistic alternative detour paths
            ("A1", "West Green Bypass", center_lat + 0.020, center_lng - 0.050),
            ("A2", "East Valley Parkway", center_lat + 0.015, center_lng + 0.055),
            ("A3", "South Canal Arterial", center_lat - 0.015, center_lng - 0.045),
            ("A4", "Riverside Boulevard", center_lat - 0.015, center_lng + 0.045),
        ]

        for nid, name, lat, lng in nodes_def:
            self.add_node(nid, name, lat, lng)

        # Connect road edges
        roads = [
            ("N1", "N2", "North Ring Road", 70.0),
            ("N2", "N3", "Outer Tech Expressway", 70.0),
            ("N1", "N4", "West Arterial Road", 55.0),
            ("N2", "N5", "Central Expressway Overpass", 60.0), # Target prime road for blockage demo
            ("N3", "N6", "East Boulevard", 50.0),
            ("N4", "N5", "MG Road West", 45.0),
            ("N5", "N6", "Tech Avenue", 50.0),
            ("N4", "N7", "Industrial Link Road", 50.0),
            ("N5", "N8", "Hospital Way Avenue", 45.0),
            ("N6", "N9", "East Ring Extension", 60.0),
            ("N7", "N8", "South Boulevard", 50.0),
            ("N8", "N9", "Southern Radial", 55.0),
            
            # Alternative bypass routes
            ("N1", "A1", "Northern Bypass", 65.0),
            ("A1", "N4", "Outer West Ring", 60.0),
            ("A1", "A3", "Greenway Bypass", 55.0),
            ("A3", "N7", "Southwest Feeder", 50.0),
            
            ("N3", "A2", "Valley Expressway", 65.0),
            ("A2", "N6", "Parkway Link", 55.0),
            ("A2", "A4", "Eastern Arterial", 60.0),
            ("A4", "N9", "South Canal Way", 50.0),
            ("A3", "N8", "South Link Spur", 45.0),
            ("A4", "N8", "Medical Center Connector", 45.0),
        ]

        for u, v, rname, speed in roads:
            self.add_edge(u, v, rname, speed)

    def find_nearest_node(self, lat: float, lng: float) -> str:
        """Find the closest intersection node in the graph to a given coordinate."""
        best_node = None
        min_dist = float("inf")
        for nid, data in self.nodes.items():
            d = haversine_distance_km(lat, lng, data["lat"], data["lng"])
            if d < min_dist:
                min_dist = d
                best_node = nid
        return best_node

    def set_road_blockage(self, road_name: str, blocked: bool = True):
        """Toggle blockage on road segments matching road_name."""
        for u, edges in self.edges.items():
            for e in edges:
                if road_name.lower() in e["road_name"].lower():
                    e["blocked"] = blocked

    def clear_all_blockages(self):
        for u, edges in self.edges.items():
            for e in edges:
                e["blocked"] = False

    def astar_search(self, start_node: str, goal_node: str) -> Tuple[Optional[List[str]], float, float]:
        """
        A* algorithm to find optimal path between start_node and goal_node.
        Returns: (path_node_ids, total_distance_km, eta_minutes)
        """
        if start_node not in self.nodes or goal_node not in self.nodes:
            return None, 0.0, 0.0
            
        if start_node == goal_node:
            return [start_node], 0.0, 0.0

        goal_lat = self.nodes[goal_node]["lat"]
        goal_lng = self.nodes[goal_node]["lng"]

        # Priority queue stores tuples: (f_score, current_node, current_path, current_distance_km, current_travel_time_hrs)
        # Heuristic: Haversine distance to goal divided by max theoretical speed (70 km/h) = travel time in hours
        h_start = (haversine_distance_km(self.nodes[start_node]["lat"], self.nodes[start_node]["lng"], goal_lat, goal_lng) / 70.0)
        
        open_set = [(h_start, start_node, [start_node], 0.0, 0.0)]
        heapq.heapify(open_set)
        
        best_g_time = {start_node: 0.0}

        while open_set:
            f_score, current, path, dist_km, time_hrs = heapq.heappop(open_set)

            if current == goal_node:
                return path, round(dist_km, 2), round(time_hrs * 60.0, 1)

            if time_hrs > best_g_time.get(current, float("inf")):
                continue

            for edge in self.edges.get(current, []):
                if edge["blocked"]:
                    continue # Skip impassable blocked segment

                neighbor = edge["target"]
                seg_dist = edge["weight_km"]
                seg_time = seg_dist / max(10.0, edge["speed_limit"]) # hours

                tentative_g_time = time_hrs + seg_time

                if tentative_g_time < best_g_time.get(neighbor, float("inf")):
                    best_g_time[neighbor] = tentative_g_time
                    h = (haversine_distance_km(self.nodes[neighbor]["lat"], self.nodes[neighbor]["lng"], goal_lat, goal_lng) / 70.0)
                    new_f = tentative_g_time + h
                    heapq.heappush(open_set, (
                        new_f,
                        neighbor,
                        path + [neighbor],
                        dist_km + seg_dist,
                        tentative_g_time
                    ))

        # If no path found (e.g. completely isolated)
        return None, 0.0, 0.0

    def plan_full_emergency_route(
        self,
        ambulance_lat: float,
        ambulance_lng: float,
        incident_lat: float,
        incident_lng: float,
        hospital_lat: float,
        hospital_lng: float
    ) -> Dict:
        """
        Plans two-phase emergency route:
        Leg 1: Ambulance -> Incident
        Leg 2: Incident -> Hospital
        Returns combined polyline coordinates [[lat, lng], ...], distance, and ETA.
        """
        amb_node = self.find_nearest_node(ambulance_lat, ambulance_lng)
        inc_node = self.find_nearest_node(incident_lat, incident_lng)
        hosp_node = self.find_nearest_node(hospital_lat, hospital_lng)

        path_leg1, dist1, eta1 = self.astar_search(amb_node, inc_node)
        path_leg2, dist2, eta2 = self.astar_search(inc_node, hosp_node)

        # Assemble full path
        full_node_path = []
        if path_leg1:
            full_node_path.extend(path_leg1)
        if path_leg2:
            if full_node_path and full_node_path[-1] == path_leg2[0]:
                full_node_path.extend(path_leg2[1:])
            else:
                full_node_path.extend(path_leg2)

        # Convert node ids to lat/lng polyline
        polyline = [[ambulance_lat, ambulance_lng]]
        for nid in full_node_path:
            polyline.append([self.nodes[nid]["lat"], self.nodes[nid]["lng"]])
        
        # Ensure incident and hospital points are explicitly on the polyline
        polyline.insert(-1, [incident_lat, incident_lng])
        polyline.append([hospital_lat, hospital_lng])

        total_dist = round(dist1 + dist2 + 0.5, 2)
        total_eta = round(eta1 + eta2 + 2.0, 1) # add buffer for pickup & triage

        return {
            "node_path": full_node_path,
            "polyline": polyline,
            "distance_km": total_dist,
            "eta_minutes": total_eta,
            "leg1_eta": eta1,
            "leg2_eta": eta2
        }

# Singleton road graph instance
city_road_graph = RoadNetworkGraph()
