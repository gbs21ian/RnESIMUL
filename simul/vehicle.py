import pygame
import math
from utils import shortest_path

CELL_SIZE_M = 5  # 1 셀이 실제 몇 미터인지(간단한 상수)

class Vehicle:
    def __init__(self, id, start_r, start_c, dir, speed_kmh, target_r, target_c, lane=0):
        self.id = id
        self.start_r = start_r
        self.start_c = start_c
        self.dir = dir
        self.speed_kmh = speed_kmh
        self.target_r = target_r
        self.target_c = target_c
        self.lane = lane
        self.x = float(start_c)
        self.y = float(start_r)
        self.arrived = False
        self.depart_time = None
        self.arrive_time = None
        self.path = []
        self.used_roads = []
        self.total_distance = 0.0

    def move(self, grid, signal_map, vehicles, sim_time):
        curr_rc = (int(self.y), int(self.x))
        if self.arrived:
            return
        if self.depart_time is None:
            self.depart_time = sim_time
        if int(self.x) == self.target_c and int(self.y) == self.target_r:
            self.arrived = True
            self.arrive_time = sim_time
            self.path.append((int(self.y), int(self.x)))
            return
        # 봉쇄된 셀이면 대기(또는 경로 재계산)
        if curr_rc in grid.closed_cells:
            return
        # 경로 계산 (BFS)
        if not self.path or (self.path and self.path[0] != curr_rc):
            self.path = shortest_path(grid.map, grid.rows, grid.cols, curr_rc, (self.target_r, self.target_c))
            if self.path and self.path[0] != curr_rc:
                self.path.insert(0, curr_rc)
        if not self.path or len(self.path) < 2:
            return
        next_r, next_c = self.path[1]
        next_rc = (next_r, next_c)
        # 차선 변경 허용/금지(단순화: 진입 셀 기준)
        if not grid.lane_change_rule.get(next_rc, True) and self.lane != self.lane:
            return
        # 방향별 전용 차로 검사
        turn_dir = self.get_next_turn_direction(next_rc)
        allowed_lanes = grid.turn_rule.get(next_rc, {}).get(turn_dir, [self.lane])
        if self.lane not in allowed_lanes:
            return
        # 비보호 좌회전 처리
        if turn_dir == "L" and not signal_map.has_left_signal(next_rc):
            sig = signal_map.get_state(next_rc)
            if sig not in ("green", "yellow"):
                return
        # 속도 제한(차선별)
        limit = grid.speed_limit.get((next_r, next_c, self.lane), int(self.speed_kmh))
        speed_ms = min(self.speed_kmh, limit) * 1000.0 / 3600.0
        # 프레임당 이동거리 (초당 프레임을 25로 가정)
        move_dist_m = speed_ms * (1.0 / 25.0)
        move_dist_cells = move_dist_m / CELL_SIZE_M
        # 정지선과 신호
        if next_rc in grid.stop_line:
            sig = signal_map.get_state(next_rc)
            if sig == "red":
                return
        # 실제 이동
        dx = next_c - self.x
        dy = next_r - self.y
        dist = math.hypot(dx, dy)
        if dist < 1e-4:
            # 이미 거의 위치함. 다음 스텝으로 경로 갱신
            if self.path:
                self.path.pop(0)
            return
        ratio = min(move_dist_cells / dist, 1.0)
        self.x += dx * ratio
        self.y += dy * ratio
        self.total_distance += move_dist_m
        # 기록
        if curr_rc not in self.used_roads:
            self.used_roads.append(curr_rc)

    def draw(self, screen, grid):
        cs = grid.cell_size
        lanes = grid.lane_count.get((int(self.y), int(self.x)), 1)
        lane_width = max(1, cs // lanes)
        px = int(self.x * cs + lane_width // 2 + (self.lane * lane_width))
        py = int(self.y * cs + cs // 2)
        car_width = max(4, lane_width - 6)
        car_height = cs // 3
        rect = pygame.Rect(px - car_width // 2, py - car_height // 2, car_width, car_height)
        pygame.draw.rect(screen, (20, 120, 255), rect, border_radius=6)
        pygame.draw.rect(screen, (40, 40, 60), rect, 2, border_radius=6)

    def get_direction(self):
        if not self.path or len(self.path) < 2:
            return 'S'
        curr_r, curr_c = self.path[0]
        next_r, next_c = self.path[1]
        if next_r < curr_r:
            return 'U'
        if next_r > curr_r:
            return 'D'
        if next_c < curr_c:
            return 'L'
        if next_c > curr_c:
            return 'R'
        return 'S'

    def get_next_turn_direction(self, next_rc):
        curr_r, curr_c = int(self.y), int(self.x)
        next_r, next_c = next_rc
        if next_r < curr_r:
            return 'U'
        if next_r > curr_r:
            return 'D'
        if next_c < curr_c:
            return 'L'
        if next_c > curr_c:
            return 'R'
        return 'S'