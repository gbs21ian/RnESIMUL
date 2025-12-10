from pathfinding import shortest_path


class MetricsTracker:
    def __init__(self, grid):
        self.grid = grid
        # (origin_zone, dest_zone, time_sec)
        self.travel_log = []

        self.zones = ["A", "B", "C"]

        # zone 대표 도로 좌표 저장
        self.zone_points = {}
        for z in self.zones:
            lo, hi = grid.zone_ranges[z]
            pts = [(r, c) for r in range(lo, hi)
                   for c in range(grid.cols)
                   if grid.is_road(r, c)]
            if not pts:
                pts = [(lo, 0)]
            self.zone_points[z] = pts

    # ------------------------------
    def log_trip(self, origin, dest, time_sec):
        self.travel_log.append((origin, dest, time_sec))

    # ------------------------------
    def compute(self):
        """
        반환 형식:
        {
            "A→C": {
                "avg": float,
                "shortest": float,
                "weighted": float,
                "ratio": float,
                "normalized": float
            },
            ...
        }
        """
        result = {}

        # 1) 평균 통행 시간
        avg_times = {}
        for a in self.zones:
            for b in self.zones:
                if a == b:
                    continue
                key = f"{a}→{b}"
                times = [t for (o, d, t) in self.travel_log if o == a and d == b]
                avg_times[key] = sum(times) / len(times) if times else 0.0

        # 2) BFS 최단 거리
        shortest = {}
        for a in self.zones:
            for b in self.zones:
                if a == b:
                    continue
                key = f"{a}→{b}"
                shortest[key] = self.shortest_distance_between_zones(a, b)

        # 3) 효율지수: avg / shortest
        weighted = {}
        for key in avg_times:
            s = shortest.get(key, 0.0)
            weighted[key] = (avg_times[key] / s) if s > 0 else 0.0

        # 4) 형평성: avg / 전체 평균
        all_avg = (sum(avg_times.values()) / len(avg_times)) if avg_times else 1.0
        ratio = {}
        for key in avg_times:
            ratio[key] = (avg_times[key] / all_avg) if all_avg > 0 else 1.0

        # 5) 정규화지수: weighted / max_weight
        max_weight = max(weighted.values()) if weighted else 1.0
        if max_weight == 0:
            max_weight = 1.0

        normalized = {}
        for key in weighted:
            normalized[key] = weighted[key] / max_weight

        # 6) 최종 result 구성
        for key in avg_times:
            result[key] = {
                "avg": avg_times[key],
                "shortest": shortest[key],
                "weighted": weighted[key],
                "ratio": ratio[key],
                "normalized": normalized[key],
            }

        return result

    # ------------------------------
    # Zone BFS 거리
    # ------------------------------
    def shortest_distance_between_zones(self, z1, z2):
        s1 = self.zone_points[z1][0]
        s2 = self.zone_points[z2][0]

        path = shortest_path(self.grid, s1, s2)
        if path:
            return len(path)
        return 1
