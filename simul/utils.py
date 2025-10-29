import csv
from collections import deque

def save_csv(fname, data):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

def shortest_path(grid, rows, cols, start, goal):
    # BFS 기반 단순 경로탐색 (격자 상하좌우)
    q = deque()
    q.append((start, [start]))
    visited = {start}
    while q:
        curr, path = q.popleft()
        if curr == goal:
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = curr[0] + dr, curr[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                try:
                    cell = grid[nr][nc]
                except Exception:
                    continue
                if cell not in ('R','C'):
                    continue
                npos = (nr, nc)
                if npos in visited:
                    continue
                visited.add(npos)
                q.append((npos, path + [npos]))
    return []