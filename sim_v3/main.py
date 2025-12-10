import pygame

from grid_v2 import GridV2
from vehicle_v2 import VehicleV2
from ui_overlay import draw_metrics_box
from metrics import MetricsTracker

FPS = 60


def main():
    pygame.init()

    grid = GridV2("road_map.txt", cell_size=24)
    width = grid.cols * grid.cell_size
    hud_height = 120
    height = grid.rows * grid.cell_size + hud_height  # 아래 HUD 영역

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("브라에스 패러독스 실험 시뮬레이터 v3")

    clock = pygame.time.Clock()

    vehicles = []
    spawn_timer = 0.0
    spawn_interval = 1.0  # 초당 1대 정도

    metrics = MetricsTracker(grid)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ======================
        # 차량 스폰
        # ======================
        spawn_timer += dt
        if spawn_timer >= spawn_interval:
            spawn_timer = 0.0
            start, goal = grid.get_spawn_and_goal()
            if start and goal:
                v = VehicleV2(start, goal)
                v.origin_zone = grid.zone_of(start[0])  # A/B/C
                v.dest_zone = grid.zone_of(goal[0])     # A/B/C
                vehicles.append(v)

        # ======================
        # 차량 업데이트
        # ======================
        alive = []
        for v in vehicles:
            v.update(grid, dt, vehicles)
            if v.arrived:
                # 도착한 애들만 로그에 기록
                metrics.log_trip(v.origin_zone, v.dest_zone, v.total_time)
            else:
                alive.append(v)
        vehicles = alive

        # ======================
        # 그리기
        # ======================
        screen.fill((15, 15, 30))
        grid.draw(screen)

        # 차량 그리기
        for v in vehicles:
            v.draw(screen, grid)

        # HUD 표시 (평가 팝업)
        metric_result = metrics.compute()
        draw_metrics_box(screen, metric_result, width, height)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
