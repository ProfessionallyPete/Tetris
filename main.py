#from warnings import showwarning
import pygame
import random
 
"""
game grid is 10 wide by 20 tall 
shapes are: S, Z, I, O, J, L, T
shapes are indexed 0 to 6: 0=S, 1=Z...
"""
 
pygame.font.init()
 
# GLOBALS
s_width = 800   # screen size - room for next shape
s_height = 700
play_width = 300  # 30 width per block * 10 blocks wide
play_height = 600  # 30 height per block * 20 blocks tall
block_size = 30
 
top_left_x = (s_width - play_width) // 2  # reference point for top left of play area.
top_left_y = s_height - play_height
 
 
# DEFINE SHAPE FORMATS FOR EACH LETTER/ROTATION
 
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]
 
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]
 
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]
 
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]
 
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]
 
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]
 
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]
 
shapes = [S, Z, I, O, J, L, T]
shape_colours = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index from 0 to 6 to get the shape you want.
 
 
class Piece(object):
    rows = 20
    columns = 10

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.colour = shape_colours[shapes.index(shape)]
        self.rotation = 0  #default orientation at birth of shape. increment later to rotate.
 
def create_grid(filled_locations={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]    #a 10 wide by 20 deep matrix of (0,0,0)

    for i in range (len(grid)):     #this nested loop checks for grid locations filled by pieces that are no longer moving
        for j in range (len(grid[i])):
            if (j, i) in filled_locations:
                c = filled_locations[(j,i)]
                grid[i][j] = c
    return grid
 
def convert_shape_format(shape):
    positions=[]
    format = shape.shape[shape.rotation % len(shape.shape)]     #get the nth element of the shape, depending on rotation count.

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x+j, shape.y+i))
    
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)     #offset left and up
    
    return positions
 
def valid_space(shape, grid):
    accepted_pos=[[(j,i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]       #a position is acceptable if it is in the 10 by 20 grid and not coloured.
    accepted_pos = [j for sub in accepted_pos for j in sub]     #flatten accepted_pos into 1D list

    formatted_shape = convert_shape_format(shape)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1]>-1:
                return False
    return True
 
def check_lost(positions):
    for pos in positions:
        x,y = pos
        if y<1:         # if your block is off the top edge of the screen.
            return True
    return False
 
def get_shape():        #picks the next shape to birth.
    global shapes, shape_colours
    return Piece(5,0,random.choice(shapes))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))

def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*block_size), (sx + play_width, sy + i * block_size))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))  # vertical lines

def clear_rows(grid, filled_locations):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:      #if your row has no black squares then it's filled
            inc+=1
            ind = i
            for j in range(len(row)):
                try:
                    del filled_locations[(j,i)]     #delete the filled row
                except:
                    continue
    
    if inc>0:           #now move all the rows above down one row
        for key in sorted(list(filled_locations), key = lambda x: x[1])[::-1]:
            x,y = key
            if y<ind:
                newKey = (x,y+inc)
                filled_locations[newKey] = filled_locations.pop(key)

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape:',1,(255,255,255))

    sx=top_left_x+play_width + 50       #set location of next shape box
    sy=top_left_y+play_height/2 - 100
    format = shape.shape[shape.rotation%len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.colour, (sx +j*block_size, sy+i*block_size, block_size,block_size),0)
    
    surface.blit(label,(sx+10, sy-30))

def draw_window(surface):
    surface.fill((0,0,0))
    # Tetris Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255,255,255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* block_size, top_left_y + i * block_size, block_size, block_size), 0)

	
    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    # pygame.display.update()
 
def main(win):
    global grid
    filled_locations={}     #format: (xpos, ypos):(R,G,B)
    grid=create_grid(filled_locations)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0

    while run:      #the game loop
        fall_speed = 0.27
        grid = create_grid(filled_locations)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000>=fall_speed:
            fall_time = 0
            current_piece.y +=1
            if not (valid_space(current_piece,grid)) and current_piece.y>0:      #if the piece has rested on another piece or the bottom of screen
                current_piece.y -= 1
                change_piece = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece,grid)):        #if you've made an illegal move, then you're sent back.
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece,grid)):        #if you've made an illegal move, then you're sent back.
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece,grid)):        #if you've made an illegal move, then you're sent back.
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece,grid)):        #if you've made an illegal move, then you're sent back.
                        current_piece.rotation -= 1
        
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x,y = shape_pos[i]
            if y>-1:    #if you're not off the screen
                grid[y][x] = current_piece.colour
        
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                filled_locations[p] = current_piece.colour
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            clear_rows(grid, filled_locations)
                
        
        draw_window(win)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        if check_lost(filled_locations):
            run = False
    draw_text_middle("You Lost", 40, (255,255,255), win)
    pygame.display.update()
    pygame.time.delay(2000)

def main_menu():
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle('Press any key to begin.', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

main_menu()  # start game