import pygame
import heapq
import queue
import asyncio

# --- Pygame Window Setup ---
WIDTH = 800

# --- Colors ---
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  # Obstacle
PURPLE = (128, 0, 128)  # Path
ORANGE = (255, 165, 0)  # Start
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)  # End
BROWN = (165, 42, 42)  # Weight ("Mud")


# --- Core Logic: Node Class (from pathfinder.py) ---
class Node:
    """Represents each cell (or 'Spot') in the grid."""

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

        # Pathfinding properties
        self.g_score = float('inf')
        self.came_from = None
        self.weight = 1  # Default weight

    def get_pos(self):
        return self.row, self.col

    # --- Node Status Methods ---
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_obstacle(self):
        return self.color == BLACK

    def is_weight(self):
        return self.color == BROWN

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    # --- Node Mutator Methods ---
    def reset(self):
        self.color = WHITE
        self.g_score = float('inf')
        self.came_from = None
        self.weight = 1  # Reset weight

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_obstacle(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_weight(self, weight_val=10):
        self.color = BROWN
        self.weight = weight_val

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        """Populates the neighbors list, respecting obstacles."""
        self.neighbors = []
        total_cols = len(grid[self.row])
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < total_cols - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


# --- Core Logic: Algorithms (from pathfinder.py) ---

def reconstruct_path(came_from, current, draw):
    """Traces back from end node to start node and draws the path."""
    while current in came_from:
        current = came_from[current]
        if current.is_start():
            break
        current.make_path()
        draw()

def bfs_search(draw, grid, start, end):
    """Performs BFS and animates the process. Ignores weights."""
    q = queue.Queue()
    q.put(start)

    came_from = {}  # To reconstruct path
    visited = {start}  # A set to prevent re-processing

    while not q.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = q.get()

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()  # Ensure end node color persists
            start.make_start()  # Ensure start node color persists
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                came_from[neighbor] = current
                visited.add(neighbor)
                q.put(neighbor)
                neighbor.make_open()  # Show it's in the queue

        draw()

        if current != start:
            current.make_closed()  # Show it's been processed

    return False


def dijkstra_search(draw, grid, start, end):
    """Performs Dijkstra's and animates the process. Considers weights."""
    count = 0
    pq = []
    heapq.heappush(pq, (0, count, start))  # (g_score, count, node)

    came_from = {}

    # Reset g_scores for all nodes
    for row in grid:
        for node in row:
            node.g_score = float('inf')
    start.g_score = 0

    # Use a set for efficient checking of items in the PQ
    pq_hash = {start}

    while pq:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Get the node with the lowest g_score
        popped_g, _, current = heapq.heappop(pq)
        # Lazy-deletion: skip stale entries where a shorter path was already processed
        if popped_g > current.g_score:
            continue
        pq_hash.discard(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            # THIS IS THE KEY: neighbor.weight is the cost (e.g., 1 for grass, 10 for mud)
            new_g_score = current.g_score + neighbor.weight

            if new_g_score < neighbor.g_score:
                neighbor.g_score = new_g_score
                came_from[neighbor] = current
                # Always push; stale entries are discarded via lazy-deletion below
                count += 1
                heapq.heappush(pq, (new_g_score, count, neighbor))
                pq_hash.add(neighbor)
                neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


# --- GUI Helper Functions ---

def make_grid(rows, width):
    """Creates the 2D list of Node objects."""
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


def draw_grid_lines(win, rows, width):
    """Draws the grey grid lines."""
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    """Main drawing function, called every frame."""
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)  # Draw the node (colored square)

    draw_grid_lines(win, rows, width)  # Draw grid lines on top
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    """Converts mouse click (x,y) to grid (row,col)."""
    gap = width // rows
    x, y = pos  # pygame returns (x, y); x is horizontal (col), y is vertical (row)
    row = y // gap
    col = x // gap
    return row, col


# --- Main Program Loop ---

async def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("Pathfinding Visualizer (B=BFS, Space=Dijkstra, W+Click=Weight, C=Clear)")

    ROWS = 15
    grid = make_grid(ROWS, WIDTH)

    start_node = None
    end_node = None

    run = True
    started = False

    clock = pygame.time.Clock()

    while run:
        clock.tick(60)  # Cap FPS
        draw(win, grid, ROWS, WIDTH)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:  # Don't allow drawing while algorithm is running
                continue

            # --- Mouse Clicks ---
            # LEFT CLICK (0)
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]

                keys = pygame.key.get_pressed()  # Check which keys are held

                # Priority 1: Place Start Node
                if not start_node and node != end_node and not keys[pygame.K_w]:
                    start_node = node
                    start_node.make_start()

                # Priority 2: Place End Node
                elif not end_node and node != start_node and not keys[pygame.K_w]:
                    end_node = node
                    end_node.make_end()

                # Priority 3: Place Weight (if 'W' is held)
                elif keys[pygame.K_w] and node != start_node and node != end_node:
                    node.make_weight(10)  # Set weight to 10

                # Priority 4: Place Obstacle
                elif node != end_node and node != start_node:
                    node.make_obstacle()

            # RIGHT CLICK (2)
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]
                node.reset()  # This also resets the weight to 1
                if node == start_node:
                    start_node = None
                elif node == end_node:
                    end_node = None

            # --- Keyboard Presses ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_node and end_node:
                    started = True
                    # Update neighbors for all nodes right before search
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    # Run Dijkstra's
                    dijkstra_search(lambda: draw(win, grid, ROWS, WIDTH), grid, start_node, end_node)
                    started = False

                if event.key == pygame.K_b and start_node and end_node:
                    started = True
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    # Run BFS
                    bfs_search(lambda: draw(win, grid, ROWS, WIDTH), grid, start_node, end_node)
                    started = False

                if event.key == pygame.K_c:
                    # Clear grid
                    start_node = None
                    end_node = None
                    grid = make_grid(ROWS, WIDTH)

        await asyncio.sleep(0)  # Required for Pygbag web compatibility

    pygame.quit()


# --- Run the App ---
if __name__ == "__main__":
    asyncio.run(main())