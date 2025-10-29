import os
import time
from grid import Grid
from vehicle import Vehicle
from sig_nal import SignalMap

# BASE_PATH is set relative to this file's directory to avoid cwd issues
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class Simulation:
    def __init__(self, screen):
        self.screen = screen
        self.grid = Grid(
            os.path.join(BASE_PATH, "road_map.txt"),
            os.path.join(BASE_PATH, "capacity_map.txt"),
            os.path.join(BASE_PATH, "lane_change_map.txt"),
            os.path.join(BASE_PATH, "turn_map.txt"),
            os.path.join(BASE_PATH, "speed_limit_map.txt"),
            os.path.join(BASE_PATH, "closed_cells.txt"),
            os.path.join(BASE_PATH, "stop_line.txt")
        )
        self.signal_map = SignalMap(os.path.join(BASE_PATH, "signal_patterns.txt"))
        self.vehicles = []
        self.results = []
        self.finished = False
        self.start_time = time.time()
        self.load_vehicles(os.path.join(BASE_PATH, "vehicle_data.txt"))

    def load_vehicles(self, path):
        self.vehicles.clear()
        if not os.path.exists(path):
            print(f"[Info] vehicle data file not found: {path}")
            return
        with open(path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 7:
                    continue
                r, c, d, spd, tr, tc, lane = parts[:7]
                try:
                    self.vehicles.append(
                        Vehicle(idx, int(r), int(c), d, float(spd), int(tr), int(tc), int(lane))
                    )
                except ValueError:
                    # malformed line; skip
                    continue

    def update(self):
        if self.finished:
            return
        now = time.time()
        for v in self.vehicles:
            if not v.arrived:
                v.move(self.grid, self.signal_map, self.vehicles, now - self.start_time)
        if self.vehicles and all(v.arrived for v in self.vehicles):
            self.stop()

    def stop(self):
        if self.finished:
            return
        self.finished = True
        self.results = [
            {
                "id": v.id,
                "start": (v.start_r, v.start_c),
                "target": (v.target_r, v.target_c),
                "depart": v.depart_time if v.depart_time is not None else 0.0,
                "arrive": v.arrive_time if v.arrive_time is not None else 0.0,
                "total": (v.arrive_time - v.depart_time) if v.arrived and v.depart_time is not None else None,
                "distance": v.total_distance,
                "avg_speed_kmh": (v.total_distance / (v.arrive_time - v.depart_time) * 3.6) if v.arrived and (v.arrive_time - v.depart_time) and (v.arrive_time - v.depart_time) > 0 else 0,
                "path": v.path,
                "used_roads": v.used_roads
            }
            for v in self.vehicles
        ]

    def render(self):
        self.grid.draw(self.screen, self.signal_map.get_states(), self.vehicles)
        for v in self.vehicles:
            v.draw(self.screen, self.grid)

    def draw_grid_background(self):
        self.grid.draw_background(self.screen)

    def get_live_stats(self):
        arrived = sum(1 for v in self.vehicles if v.arrived)
        total = len(self.vehicles)
        times = [v.arrive_time - v.depart_time for v in self.vehicles if v.arrived and v.depart_time is not None and v.arrive_time is not None]
        avg_time = sum(times)/len(times) if times else 0
        max_time = max(times) if times else 0
        min_time = min(times) if times else 0
        if arrived:
            avg_speed = sum((v.total_distance / (v.arrive_time - v.depart_time) * 3.6) for v in self.vehicles if v.arrived and (v.arrive_time - v.depart_time) > 0) / arrived
        else:
            avg_speed = 0
        avg_congestion = self.grid.get_average_congestion(self.vehicles)
        return [
            "[Live Traffic Stats]",
            f"Arrived vehicles: {arrived}/{total}",
            f"Average travel time: {avg_time:.2f}s",
            f"Average speed: {avg_speed:.2f} km/h",
            f"Min: {min_time:.2f}s | Max: {max_time:.2f}s",
            f"Average congestion: {avg_congestion:.2f}",
            "(Press SPACE to show/save results)",
            ""
        ]

    def get_results_csv(self):
        header = ["vehicle_id","start_r","start_c","target_r","target_c","depart_time","arrive_time","total_time","distance_m","avg_speed_kmh","path","used_roads"]
        rows = []
        for r in self.results:
            rows.append([
                r["id"], r["start"][0], r["start"][1], r["target"][0], r["target"][1],
                f"{r['depart']:.2f}", f"{r['arrive']:.2f}", f"{r['total']:.2f}" if r['total'] is not None else "",
                f"{r['distance']:.2f}", f"{r['avg_speed_kmh']:.2f}",
                ";".join(str(x) for x in r["path"]),
                ";".join(str(x) for x in r["used_roads"])
            ])
        return [header] + rows