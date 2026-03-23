import heapq
import queue
import sys


# --- Core Logic (Same as before) ---

class Node:
    """Represents each cell in the grid."""

    def __init__(self, row, col, is_obstacle=False):
        self.row = row
        self.col = col
        self.is_obstacle = is_obstacle
        self.weight = 1  # Default weight for Dijkstra's
        self.neighbors = []
        self.g_score = float('inf')  # Cost from start to this node
        self.came_from = None  # To reconstruct the path

    def __lt__(self, other):
        """For the priority queue (heapq)."""
        return self.g_score < other.g_score

    def __repr__(self):
        """String representation for printing."""
        return f"Node({self.row}, {self.col})"


def create_grid(rows, cols):
    """Creates a 2D list of Node objects."""
    grid = []
    for r in range(rows):
        grid.append([Node(r, c) for c in range(cols)])
    return grid


def add_neighbors(grid):
    """Populates the neighbors list for each node, respecting obstacles."""
    rows = len(grid)
    cols = len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c].is_obstacle:
                continue

            # Check 4 directions
            if r > 0 and not grid[r - 1][c].is_obstacle:  # UP
                grid[r][c].neighbors.append(grid[r - 1][c])
            if r < rows - 1 and not grid[r + 1][c].is_obstacle:  # DOWN
                grid[r][c].neighbors.append(grid[r + 1][c])
            if c > 0 and not grid[r][c - 1].is_obstacle:  # LEFT
                grid[r][c].neighbors.append(grid[r][c - 1])
            if c < cols - 1 and not grid[r][c + 1].is_obstacle:  # RIGHT
                grid[r][c].neighbors.append(grid[r][c + 1])


def reconstruct_path(end_node):
    """Traces back from the end node to the start node."""
    path = []
    current = end_node
    while current:
        path.append((current.row, current.col))
        current = current.came_from
    if not path:
        return None
    return path[::-1]  # Reverse the path to get start -> end


def reset_grid(grid):
    """Resets g_scores and came_from for a new search."""
    for row in grid:
        for node in row:
            node.g_score = float('inf')
            node.came_from = None


# --- Algorithm 1: Breadth-First Search (BFS) ---
def bfs_search(grid, start_node, end_node):
    reset_grid(grid)
    q = queue.Queue()

    start_node.g_score = 0
    q.put(start_node)

    visited = {start_node}  # A set to prevent re-processing

    while not q.empty():
        current = q.get()

        if current == end_node:
            return reconstruct_path(end_node), visited

        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.came_from = current
                neighbor.g_score = current.g_score + 1
                visited.add(neighbor)
                q.put(neighbor)

    return None, visited


# --- Algorithm 2: Dijkstra's Algorithm ---
def dijkstra_search(grid, start_node, end_node):
    reset_grid(grid)

    pq = []
    start_node.g_score = 0
    heapq.heappush(pq, (0, start_node))

    # Using a dictionary for visited to store g_score
    # This helps in the 'if new_g_score < neighbor.g_score' check
    visited = {start_node: 0}
    nodes_explored = 0

    while pq:
        current_g_score, current = heapq.heappop(pq)
        nodes_explored += 1

        if current == end_node:
            return reconstruct_path(end_node), nodes_explored

        # If we found a shorter path to this node earlier, skip
        if current_g_score > current.g_score:
            continue

        for neighbor in current.neighbors:
            new_g_score = current.g_score + neighbor.weight

            if new_g_score < neighbor.g_score:
                neighbor.g_score = new_g_score
                neighbor.came_from = current
                heapq.heappush(pq, (new_g_score, neighbor))
                visited[neighbor] = new_g_score

    return None, nodes_explored


# --- Helper functions for user input ---

def get_grid_dimensions():
    """Gets valid grid dimensions from the user."""
    while True:
        try:
            rows = int(input("Enter number of rows: "))
            cols = int(input("Enter number of columns: "))
            if rows > 0 and cols > 0:
                return rows, cols
            print("Rows and columns must be greater than 0.")
        except ValueError:
            print("Invalid input. Please enter numbers.")


def get_obstacles(grid, rows, cols):
    """Gets obstacle coordinates from the user."""
    print("\nEnter obstacles. Type 'row,col' (e.g., '2,3'). Type 'done' to finish.")
    while True:
        user_input = input("Obstacle at: ").strip().lower()
        if user_input == 'done':
            break
        try:
            row, col = map(int, user_input.split(','))
            if 0 <= row < rows and 0 <= col < cols:
                grid[row][col].is_obstacle = True
                print(f"Added obstacle at ({row},{col}).")
            else:
                print(f"Coordinates ({row},{col}) are out of bounds.")
        except ValueError:
            print("Invalid format. Please use 'row,col' or 'done'.")


def get_weights(grid, rows, cols):
    """Gets custom weights for cells from the user."""
    print("\nEnter weighted cells (e.g., 'mud'). Type 'row,col,weight' (e.g., '3,4,10'). Type 'done' to finish.")
    while True:
        user_input = input("Weight at: ").strip().lower()
        if user_input == 'done':
            break
        try:
            row, col, weight = map(int, user_input.split(','))
            if 0 <= row < rows and 0 <= col < cols:
                if grid[row][col].is_obstacle:
                    print(f"Cannot add weight to an obstacle at ({row},{col}).")
                elif weight > 0:
                    grid[row][col].weight = weight
                    print(f"Set weight at ({row},{col}) to {weight}.")
                else:
                    print("Weight must be positive.")
            else:
                print(f"Coordinates ({row},{col}) are out of bounds.")
        except ValueError:
            print("Invalid format. Please use 'row,col,weight' or 'done'.")


def get_start_end(grid, rows, cols):
    """Gets valid start and end nodes from the user."""
    while True:
        try:
            start_row, start_col = map(int, input("Enter start node (row,col): ").split(','))
            if 0 <= start_row < rows and 0 <= start_col < cols:
                if grid[start_row][start_col].is_obstacle:
                    print("Start node cannot be on an obstacle.")
                else:
                    start_node = grid[start_row][start_col]
                    break
            else:
                print(f"Coordinates ({start_row},{start_col}) are out of bounds.")
        except ValueError:
            print("Invalid format. Please use 'row,col'.")

    while True:
        try:
            end_row, end_col = map(int, input("Enter end node (row,col): ").split(','))
            if 0 <= end_row < rows and 0 <= end_col < cols:
                if grid[end_row][end_col].is_obstacle:
                    print("End node cannot be on an obstacle.")
                else:
                    end_node = grid[end_row][end_col]
                    break
            else:
                print(f"Coordinates ({end_row},{end_col}) are out of bounds.")
        except ValueError:
            print("Invalid format. Please use 'row,col'.")

    return start_node, end_node


def print_complexity(rows, cols):
    """Prints the time and space complexity analysis."""
    v = rows * cols  # V (Vertices) = Number of nodes
    # E (Edges) is roughly 4 * V in a grid, so O(E) is proportional to O(V)

    print("\n--- Complexity Analysis ---")
    print(f"Grid Size: {rows}x{cols}")
    print(f"V (Vertices/Nodes): {v}")
    print("Note: R = Rows, C = Columns, V = R * C")

    print("\n[Breadth-First Search (BFS)]")
    print("  - Time: O(V + E) which for a grid is O(V) or O(R * C)")
    print("    - Explanation: Visits each vertex and edge exactly once.")
    print("  - Space: O(V) or O(R * C)")
    print("    - Explanation: In the worst case, the queue and 'visited' set")
    print("      can store all vertices.")

    print("\n[Dijkstra's Algorithm (with Priority Queue)]")
    print("  - Time: O(E log V) or O((V + E) log V)")
    print("    - For a grid: O((R*C) log (R*C))")
    print("    - Explanation: Each edge is processed, and heap operations")
    print("      (push/pop) take O(log V) time.")
    print("  - Space: O(V + E) or O(R * C)")
    print("    - Explanation: Stores all vertices in the priority queue")
    print("      and 'visited' dictionary in the worst case.")
    print("---------------------------------")


# --- Main execution ---
def main():
    print("Welcome to the Pathfinding Algorithm Visualizer Logic")

    # 1. Get grid size
    rows, cols = get_grid_dimensions()
    grid = create_grid(rows, cols)

    # 2. Get obstacles
    get_obstacles(grid, rows, cols)

    # 3. Get weights
    get_weights(grid, rows, cols)

    # 4. Get Start and End
    start_node, end_node = get_start_end(grid, rows, cols)

    # 5. Build the graph connections
    add_neighbors(grid)

    # 6. Print complexity analysis
    print_complexity(rows, cols)

    # 7. Run BFS
    print("\n--- Running BFS ---")
    bfs_path, bfs_visited = bfs_search(grid, start_node, end_node)
    if bfs_path:
        print(f"BFS Path Found ({len(bfs_path)} steps):")
        print(bfs_path)
        print(f"Nodes visited: {len(bfs_visited)}")
    else:
        print("BFS: No path found.")

    # 8. Run Dijkstra's
    print("\n--- Running Dijkstra's ---")
    dijkstra_path, dijkstra_nodes = dijkstra_search(grid, start_node, end_node)
    if dijkstra_path:
        print(f"Dijkstra Path Found ({len(dijkstra_path)} steps, Cost: {end_node.g_score}):")
        print(dijkstra_path)
        print(f"Nodes explored (pops from pq): {dijkstra_nodes}")
    else:
        print("Dijkstra: No path found.")


if __name__ == "__main__":
    main()
