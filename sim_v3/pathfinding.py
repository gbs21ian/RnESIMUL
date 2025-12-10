from collections import deque


def shortest_path(grid, start, goal):
    """
    grid: GridV2 인스턴스
    start, goal: (r, c)
    return: [ (r, c), ... ]  start 포함
    """
    sr, sc = start
    gr, gc = goal

    if not grid.is_road(sr, sc) or not grid.is_road(gr, gc):
        return []

    R, C = grid.rows, grid.cols
    visited = [[False] * C for _ in range(R)]
    prev = [[None] * C for _ in range(R)]

    q = deque()
    q.append((sr, sc))
    visited[sr][sc] = True

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    found = False
    while q:
        r, c = q.popleft()
        if (r, c) == (gr, gc):
            found = True
            break

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if not visited[nr][nc] and grid.is_road(nr, nc):
                    visited[nr][nc] = True
                    prev[nr][nc] = (r, c)
                    q.append((nr, nc))

    if not found:
        return []

    # 경로 복원
    path = []
    cur = (gr, gc)
    while cur is not None:
        path.append(cur)
        r, c = cur
        cur = prev[r][c]

    path.reverse()
    return path
