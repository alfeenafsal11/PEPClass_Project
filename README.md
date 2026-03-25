# 🗺️ Interactive Pathfinding Algorithm Visualizer

An interactive visualizer built with **Pygame** that demonstrates two classic pathfinding algorithms — **BFS** (Breadth-First Search) and **Dijkstra's Algorithm** — on a dynamic grid. Play it live in the browser or run locally.

---

## 🚀 Live Demo

> **[▶ Play in Browser](https://alfeenafsal11.github.io/PEPClass_Project/)**
> *(Powered by Pygbag — no install needed)*

---

## 🎮 Controls

| Action | Control |
|---|---|
| Place **Start** node | Left-click (first click) |
| Place **End** node | Left-click (second click) |
| Draw **Obstacle** | Left-click (drag) |
| Draw **Weighted** cell (cost ×10) | Hold `W` + Left-click |
| Remove / Reset a cell | Right-click |
| Run **Dijkstra's** (weight-aware) | `Space` |
| Run **BFS** (unweighted shortest) | `B` |
| **Clear** the grid | `C` |

---

## 🧠 Algorithms

### Breadth-First Search (BFS)
- Explores all neighbors level by level.
- Guarantees the **shortest path by steps** on an unweighted grid.
- Time: `O(V + E)` — Space: `O(V)`

### Dijkstra's Algorithm
- Uses a priority queue to always expand the lowest-cost node.
- Respects **weighted cells** (mud = cost 10, normal = cost 1).
- Guarantees the **lowest-cost path** on a weighted grid.
- Time: `O((V + E) log V)` — Space: `O(V)`

---

## 🛠️ Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the visualizer
python main.py
```

---

## 🌐 Build for Web (Pygbag)

```bash
python -m pygbag --build main.py
```

Output goes to `web-build/`. Deploy the contents to GitHub Pages (see below).

---

## 📦 Project Structure

```
PEPClass_Project/
├── main.py         # Pygame GUI with BFS + Dijkstra visualisation
├── cli.py          # CLI version (terminal-based, no GUI)
├── requirements.txt
└── README.md
```

---

## 🏗️ Tech Stack
- **Python 3.x**
- **Pygame** — rendering & event loop
- **Pygbag** — WebAssembly build for browser deployment
