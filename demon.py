import sys
import math
import pygame


# Just represents a single node where dist is the distance from the start
# (defaults to infiinity to designate it's been unvisited), prev is the node
# leading to this node, and is_wall is as it sounds.
class Node:
    dist = math.inf
    prev = None
    is_wall = False


SIZE = WIDTH, HEIGHT = 750, 750
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GRID_SIZE = 10
NODE_SIZE = WIDTH // GRID_SIZE
NUM_NODES = GRID_SIZE ** 2
BLOCKED = 9999

# Create a NxN grid of nodes where N is GRID_SIZE
nodes = [[Node() for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]

begin_search = False
last_move = 0
pause = 500  # Miliseconds to wait between demon moves
path = []
demon_node = 0

# Setup Pygame window
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Dijkstra's Demon")

# Demon!
demon = pygame.image.load('images/demon.png')
demon = pygame.transform.scale(demon, (NODE_SIZE, NODE_SIZE))
demon_grid_pos = (0, 0)
demon_screen_pos = (demon_grid_pos[0] * NODE_SIZE,
                    demon_grid_pos[1] * NODE_SIZE)

# Marshmallow!
marshmallow = pygame.image.load('images/marshmallow.png')
marshmallow = pygame.transform.scale(marshmallow, (NODE_SIZE, NODE_SIZE))
marshmallow_grid_pos = (GRID_SIZE // 2, GRID_SIZE // 2)
marshmallow_screen_pos = (marshmallow_grid_pos[0] * NODE_SIZE,
                          marshmallow_grid_pos[1] * NODE_SIZE)


def get_neighbors(coords):
    ''' Returns a list of all coordinates of neighbors of a node
    at the given coordinates '''
    neighbors = []

    # Essentially add the nodes above, below, and to the left and right
    # But need to check that we don't go out of bounds
    if coords[0] > 0:
        neighbors.append((coords[0] - 1, coords[1]))
    if coords[0] < GRID_SIZE - 1:
        neighbors.append((coords[0] + 1, coords[1]))
    if coords[1] > 0:
        neighbors.append((coords[0], coords[1] - 1))
    if coords[1] < GRID_SIZE - 1:
        neighbors.append((coords[0], coords[1] + 1))

    return neighbors


def find_closest(unvisited):
    ''' Finds the closet unvisited node (node with shortest distance
    from start node) '''
    closest = math.inf
    closest_node = None

    # Loop through all unvisited nodes looking for the one with least distance
    for coords in unvisited:
        node = nodes[coords[1]][coords[0]]
        if node.dist < closest:
            closest = node.dist
            closest_node = coords

    return closest_node


def get_path(start, end):
    ''' Returns a path as a list of coordinates from start to end '''
    path = []
    cur = end

    # We start at the end, and work our way back
    # by following the 'prev' field of the node
    while cur != start:
        path.append((cur[0], cur[1]))
        cur = nodes[cur[1]][cur[0]].prev

    # Finally return a reversed version of the list (since we started at end)
    return list(reversed(path))


def find_path(start, end):
    ''' Given start and end coordinates,
    finds the shortest path between them '''
    # Fill the unvisited list with all possible x, y pairs of nodes
    unvisited = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]

    # Start node is 0 distance away from itself
    nodes[start[1]][start[0]].dist = 0

    # Set current node to start node
    cur = start

    # Until we reach the end node, repeat the algorithm
    while cur != end:
        neighbors = get_neighbors(cur)

        # Investigate all neighbors
        for n in neighbors:
            node = nodes[n[1]][n[0]]

            # We are using a sort of "binary" weighted graph where the distance
            # between any two adjacent nodes is always 1, except if there is a
            # wall in which case the distance is just some large number
            # indicating that that path is inaccessible.
            dist = BLOCKED if node.is_wall else nodes[cur[1]][cur[0]].dist + 1

            # If we can reach the neighbor more quickly from here,
            # update the neighbor with the current node as it's previous
            # and the neighbor's distance from the start point
            if dist < node.dist:
                node.dist = dist
                node.prev = cur

        # Mark this node as visited
        unvisited.remove(cur)

        # Get the next closest node as our next start point
        cur = find_closest(unvisited)

    # We update the path variable with a list representing the shortest path
    global path
    path = get_path(start, end)


def draw_grid():
    ''' Draws lines to make up a grid '''
    for i in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (i * NODE_SIZE, 0),
                         (i * NODE_SIZE, HEIGHT))
        pygame.draw.line(screen, BLACK, (0, i * NODE_SIZE),
                         (WIDTH, i * NODE_SIZE))


def draw_nodes():
    ''' Draws the nodes (just a black rectangle if a wall, white otherwise) '''
    for i, row in enumerate(nodes):
        for j, node in enumerate(row):
            pygame.draw.rect(screen, BLACK if node.is_wall else WHITE,
                             pygame.Rect(j * NODE_SIZE, i * NODE_SIZE,
                                         NODE_SIZE, NODE_SIZE))


def flip_node(pos):
    ''' Changes a node to a wall and vice-versa '''
    col = pos[0] // NODE_SIZE
    row = pos[1] // NODE_SIZE

    nodes[row][col].is_wall = not nodes[row][col].is_wall


def handle_input():
    ''' Handles all input '''
    global begin_search

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif not begin_search and event.type == pygame.MOUSEBUTTONUP:
            flip_node(pygame.mouse.get_pos())
        elif (not begin_search and event.type == pygame.KEYUP
                and event.key == pygame.K_RETURN):
            begin_search = True
            find_path(demon_grid_pos, marshmallow_grid_pos)


def move_demon():
    ''' Moves the demon from its starting point to the marshamllow '''
    # Yuck globals I know...
    global last_move
    global demon_node
    global demon_grid_pos
    global demon_screen_pos
    global path

    # Move the demon to the next node in the path every 500ms or so
    now = pygame.time.get_ticks()
    if now - last_move >= pause:
        demon_grid_pos = (path[demon_node][0], path[demon_node][1])
        demon_screen_pos = (demon_grid_pos[0] * NODE_SIZE,
                            demon_grid_pos[1] * NODE_SIZE)
        last_move = now
        demon_node += 1


# Main loop
while 1:
    handle_input()
    screen.fill(WHITE)
    draw_nodes()
    draw_grid()
    screen.blit(demon, demon_screen_pos)
    screen.blit(marshmallow, marshmallow_screen_pos)

    # Start moving demon if user pressed enter key
    if begin_search and demon_node < len(path):
        move_demon()

    pygame.display.flip()
