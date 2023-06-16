'''

pathfinder.py

Michael Grimsley
6/16/2023

Pathfinding Visualizer:
    Color-coded graph search visualizer on a customizable grid
    Implements Depth-First Search, Breadth-First Search, Greedy Best-First Search, and A*
    User Interface created with the pygame library

Wishlist:
- improve user interface
- resizable grid
- display algorithm stats
- upload/download grids

'''

import pygame
import sys

# Resolution
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

# Colors
WHITE = (255, 255, 255) # Grid Lines
GRAY = (200, 200, 200)  # 0 in GRID (Path)
BLACK = (0, 0, 0)       # 1 in GRID (Wall)
GREEN = (0, 255, 0)     # 2 in GRID (Start Tile)
RED = (255, 0, 0)       # 3 in GRID (End Tile)
BLUE = (0, 0, 255)      # 4 in GRID (Closed Tiles)
CYAN = (0, 255, 255)    # 5 in GRID (Open Tiles)
YELLOW = (255, 255, 0)  # 6 in GRID (Final Path)
COLORS = (GRAY, BLACK, GREEN, RED, BLUE, CYAN, YELLOW)

# Grid Dimensions
DEFAULT_TILE_SIZE = 20
TILE_SIZE = DEFAULT_TILE_SIZE # for resizing grid
GRID_WIDTH = WINDOW_HEIGHT // TILE_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // TILE_SIZE

class Node:
    '''
    A class to represent the Nodes used for traversing the GRID matrix
    
    Attributes
    ----------
    y: int
        y-coordinate of this Node within GRID
    x: int
        x-coordinate of this Node within GRID
    parent: Node
        Parent Node of this Node
    gCost: int
        The exact path length from this Node to the Start Node
    hCost: int
        The estimated path length from this Node to the End Node
    
    Methods
    -------
    getPos():
        Returns the x- and y-coordinates of this Node
    getNeighbors():
        Returns the Nodes adjacent to this Node
    fCost():
        Returns the f-cost of this Node
    '''
    
    def __init__(self, y, x, parent):
        '''
        Constructor to initialize the Node attributes
        
        g- and h-costs are set to 0
        
        Parameters
        ----------
        y: int
            y-coordinate of this Node within GRID
        x: int
            x-coordinate of this Node within GRID
        parent: Node
            Parent Node of this Node
        '''
        self.y = y
        self.x = x
        self.parent = parent
        
        self.gCost = 0
        self.hCost = 0
    
    def __eq__(self, node):
        '''
        Compares the x- and y-coordinates of this Node with the input Node
        
        Parameters
        ----------
        node: Node
            Node to compare this Node with
        
        Returns
        -------
        boolean:
            True if both nodes have the same x- and y-coordinates
        '''
        return isinstance(node, Node) and self.y == node.y and self.x == node.x
    
    def getPos(self):
        '''
        Returns the x- and y-coordinates of this Node
        
        Returns
        -------
        tuple:
            The ordered pair coordinates of this Node
        '''
        return self.y, self.x
    
    def getNeighbors(self):
        '''
        Returns the Nodes adjacent to this Node
        
        If diagonal movement is allowed, returns all 8 surrounding neighbors
        Otherwise, returns the 4 orthogonal neighbors
        
        Returns
        -------
        tuple:
            A collection of Nodes adjacent to this Node
        '''   
        up = Node(self.y - 1, self.x, self)
        right = Node(self.y, self.x + 1, self)
        down = Node(self.y + 1, self.x, self)
        left = Node(self.y, self.x - 1, self)
        
        if DIAGONAL:
            ur = Node(self.y - 1, self.x + 1, self)
            dr = Node(self.y + 1, self.x + 1, self)
            dl = Node(self.y + 1, self.x - 1, self)
            ul = Node(self.y - 1, self.x - 1, self)
            
            return up, right, down, left, ur, dr, dl, ul
        
        return up, right, down, left
    
    def fCost(self):
        '''
        Returns the f-cost of this Node
        
        The f-cost of a Node is the sum of its g-cost and h-cost
            g-cost: the exact path length from a Node to the Start Node
            h-cost: the estimated path length from a Node to the End Node
        
        Returns
        -------
        int:
            f-cost = g-cost + h-cost
        '''
        return self.gCost + self.hCost

class Button:
    '''
    A class to represent the Buttons in the User Interface
    
    Attributes
    ----------
    x: int
        x-coordinate of this Button within the window
    y: int
        y-coordinate of this Button within the window
    width: int
        Width of this Button
    height: int
        Height of this Button
    text: str
        Text to be displayed on this Button
    onClick: function
        Function to be called when this Button is clicked
    isArgument: boolean
        Flag for checking if this Button needs to be passed as an argument to the on click function
    isPressed: boolean
        Flag for checking if this Button is currently being pressed
    colors: dictionary
        Colors for the 3 states each Button can have
    
    Methods
    -------
    draw():
        Draws this Button on the screen
    '''
    
    def __init__(self, x, y, width, height, text, onClick, isArgument):
        '''
        Constructor to initialize the Button attributes
        
        Colors are defined for each state the Button can have
        
        Parameters
        ----------
        x: int
            x-coordinate of this Button within the window
        y: int
            y-coordinate of this Button within the window
        width: int
            Width of this Button
        height: int
            Height of this Button
        text: str
            Text to be displayed on this Button
        onClick: function
            Function to be called when this Button is clicked
        isAlgorithm: boolean
            Flag for checking if this Button needs to be passed as an argument to the on click function
        '''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.onClick = onClick
        self.isArgument = isArgument
        
        self.isPressed = False
        self.colors = {
            'default': '#000000',
            'hover': '#555555',
            'pressed': '#AAAAAA'
        }
        
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        font = pygame.font.SysFont(None, 20)
        self.contents = font.render(text, True, WHITE)
        
    def draw(self):
        '''
        Draws this Button on the screen
        
        The color of the Button will change according to its state
        The on click function will only be called once for each time the Button is clicked
        '''
        mousePos = pygame.mouse.get_pos()
        self.surface.fill(self.colors['default'])
        if self.rect.collidepoint(mousePos):
            self.surface.fill(self.colors['hover'])
            if pygame.mouse.get_pressed(num_buttons = 3)[0]:
                self.surface.fill(self.colors['pressed'])
                if not self.isPressed:
                    if self.isArgument:
                        self.onClick(self)
                    else:
                        self.onClick()
                    self.isPressed = True
            else:
                self.isPressed = False
        
        self.surface.blit(self.contents, [
            self.rect.width / 2 - self.contents.get_rect().width / 2,
            self.rect.height / 2 - self.contents.get_rect().height / 2,
        ])
        SCREEN.blit(self.surface, self.rect)
    
def main():
    # global variables
    global SCREEN, GRID, START, END, ALGORITHM, DIAGONAL
    global open, closed, searching
    
    START = None
    END = None
    open = []
    closed = []
    
    # pygame setup
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Pathfinding Visualizer')
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)
    
    # default grid setup
    GRID = [[0 for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
    for x in range(GRID_WIDTH):
        GRID[0][x] = 1
        GRID[GRID_HEIGHT - 1][x] = 1
    for y in range(GRID_HEIGHT):
        GRID[y][0] = 1
        GRID[y][GRID_WIDTH - 1] = 1
    START = setStart(1, 1)
    END = setEnd(GRID_WIDTH - 2, GRID_HEIGHT - 2)
    
    # search variables
    ALGORITHM = AStar # default algorithm
    DIAGONAL = True
    searching = False
    
    # mouse event variables
    drag = False
    clickType = None
    
    buttons = [
        Button(625, 200, 100, 50, 'DFS', selectAlgorithm, True),
        Button(775, 200, 100, 50, 'BFS', selectAlgorithm, True),
        Button(625, 275, 100, 50, 'Greedy BFS', selectAlgorithm, True),
        Button(775, 275, 100, 50, 'A*', selectAlgorithm, True),
        Button(625, 350, 250, 50, 'Toggle Diagonal Movement (D Key)', toggleDiagonal, False),
        Button(625, 450, 100, 50, 'Reset (R Key)', reset, False),
        Button(775, 450, 100, 50, 'Clear (C Key)', clear, False),
        Button(625, 525, 250, 50, 'Begin Search (SPACE Key)', start, False)
    ]
    
    TICK = 100
    
    # game loop
    while True:
        drawGrid()
        drawLegend()
        for button in buttons:
            button.draw()
        
        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                keyHandler(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                drag = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clickType = event.button
                mouseHandler(event, clickType)
                drag = True
            elif event.type == pygame.MOUSEMOTION and drag:
                mouseHandler(event, clickType)
        
        if searching:
            found = ALGORITHM()
            if found == False:
                searching = False
            elif found == True:
                reconstructPath()
                searching = False
        
        pygame.display.update()
        CLOCK.tick(TICK)

##############################
#      Helper Functions      #
##############################

def drawGrid():
    '''
    Draws a grid with dimensions GRID_WIDTH x GRID_HEIGHT and colors each tile according to the corresponding values in the GRID matrix
    Grid lines are colored white and the size of the grid tiles are determined by TILE_SIZE
    '''
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(SCREEN, COLORS[GRID[y][x]], rect)
            pygame.draw.rect(SCREEN, WHITE, rect, 1)

def drawLegend():
    ''' Draws a legend that explains what the color of each tile in the grid represents '''
    font = pygame.font.SysFont(None, 30)
    legend = ["= Path (Right Click)", "= Wall (Left Click)", "= Start (S Key)", "= End (E Key)", "= Available Paths", "= Visited", "= Final Path"]
    
    space = 5
    
    x, y = 600 + space, 0 + space
    for i in range(len(legend)):
        rect = pygame.Rect(x, y, DEFAULT_TILE_SIZE, DEFAULT_TILE_SIZE)
        pygame.draw.rect(SCREEN, COLORS[i], rect)
        pygame.draw.rect(SCREEN, BLACK, rect, 1)
        
        text = font.render(legend[i], True, BLACK)
        SCREEN.blit(text, (x + DEFAULT_TILE_SIZE + space, y))
        
        y += DEFAULT_TILE_SIZE + space

def keyHandler(event):
    '''
    Handles KEYDOWN events
    
    Program Keybinds:
        R = Stop searching and/or clear search results
        D = Switch between allowing adjacent movement and orthogonal movement
        C = Stop searching and/or clear the walls and search results
        
        (The following keys can only be pressed while the program is not searching)
        
        SPACE = begin searching for a path from the Start Node to the End Node
        S = Move the Start Node to the hovered tile
        E = Move the End Node to the hovered tile
        
    Parameters
    ----------
    event: Event
        KEYDOWN event
    '''
    global START, END

    if event.key == pygame.K_r:
        reset()
    elif event.key == pygame.K_d:
        toggleDiagonal()
    elif event.key == pygame.K_c:
        clear()
    else:
        if not searching:
            if event.key == pygame.K_SPACE:
                start()
            elif event.key == pygame.K_s:
                xPos, yPos = pygame.mouse.get_pos()
                y, x = getCoordsFromPosition(xPos, yPos)
                if inGrid(x, y) and (y, x) != END.getPos():
                    START = setStart(x, y)
            elif event.key == pygame.K_e:
                xPos, yPos = pygame.mouse.get_pos()
                y, x = getCoordsFromPosition(xPos, yPos)
                if inGrid(x, y) and (y, x) != START.getPos():
                    END = setEnd(x, y)

def mouseHandler(event, clickType):
    '''
    Handles MOUSEBUTTONDOWN and MOUSEMOTION events in the GRID
    
    Left Clicking converts the hovered tile into a wall
    Right Clicking converts the hovered tile into a path
    Clicking and dragging also converts tiles accordingly
    
    Parameters
    ----------
    event: Event
        MOUSEBUTTONDOWN or MOUSEMOTION event
    clickType: int
        Number representing which mouse button has been clicked
    '''
    xPos, yPos = event.pos
    y, x = getCoordsFromPosition(xPos, yPos)
    if inGrid(x, y) and GRID[y][x] in [0, 1]:
        if clickType == 1: # left click
            GRID[y][x] = 1
        elif clickType == 3: # right click
            GRID[y][x] = 0

def setStart(x, y):
    '''  
    Set the coordinates of the Start Node
    
    If a Start Node already exists, change that tile to a path first
    
    Parameters
    ----------
    x: int
        x-coordinate for the new Start Node
    y: int
        y-coordinate for the new Start Node
        
    Returns
    -------
    Node
        Start Node object initialized with new x- and y-coordinates
    '''    
    if START:
        GRID[START.y][START.x] = 0
    GRID[y][x] = 2
    return Node(y, x, None)

def setEnd(x, y):
    '''  
    Set the coordinates of the End Node
    
    If a End Node already exists, change that tile to a path first
    
    Parameters
    ----------
    x: int
        x-coordinate for the new End Node
    y: int
        y-coordinate for the new End Node
        
    Returns
    -------
    Node
        End Node object initialized with new x- and y-coordinates
    '''   
    if END:
        GRID[END.y][END.x] = 0
    GRID[y][x] = 3
    return Node(y, x, None)

def toggleDiagonal():
    ''' Switch between allowing adjacent movement and orthogonal movement '''
    global DIAGONAL
    
    if not searching:
        DIAGONAL = not DIAGONAL

def selectAlgorithm(button):
    '''
    Selects the Algorithm to traverse the GRID matrix with and begins searching
    
    Parameters
    ----------
    button: Button
        Algorithm Button that was clicked
    '''
    global ALGORITHM
    
    if not searching:
        if button.text == 'DFS':
            ALGORITHM = DFS
        elif button.text == 'BFS':
            ALGORITHM = BFS
        elif button.text == 'Greedy BFS':
            ALGORITHM = Greedy
        elif button.text == 'A*':
            ALGORITHM = AStar
        start()

def inGrid(x, y):
    '''
    Checks if the tile at coordinates (x, y) is within the GRID matrix
    
    Parameters
    ----------
    x: int
        x-coordinate
    y: int
        y-coordinate
    
    Returns
    -------
    boolean
        True if the ordered pair (x, y) defines a tile within the grid
    '''
    return (x > 0 and x < GRID_WIDTH - 1) and (y > 0 and y < GRID_HEIGHT - 1)

def isPath(node):
    '''
    Checks if the tile in the GRID matrix defined by the input Node is a path
    
    Parameters
    ----------
    node: Node
        Node object to be evaluated
    
    Returns
    -------
    boolean
        True if the tile defined by the input Node has a value that is not equal to 1
    '''
    return GRID[node.y][node.x] != 1

def getCoordsFromPosition(xPos, yPos):
    '''
    Returns the coordinates of the tile within the GRID matrix that is at (xPos, yPos) in the window
    
    Parameters
    ----------
    xPos: int
        x-coordinate within the SCREEN window
    yPos: int
        y-coordinate within the SCREEN window
    
    Returns
    -------
    tuple
        The matrix coordinates of the tile at (xPos, yPos) in the window
    '''
    return yPos // TILE_SIZE, xPos // TILE_SIZE
    
def HCost(node):
    '''
    Returns the h-cost of the input Node
    
    The h-cost of a Node is the estimated path length from that Node to the End Node
    If diagonal movement is allowed, the h-cost is the Diagonal Distance between the two Nodes
        max(dy, dx)
    Otherwise, the h-cost is the Manhattan Distance between the two Nodes
        dy + dx
    
    Parameters
    ----------
    node: Node
        Node to be evaluated
    
    Returns
    -------
    int
        h-cost
    '''
    dy = abs(END.y - node.y)
    dx = abs(END.x - node.x)
    if DIAGONAL:
        return max(dy, dx)
    else:
        return dy + dx

def reconstructPath():
    ''' Creates the path from the Start Node to the End Node found by the current algorithm '''
    curr = closed.pop()
    parent = curr.parent
    
    while parent != None:
        GRID[curr.y][curr.x] = 6
        for node in closed:
            if parent == node:
                curr, parent = node, node.parent
                break
    
    GRID[START.y][START.x] = 2
    GRID[END.y][END.x] = 3

def clear():
    ''' Clears any custom walls and previous search results then stops searching '''
    global searching
    
    for x in range(1, GRID_WIDTH - 1):
        for y in range(1, GRID_HEIGHT - 1):
            GRID[y][x] = 0
    
    GRID[START.y][START.x] = 2
    GRID[END.y][END.x] = 3
    
    searching = False

def reset():
    ''' Clears any previous search results then stops searching '''
    global searching
    
    open.clear()
    open.append(START)
    closed.clear()
    
    for x in range(1, GRID_WIDTH - 1):
        for y in range(1, GRID_HEIGHT - 1):
            if GRID[y][x] in [4, 5, 6]:
                GRID[y][x] = 0
    
    GRID[START.y][START.x] = 2
    GRID[END.y][END.x] = 3
    
    searching = False
    
def start():
    ''' Clears any previous search results then begins searching '''
    global searching
    
    open.clear()
    open.append(START)
    closed.clear()
    
    for x in range(1, GRID_WIDTH - 1):
        for y in range(1, GRID_HEIGHT - 1):
            if GRID[y][x] in [4, 5, 6]:
                GRID[y][x] = 0
    
    GRID[START.y][START.x] = 2
    GRID[END.y][END.x] = 3
    
    searching = True

##############################
#         Algorithms         #
##############################

# Algorithm Explanation:
# 
# The open list will initially contain just the Start Node
# 
# If the open list is empty, return False
# - path from Start Node to End Node does not exist
# 
# Get next Node from open list
# - DFS: LIFO
# - BFS: FIFO
# - Greedy BFS: lowest h-cost
# - A*: lowest f-cost
# 
# If that Node is the End Node, return True
# - a path has been found and can be reconstructed
# 
# Otherwise, add that Node's available and unvisited neighbors to the open list
# - Greedy BFS: calculate each neighbor's h-cost
# - A*: calculate each neighbor's g-cost and h-cost
#       If the neighbor is already in the open list, compare g-costs to check if this path to that neighbor is better
#       If the new neighbor has a lower g-cost, replace the old neighbor with the new one
# 
# Repeat

def DFS():
    ''' Searches as far as possible along each path before backtracking '''
    if not open:
        return False
    
    curr = open.pop()
    closed.append(curr)
    GRID[curr.y][curr.x] = 5
    
    if curr == END:
        return True
    
    neighbors = curr.getNeighbors()
    
    for neighbor in neighbors:
        if isPath(neighbor) and neighbor not in closed and neighbor not in open:
            open.append(neighbor)
            GRID[neighbor.y][neighbor.x] = 4

def BFS():
    ''' Searches by shortest distance from the Start Node '''
    if not open:
        return False
    
    curr = open.pop(0)
    closed.append(curr)
    GRID[curr.y][curr.x] = 5
    
    if curr == END:
        return True
    
    neighbors = curr.getNeighbors()
    
    for neighbor in neighbors:
        if isPath(neighbor) and neighbor not in closed and neighbor not in open:
            open.append(neighbor)
            GRID[neighbor.y][neighbor.x] = 4

def Greedy():
    ''' Searches by lowest h-cost '''
    if not open:
        return False
    
    open.sort(key = lambda node: node.hCost)
    
    curr = open.pop(0)
    closed.append(curr)
    GRID[curr.y][curr.x] = 5
    
    if curr == END:
        return True
    
    neighbors = curr.getNeighbors()
    
    for neighbor in neighbors:
        if isPath(neighbor) and neighbor not in closed and neighbor not in open:
            neighbor.hCost = HCost(neighbor)
            open.append(neighbor)
            GRID[neighbor.y][neighbor.x] = 4

def AStar():
    ''' Searches by lowest f-cost '''
    if not open:
        return False
    
    open.sort(key = lambda node: node.fCost())
    
    curr = open.pop(0)
    closed.append(curr)
    GRID[curr.y][curr.x] = 5
    
    if curr == END:
        return True
    
    neighbors = curr.getNeighbors()
    
    for neighbor in neighbors:
        if isPath(neighbor) and neighbor not in closed:
            neighbor.gCost = curr.gCost + 1
            neighbor.hCost = HCost(neighbor)
            if neighbor in open:
                for i in range(len(open)):
                    if open[i] == neighbor and neighbor.gCost < open[i].gCost:
                        open[i] = neighbor
            else:
                open.append(neighbor)
                GRID[neighbor.y][neighbor.x] = 4

if __name__ == "__main__":
    main()
