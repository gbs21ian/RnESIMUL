import os
import pygame
import math

ARROW_COLOR = (60, 60, 200)

def draw_arrow(screen, x, y, angle, size=16, thick=4):
    end_x = x + size * math.cos(angle)
    end_y = y + size * math.sin(angle)
    pygame.draw.line(screen, ARROW_COLOR, (x, y), (end_x, end_y), thick)
    ah = size // 2
    left = (end_x + ah * math.cos(angle + 2.5), end_y + ah * math.sin(angle + 2.5))
    right = (end_x + ah * math.cos(angle - 2.5), end_y + ah * math.sin(angle - 2.5))
    pygame.draw.polygon(screen, ARROW_COLOR, [(end_x, end_y), left, right])

class Grid:
    def __init__(
        self,
        road_map_path,
        capacity_map_path,
        lane_change_path,
        turn_rule_path,
        speed_limit_path,
        closed_cells_path,
        stop_line_path,
    ):
        self.cell_size = 40
        # colors
        self.bg_color = (230, 230, 240)
        self.road_color = (215, 215, 220)
        self.road_edge_color = (140, 140, 140)
        self.build_color = (180, 140, 80)
        self.round_color = (160, 160, 210)

        # load files (each loader is robust to missing files)
        self.map, self.rows, self.cols = self.load_map(road_map_path)
        self.capacity = self.load_capacity(capacity_map_path)
        self.lane_count = self.load_lane_count(capacity_map_path)
        self.lane_change_rule = self.load_lane_change(lane_change_path)
        self.turn_rule = self.load_turn_rule(turn_rule_path)
        self.speed_limit = self.load_speed_limit(speed_limit_path)
        self.closed_cells = self.load_closed_cells(closed_cells_path)
        self.stop_line = self.load_stop_line(stop_line_path)

    def load_map(self, path):
        grid = []
        if not os.path.exists(path):
            print(f"[Warning] road map file not found: {path}. Using empty map.")
            return [], 0, 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                grid.append(list(line))
        rows = len(grid)
        cols = max(len(row) for row in grid) if rows > 0 else 0
        grid = grid[::-1]
        return grid, rows, cols

    def load_capacity(self, path):
        cap = {}
        if not os.path.exists(path):
            print(f"[Warning] capacity file not found: {path}. Using default capacities.")
            return cap
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                try:
                    r, c, val = map(int, parts[:3])
                except ValueError:
                    continue
                cap[(r, c)] = val
        return cap

    def load_lane_count(self, path):
        lane_count = {}
        if not os.path.exists(path):
            return lane_count
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                try:
                    r, c, lane = map(int, parts[:3])
                except ValueError:
                    continue
                lane_count[(r, c)] = lane
        return lane_count

    def load_lane_change(self, path):
        rule = {}
        if not os.path.exists(path):
            return rule
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                try:
                    r, c, allow = map(int, parts[:3])
                except ValueError:
                    continue
                rule[(r, c)] = bool(allow)
        return rule

    def load_turn_rule(self, path):
        rule = {}
        if not os.path.exists(path):
            return rule
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 4:
                    continue
                r, c, dir = parts[0], parts[1], parts[2]
                lanes = parts[3:]
                try:
                    rr, cc = int(r), int(c)
                    lanes_int = [int(x) for x in lanes if x != ""]
                except ValueError:
                    continue
                rule.setdefault((rr, cc), {}).setdefault(dir, []).extend(lanes_int)
        return rule

    def load_speed_limit(self, path):
        limit = {}
        if not os.path.exists(path):
            return limit
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 4:
                    continue
                try:
                    r, c, l, s = map(int, parts[:4])
                except ValueError:
                    continue
                limit[(r, c, l)] = s
        return limit

    def load_closed_cells(self, path):
        closed = set()
        # debug print to help trace path issues
        try:
            print(f"[DEBUG] load_closed_cells called. path={path}, exists={os.path.exists(path)}, abspath={os.path.abspath(path)}")
        except Exception:
            pass
        if not os.path.exists(path):
            print(f"[Info] closed_cells file not found: {path}. Continuing with no closed cells.")
            return closed
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                try:
                    coords = tuple(map(int, parts[:2]))
                except ValueError:
                    continue
                closed.add(coords)
        return closed

    def load_stop_line(self, path):
        stop = set()
        if not os.path.exists(path):
            return stop
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                try:
                    coords = tuple(map(int, parts[:2]))
                except ValueError:
                    continue
                stop.add(coords)
        return stop

    def draw(self, screen, signals, vehicles):
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c * self.cell_size, r * self.cell_size
                cell = self.map[r][c] if r < len(self.map) and c < len(self.map[r]) else 'B'
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                if cell == 'B':
                    pygame.draw.rect(screen, self.build_color, rect)
                elif cell == 'R':
                    lanes = self.lane_count.get((r, c), 1)
                    lane_width = max(1, self.cell_size // lanes)
                    for l in range(lanes):
                        lane_rect = pygame.Rect(x + l * lane_width, y, lane_width - 2, self.cell_size)
                        pygame.draw.rect(screen, self.road_color, lane_rect)
                        pygame.draw.line(screen, (180, 180, 180), (x + l * lane_width, y), (x + l * lane_width, y + self.cell_size), 1)
                    if (r, c) in self.closed_cells:
                        pygame.draw.rect(screen, (180, 30, 30), rect, 0)
                elif cell == 'C':
                    pygame.draw.rect(screen, self.round_color, rect)
                    pygame.draw.rect(screen, (120, 120, 200), rect, 3)
                if (r, c) in signals:
                    color = signals[(r, c)]
                    col = {'red': (240, 60, 60), 'green': (80, 220, 80), 'yellow': (240, 220, 60)}.get(color, (220, 220, 220))
                    pygame.draw.circle(screen, col, (x + self.cell_size // 2, y + self.cell_size // 2), 14)
                if (r, c) in self.stop_line:
                    pygame.draw.line(screen, (20, 20, 20), (x, y + 2), (x + self.cell_size, y + 2), 4)

    def draw_background(self, screen):
        for i in range(self.cols + 1):
            x = i * self.cell_size
            pygame.draw.line(screen, (100, 100, 130), (x, 0), (x, self.rows * self.cell_size), 3)
        for j in range(self.rows + 1):
            y = j * self.cell_size
            pygame.draw.line(screen, (100, 100, 130), (0, y), (self.cols * self.cell_size, y), 3)

    def get_average_congestion(self, vehicles):
        cell_count = {}
        for v in vehicles:
            if v.arrived:
                continue
            rc = (int(v.y), int(v.x))
            cell_count[rc] = cell_count.get(rc, 0) + 1
        ratios = []
        for rc, cnt in cell_count.items():
            cap = self.capacity.get(rc, 1)
            if cap <= 0:
                continue
            ratios.append(cnt / cap)
        return sum(ratios) / len(ratios) if ratios else 0