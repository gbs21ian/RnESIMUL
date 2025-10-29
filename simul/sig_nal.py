import time
import os

class SignalMap:
    def __init__(self, path):
        self.patterns = self.load_patterns(path)
        self.state = {}
        self.last_update = time.time()

    def load_patterns(self, path):
        patterns = {}
        if not os.path.exists(path):
            print(f"[Info] signal patterns file not found: {path}")
            return patterns
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 4:
                    continue
                try:
                    r, c = int(parts[0]), int(parts[1])
                except ValueError:
                    continue
                pattern_str = parts[2]
                try:
                    duration = int(parts[3])
                except ValueError:
                    continue
                patterns[(r, c)] = patterns.get((r, c), []) + [(pattern_str, duration)]
        return patterns

    def get_states(self):
        now = time.time()
        self.state = {}
        for rc, pat_seq in self.patterns.items():
            total = sum(p[1] for p in pat_seq)
            if total <= 0:
                continue
            t = int(now) % total
            acc = 0
            for pstr, dur in pat_seq:
                if acc <= t < acc + dur:
                    dir_colors = {}
                    for dpart in pstr.split(';'):
                        if '-' in dpart:
                            dir, color = dpart.split('-')
                            dir_colors[dir] = color
                    r, c = rc
                    # Apply the "N" color to a 3x3 block centered on the signal for visualization
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            self.state[(r + dr, c + dc)] = dir_colors.get('N', 'red')
                    break
                acc += dur
        return self.state

    def get_state(self, rc):
        states = self.get_states()
        return states.get(rc, None)

    def has_left_signal(self, rc):
        for center, pat_seq in self.patterns.items():
            r0, c0 = center
            r, c = rc
            if abs(r - r0) <= 1 and abs(c - c0) <= 1:
                for pstr, dur in pat_seq:
                    if 'L-green' in pstr or 'L-yellow' in pstr:
                        return True
        return False