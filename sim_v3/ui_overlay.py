import pygame


def draw_metrics_box(screen, metrics, screen_w, screen_h):
    """
    간단 HUD : 3줄만 표시
    A→C, A→B, B→C
    """
    # HUD 높이 (짧게)
    hud_height = 80
    rect = pygame.Rect(0, screen_h - hud_height, screen_w, hud_height)

    # 반투명 배경
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 160))

    font = pygame.font.SysFont("malgungothic", 22)

    # 표시할 3개 구간
    show_keys = ["A→C", "A→B", "B→C"]

    lines = []

    for key in show_keys:
        if key not in metrics:
            lines.append(f"{key}  (데이터 없음)")
            continue

        data = metrics[key]

        # 최대한 짧은 표시 형식
        line = (
            f"{key}  "
            f"Avg:{data['avg']:.1f}s  "
            f"S:{data['shortest']:.0f}  "
            f"E:{data['weighted']:.2f}"
        )
        lines.append(line)

    # 텍스트 렌더링
    x = 10
    y = 5
    for line in lines:
        img = font.render(line, True, (255, 255, 255))
        surface.blit(img, (x, y))
        y += 25  # 줄 간격 넓게해서 절대 안 겹치도록 설정

    screen.blit(surface, rect)
