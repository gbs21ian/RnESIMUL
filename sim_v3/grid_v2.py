import pygame

CELL_ROAD = "▧"
CELL_XING = "▩"
CELL_BUILD = "▣"
CELL_EMPTY = "※"

COLOR_ROAD = (40, 40, 70)
COLOR_XING = (120, 120, 170)
COLOR_BUILD = (30, 30, 30)


class GridV2:
    def __init__(self, filename="road_map.txt", cell_size=20):
        self.cell_size = cell_size

        self.map = []
        self.rows = 0
        self.cols = 0

        self.load(filename)
        self.compute_zones()  # A/B/C zone 고정 생성

    # ----------------------------------------
    # 파일 읽기
    # ----------------------------------------
    def load(self, filename):
        with open(filename, encoding="utf-8") as f:
            lines = [x.rstrip("\n") for x in f if x.strip()]

        self.rows = len(lines)
        self.cols = max(len(l) for l in lines)

        for l in lines:
            row = list(l) + [CELL_EMPTY] * (self.cols - len(l))
            self.map.append(row)

    # ----------------------------------------
    # 도로 판정
    # ----------------------------------------
    def is_road(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.map[r][c] in (CELL_ROAD, CELL_XING)
        return False

    # ----------------------------------------
    # Zone 고정 3분할 (A/B/C)
    # ----------------------------------------
    def compute_zones(self):
        """
        맵 전체 높이를 단순히 3등분해서 A/B/C로 나눈다.
        A: 위쪽 1/3, B: 가운데 1/3, C: 아래 1/3
        """
        H = self.rows
        A_end = H // 3
        B_end = (2 * H) // 3

        self.zone_ranges = {
            "A": (0, A_end),
            "B": (A_end, B_end),
            "C": (B_end, H),
        }

    # ----------------------------------------
    # 특정 r이 A/B/C 중 어디인지
    # ----------------------------------------
    def zone_of(self, r):
        for name, (lo, hi) in self.zone_ranges.items():
            if lo <= r < hi:
                return name
        return "C"  # fallback

    # ----------------------------------------
    # 스폰 & 골 선택
    # ----------------------------------------
    def get_spawn_and_goal(self):
        # 위쪽 도로(A지역)에서 출발
        A_lo, A_hi = self.zone_ranges["A"]
        A_candidates = [(r, c) for r in range(A_lo, A_hi)
                        for c in range(self.cols) if self.is_road(r, c)]

        # 아래쪽 도로(C지역)로 도착
        C_lo, C_hi = self.zone_ranges["C"]
        C_candidates = [(r, c) for r in range(C_lo, C_hi)
                        for c in range(self.cols) if self.is_road(r, c)]

        import random
        if not A_candidates or not C_candidates:
            return None, None

        return random.choice(A_candidates), random.choice(C_candidates)

    # ----------------------------------------
    # 그리기
    # ----------------------------------------
    def draw(self, screen):
        cs = self.cell_size
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.map[r][c]
                if tile == CELL_ROAD:
                    color = COLOR_ROAD
                elif tile == CELL_XING:
                    color = COLOR_XING
                elif tile == CELL_BUILD:
                    color = COLOR_BUILD
                else:
                    continue
                pygame.draw.rect(screen, color, (c * cs, r * cs, cs, cs))
