
# 🚦 Braess Paradox Experiment Simulator v3
**Braess Paradox Traffic Simulation (Python + Pygame)**

This is a **grid-based, real-time traffic simulator** built for urban reconstruction research and traffic flow analysis. It is specifically designed to let you experiment with the **Braess Paradox**, a key concept in modern urban planning theory.

The goals of this project are:

* Visually confirm how changes in road structure affect overall traffic flow.
* Experimentally demonstrate how individual driver behavior based on finding the shortest path can, counter-intuitively, create traffic congestion.
* Compare traffic efficiency based on the structure of urban reconstruction (Zones A, B, and C).
* Evaluate road structures using real-time performance metrics (HUD).

---

# 📌 Key Features

### ✅ **1. Real-Time BFS Pathfinding**
All vehicles re-calculate the **fastest route** using Breadth-First Search (BFS) every tick.
→ Implements a natural flow that instantly reacts to changing road conditions without creating permanent gridlock.

---

### ✅ **2. Automatic Vehicle Spawning & Deletion**
* Vehicles spawn in **Zone A** (top road).
* Vehicles move towards **Zone C** (bottom road).
* Vehicles are automatically deleted upon reaching the destination → Prevents cars from accumulating and causing non-stop congestion.

---

### ✅ **3. Automatic Zone (A/B/C) Division**
The map is automatically divided along its vertical axis for evaluation purposes:
* **A** = Top 1/3
* **B** = Middle 1/3
* **C** = Bottom 1/3

---

### ✅ **4. Real-Time HUD (3-Line Core Metrics)**
Simple traffic evaluation metrics are displayed at the bottom of the screen:

```yaml
A→C Avg: 6.7s S:12 E:0.56
A→B Avg: 4.3s S:10 E:0.43
B→C Avg: 5.8s S:11 E:0.52
````

Displayed Metrics:

| Metric | Description |
| :----- | :---------- |
| **Avg** | Actual **Average Travel Time** for vehicles |
| **S** | **Shortest Distance** based on BFS |
| **E (Efficiency)** | Avg / Shortest (Lower value indicates **higher efficiency**) |

-----

### ✅ **5. Custom Map Support (`road_map.txt`)**

Text-based Cell Rules:

| Character | Meaning |
| :-------- | :------ |
| `▧` | Road |
| `▩` | Intersection |
| `▣` | Building |
| `※` | Empty Cell |

Modifying the map allows for immediate experimentation with new traffic structures.

-----

# 🧱 Project Structure

```yaml
sim_v3/
│
├── main.py        # Simulator execution entry point
├── grid_v2.py     # Map loading, zone division, road determination
├── vehicle_v2.py  # Vehicle movement logic (BFS-based)
├── pathfinding.py # BFS shortest path algorithm
├── metrics.py     # Traffic evaluation metrics calculation
├── ui_overlay.py  # HUD rendering
├── road_map.txt   # Custom road map
│
└── README.md
```

-----

# ▶ How to Run

## 1\. Install Required Libraries

```bash
pip install pygame
```

## 2\. Execute

```bash
python main.py
```

## 🎮 Controls

The simulation is **automatic**. Vehicles are spawned and move on their own upon execution.

  * **Exit:** Close the window to terminate the simulator.

## 🧪 Usage for Research (Experimentation)

This project is optimized for experimenting with the **Braess Paradox**.

### Example Experiment Scenarios:

#### 🟦 Experiment A: Does Adding a Road Improve Efficiency?

1.  Add a few more `▧` (Road) cells in `road_map.txt`.
2.  Run the simulator.
3.  Compare the change in the **Efficiency (E)** metric on the HUD.
    → If adding a road **lowers** the overall efficiency, the **Braess Paradox** has occurred.

#### 🟩 Experiment B: Impact of Specific Bottlenecks

1.  Change an intersection (`▩`) or a road (`▧`) to a building (`▣`).
2.  Observe how the disconnection of a specific segment alters the overall path selection.

#### 🟨 Experiment C: Optimizing Road-to-Building Ratio in Urban Reconstruction

  * Making roads too wide might actually **increase** the **Avg (Average Travel Time)**.
  * Quickly verify the optimal ratio using the HUD metrics.

## 📊 Output Metrics Explanation

The three main lines displayed on the HUD mean the following:

| Metric | Description |
| :----- | :---------- |
| **Avg** | The **average time** it took for moved vehicles to travel. |
| **S (Shortest)** | The theoretical **shortest path distance** based on BFS. |
| **E (Efficiency)** | Avg / S → **Lower** value indicates **higher efficiency**. |

-----

# 📈 Future Updates

  * Lane system with different speed limits
  * Traffic light-based stopping lines
  * Sectional traffic volume heatmap
  * Automatic comparison of multiple road scenarios (Auto Benchmark Mode)
  * GUI-based Map Editor

## 🤝 Contributing

Bug reports, feature requests, and Pull Requests (PRs) are all welcome\!
