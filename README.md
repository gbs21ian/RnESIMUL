# RnESIMUL
This repository contains a grid-based traffic simulator designed to reflect Korean-style road rules.  
It supports lane counts, lane-change rules, direction-specific lanes, permissive left turns, lane-specific speed limits, closed (blocked) cells, stop lines, traffic signals, vehicle movement and pathfinding, and provides real-time statistics. The simulation is set up so you can run experiments related to the Braess Paradox (how adding/removing links affects overall travel times).

Below is the project overview, file layout, per-file explanations, input data file formats, run instructions, debugging tips, and suggestions for extension.

---

## Table of Contents
- Project overview
- File / folder layout
- Per-file descriptions
- data/*.txt formats (UTF-8 recommended) and examples
- How to run
- Braess Paradox experiment guide
- Common errors & fixes
- Potential improvements
- License / contact

---

## Project overview
- Grid-based city map where each cell is a road / intersection / building. Road rules (lanes, lane-change permissions, turn permissions, speed limits, closed cells, stop lines, etc.) are loaded from text files.
- Vehicles use simple pathfinding (BFS) but must obey intersection rules, signals and stop lines.
- Visualization uses pygame. Real-time summary stats are shown in a tkinter popup.
- Results can be saved to CSV (press SPACE during the simulation).

---

## File / Folder Layout (recommended)
Project root (example: `simul/`):

- main.py                — Entry point; creates pygame window and runs main loop
- simulation.py          — Simulation manager: loads Grid, SignalMap and Vehicles; coordinates updates and results
- grid.py                — Map loaders, road rule loaders, drawing & congestion calculation
- vehicle.py             — Vehicle class and movement logic (checks rules, moves, renders)
- sig_nal.py             — Traffic signal pattern loader and current-state evaluator
- utils.py               — Utilities (BFS-based pathfinding, CSV saving)
- stats_popup.py         — Tkinter popup for live statistics
- data/                  — Input text files (see below)
  - road_map.txt
  - capacity_map.txt
  - lane_change_map.txt
  - turn_map.txt
  - speed_limit_map.txt
  - closed_cells.txt
  - stop_line.txt
  - vehicle_data.txt
  - signal_patterns.txt
- results.csv            — (created when saving results)

---

## Per-file descriptions

### main.py
- Initializes pygame and the main window.
- Creates a Simulation instance and runs the main loop at ~25 FPS.
- Starts stats_popup in a separate thread.
- Press SPACE during the simulation to trigger saving a CSV results file.

### simulation.py
- Loads the data folder (relative to the file location) and constructs Grid and SignalMap objects.
- Loads vehicles from data and manages the simulation lifecycle.
- update(): advances every vehicle each frame.
- stop(): compiles results (departure/arrival times, path, distance, average speed).
- get_live_stats() / get_results_csv(): provide data for the popup and CSV.

Note: simulation.py uses __file__-based absolute paths for the data folder to avoid issues with the current working directory.

### grid.py
- Contains multiple `load_*` functions that parse the data text files and produce metadata:
  - lane counts, lane-change permissions, per-direction lane assignments, speed limits, closed cells, stop lines, cell capacities, etc.
- All loaders open files with `encoding='utf-8'`, skip blank lines and lines starting with `#`, and handle missing files gracefully.
- draw(): renders the map onto the pygame surface. Road cells can be split visually into lanes.
- get_average_congestion(): computes mean of (vehicles in cell / capacity) across occupied cells.

### vehicle.py
- Defines vehicle state and movement logic.
- Key behaviors:
  - Check if in a closed/blocked cell and wait.
  - Compute path via BFS (utils.shortest_path) if no path or path stale.
  - Before entering next cell, enforce: lane-change permissions, direction-specific lane rules, permissive-left-turn rules (depending on signals), stop-line red rules.
  - Use lane-specific speed limits (km/h → m/s), convert into movement per frame and update x/y positions.
  - Track total distance, used roads, depart & arrival times.
- draw(): renders a rectangle representing the vehicle in the correct lane.

### sig_nal.py
- Loads traffic-signal pattern sequences from the pattern file.
- get_states(): uses current time to pick the active stage of each pattern sequence and returns a map of nearby cells to signal color.
- has_left_signal(rc): checks whether a left-turn signal appears in the configured patterns for a given intersection region.

### utils.py
- save_csv(fname, data): write rows to file with UTF-8 encoding.
- shortest_path(grid, rows, cols, start, goal): BFS on the grid that permits moving through `R` (road) and `C` (intersection) cells only. Returns a list of cell coordinates.

### stats_popup.py
- Simple tkinter GUI that queries Simulation.get_live_stats() every second and displays the current values in a readable format.

---

## data/*.txt file formats (UTF-8 recommended)

All loaders ignore blank lines and lines starting with `#`. Save these files in UTF-8 encoding.

1. road_map.txt
- Grid rows written line-by-line. Each character denotes a cell type:
  - `R` = road
  - `B` = building/non-road
  - `C` = intersection / special node
- Example:
```
RRR
CBC
RRR
```

2. capacity_map.txt
- Format: `r,c,capacity`
- Used for congestion metrics (capacity should be integer > 0).
- Example:
```
# r,c,capacity
0,0,2
0,1,2
1,1,3
```

3. lane_change_map.txt
- Format: `r,c,allow`
- `allow`: 1 (lane change allowed), 0 (lane change prohibited)
- Example:
```
# r,c,allow
0,0,1
0,1,0
```

4. turn_map.txt
- Format: `r,c,DIR,lane1,lane2,...`
- DIR = direction code, e.g. `U` (u-turn), `L` (left), `R` (right), `S` (straight)
- Lane indices are zero-based.
- Example:
```
# r,c,DIR,lane...
1,1,U,0
1,1,L,1
1,1,R,0,1
```

5. speed_limit_map.txt
- Format: `r,c,lane,speed_kmh`
- Per-lane speed limit in km/h.
- Example:
```
# r,c,lane,speed
0,0,0,30
0,0,1,40
```

6. closed_cells.txt
- Format: `r,c`
- Cells where entry is blocked (construction, military base, etc.)
- Example:
```
# r,c
1,2
2,1
```

7. stop_line.txt
- Format: `r,c`
- Locations of stop lines in front of signals.
- Example:
```
# r,c
1,1
0,2
```

8. vehicle_data.txt
- Format: `start_r,start_c,dir,speed_kmh,target_r,target_c,lane`
- `dir` is a starting heading (used for visualization / initial orientation); lane is the starting lane index.
- Example:
```
# start_r,start_c,dir,speed_kmh,target_r,target_c,lane
0,0,R,40,2,2,0
0,1,R,35,2,2,1
```

9. signal_patterns.txt
- Format: `r,c,pattern_string,duration_seconds`
- `pattern_string` example: `N-green;L-red;R-green`  (N: main/straight signal; L: left turn; R: right turn)
- You can include multiple lines for the same `(r,c)` to make a sequence of stages.
- Example:
```
# r,c,pattern,duration
1,1,N-green;L-red;R-green,10
1,1,N-red;L-green;R-red,10
```

---

## How to run

1. Install Python 3.8+ (3.11 recommended) and pygame:
   ```
   pip install pygame
   ```

2. Place code files and a `data/` folder (with the necessary text files saved in UTF-8) in the same project folder.

3. From the project root (the folder that contains main.py), run:
   ```
   python main.py
   ```

4. A pygame window will appear. A tkinter window will show live statistics. Press SPACE during the simulation to save results.csv.

---

## Braess Paradox experiment guide (brief)
- Goal: Compare network performance (average travel times / congestion) between scenarios with or without specific links.
- Suggested flow:
  1. Scenario A: baseline map (set `road_map.txt`, `closed_cells.txt`, etc.), run simulation, save results.
  2. Scenario B: add or remove a connection (edit `road_map.txt` or `closed_cells.txt`), run again.
  3. Compare average travel times, arrival counts and congestion metrics in the saved CSVs.
- Note: Current pathfinding is BFS (distance-based). To model selfish route choice and real Braess effects more accurately, incorporate dynamic time/cost-based path selection (e.g., Dijkstra with congestion costs or iterative user-equilibrium).

---

## Common errors & fixes

1. FileNotFoundError: `./data/xxx.txt`
   - Ensure `data/` is in the same directory as `main.py` (simulation.py uses `__file__`-based data path).
   - Run `dir .\data\` (PowerShell) or `ls data/` to verify files exist.
   - If missing, create the required text files (examples above).

2. UnicodeDecodeError when reading files
   - Save data files in UTF-8 (Windows Notepad defaults to ANSI or CP949 sometimes).
   - All file reads in the code use `encoding='utf-8'`.

3. Parsing ValueError from malformed lines
   - Check for stray text or malformed rows in data files; loaders skip blank lines and `#` comments, but malformed numeric fields will be skipped or cause errors if not handled.

4. OneDrive or permission issues
   - If your project directory is synced by OneDrive, ensure files are fully available locally and not in a placeholder state. Alternatively, use a local folder.

---

## Potential improvements / extensions

- Replace BFS with Dijkstra/A* using dynamic edge costs that reflect congestion (to model route choice and user equilibrium).
- Implement more realistic lane-change and car-following models (e.g., safety gaps, lane-change delays).
- Model intersection blocking (queueing that blocks upstream cells).
- Implement adaptive/optimized signal control and measure network-wide effects.
- Improve performance for large maps or many vehicles (profiling, spatial indexing, partial updates).

---

## License & Contact
- This is example code—feel free to adapt and extend. If you publish or share modified code, please attribute the original source.
- For questions or issues, open an issue in this repository.

---
