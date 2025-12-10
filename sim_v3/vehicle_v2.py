import pygame

from pathfinding import shortest_path

CAR_COLOR = (20, 130, 255)


class VehicleV2:
    def __init__(self, start, goal, speed_cells_per_sec=3.0):
        self.start = start
        self.goal = goal
        self.r, self.c = float(start[0]), float(start[1])
        self.path = []
        self.arrived = False
        self.speed = speed_cells_per_sec
        self.total_time = 0.0

        # 나중에 main에서 채움 (A/B/C)
        self.origin_zone = None
        self.dest_zone = None

    @property
    def cell(self):
        return int(round(self.r)), int(round(self.c))

    def update(self, grid, dt, vehicles):
        if self.arrived:
            return

        self.total_time += dt
        curr = self.cell

        # 도착 체크
        if curr == self.goal:
            self.arrived = True
            return

        # ---------------------
        # 매 tick BFS 재탐색
        # ---------------------
        self.path = shortest_path(grid, curr, self.goal)
        if not self.path or len(self.path) < 2:
            return

        nr, nc = self.path[1]

        # 다음 칸을 이미 다른 차량이 점유하면 대기
        for v in vehicles:
            if v is self:
                continue
            if v.cell == (nr, nc):
                return

        # 이동
        dist = ((nr - self.r) ** 2 + (nc - self.c) ** 2) ** 0.5
        if dist < 1e-6:
            return

        step = self.speed * dt
        ratio = min(step / dist, 1.0)
        self.r += (nr - self.r) * ratio
        self.c += (nc - self.c) * ratio

    def draw(self, screen, grid):
        cs = grid.cell_size
        x = int(self.c * cs + cs / 2)
        y = int(self.r * cs + cs / 2)

        pygame.draw.circle(screen, CAR_COLOR, (x, y), cs // 3)
