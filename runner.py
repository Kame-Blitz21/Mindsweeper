import pygame
import sys
import time
import copy

from minesweeper import Minesweeper, MinesweeperAI

#*************************************************************************************************************************************************************************

# Originally all 8
HEIGHT = 16
WIDTH = 16
MINES = 48

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Adobe color
A = 214, 125, 255
B = 255, 209, 176
C = 134, 255, 28
D = 222, 255, 122
E = 135, 245, 255

# Create game
pygame.init()
pygame.display.set_caption("Mindsweeper")
size = width, height = 900, 600 # Originally 600, 400
screen = pygame.display.set_mode(size)
game = None

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 50)
ccc = 0 #Colour Change Counting

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
asset_flag = pygame.image.load("assets/images/flag.png")
#asset_mine = pygame.image.load("assets/images/mine.png")

# Set icon
asset_icon = pygame.image.load("assets/images/icon.jpg")
pygame.display.set_icon(asset_icon)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False
won = False

# Check for the first move
first_move = True

# Check whether or not a safe board has been found
found = False

# Show instructions initially
instructions = True
show_instructions = False
choose_difficulty = False
main_menu = True

#*************************************************************************************************************************************************************************

# Button class
class Button:
    def __init__(self, height_offset, text, on_click_func):
        self.disabled = False

        self.on_click_func = on_click_func

        self.x = width / 4
        self.y = 0.5 * height + height_offset
        self.width = width / 2
        self.height = 50

        self.text = text
        self.text_color = BLACK
        self.button_color = C

        self.rect = None

    def new_func(self, new_func):
        self.on_click_func = new_func

    def check_everything(self):
        if self.disabled:
            return

        self.draw()
        self.display_text()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        click, _, _ = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_x, mouse_y):

            self.button_color = D

            if click == 1:
                self.on_click_func()

        else:
            self.button_color = C

    def display_text(self):
        buttonText = mediumFont.render(self.text, True, self.text_color)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = self.rect.center

        screen.blit(buttonText, buttonTextRect)

    def draw(self):
        if not self.disabled:
            self.rect = pygame.draw.rect(screen, self.button_color, (self.x, self.y, self.width, self.height))

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

# Clear function, called only when the number on square_position is 0
def clear(square_position):
    clearings = set()
    tiles = set()
    checked_tiles = set()
    clears = set()
    
    # Add the cell itself
    clearings.add(square_position)
    tiles.add(square_position)
    clears.add(square_position)
    
    while tiles:
        new_tiles = set()
        for tile in tiles:
            for i, j in [(x, y) for x in range(tile[0]-1, tile[0]+2) for y in range(tile[1]-1, tile[1]+2) if 0 <= x < HEIGHT and 0 <= y < WIDTH]:
                    
                # Ignore the cell itself
                if (i, j) == square_position or (i, j) in revealed or (i, j) in checked_tiles:
                    continue

                # Add the empty squares to the queue
                if game.nearby_mines((i, j)) == 0:
                    new_tiles.add((i, j))
                    clears.add((i, j))
                    
        checked_tiles = tiles.copy()
        tiles = new_tiles.copy()
    for clear_tile in clears:
        clearings.add(clear_tile)
        for i, j in [(x, y) for x in range(clear_tile[0]-1, clear_tile[0]+2) for y in range(clear_tile[1]-1, clear_tile[1]+2) if 0 <= x < HEIGHT and 0 <= y < WIDTH]:
            if (i, j) not in clears or game.nearby_mines((i, j)) != 0:
                clearings.add((i, j))
    return clearings

# Returns the amount of nearby flags
def nearby_flags(square):
    n_flags = 0
    for i, j in [(x, y) for x in range(square[0]-1, square[0]+2) for y in range(square[1]-1, square[1]+2) if 0 <= x < HEIGHT and 0 <= y < WIDTH]:
        if (i, j) in flags:
            n_flags += 1
    return n_flags

#*************************************************************************************************************************************************************************

# Helper functions
def on_click():
    global instructions
    global choose_difficulty
    global main_menu

    instructions = False
    choose_difficulty = True
    main_menu = False

    time.sleep(0.3)

def quit_game():
    pygame.quit()
    quit()

def go_back():
    time.sleep(0.3)

    global show_instructions
    global main_menu

    play_button.enable()
    quit_button.enable()
    rules_button.enable()

    rules_button.new_func(rules_page)
    rules_button.text = "Rules"
    rules_button.y = 0.5 * height + 75
    show_instructions = False
    main_menu = True

def rules_page():
    time.sleep(0.3)

    global show_instructions
    global main_menu

    play_button.disable()
    quit_button.disable()
    
    rules_button.text = "Back"
    rules_button.y = 0.5 * height + 200
    show_instructions = True
    main_menu = False
    rules_button.new_func(go_back)

# Main menu buttons
play_button = Button(0, "Play Game", on_click)
quit_button = Button(150, "Quit", quit_game)
rules_button = Button(75, "Rules", rules_page)

#*************************************************************************************************************************************************************************

# Difficulty selection functions
def diff_easy():
    global HEIGHT
    global WIDTH
    global MINES
    global ai
    global choose_difficulty
    global cell_size
    global flag
    global mine
    global gameFont
    global difficulty_level
    global fmove

    HEIGHT = 8
    WIDTH = 8
    MINES = 8
    choose_difficulty = False

    cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))

    flag = pygame.transform.scale(asset_flag, (cell_size, cell_size))
    #mine = pygame.transform.scale(asset_mine, (cell_size, cell_size))
    mine = pygame.image.load("assets/images/mine_easy.png")

    difficulty_level = 1

    ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
    gameFont = pygame.font.Font(OPEN_SANS, 40)

    fmove = None

    time.sleep(0.3)

def diff_medium():
    global HEIGHT
    global WIDTH
    global MINES
    global ai
    global choose_difficulty
    global cell_size
    global flag
    global mine
    global gameFont
    global difficulty_level
    global fmove

    HEIGHT = 12
    WIDTH = 12
    MINES = 24
    choose_difficulty = False

    cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))

    flag = pygame.transform.scale(asset_flag, (cell_size, cell_size))
    #mine = pygame.transform.scale(asset_mine, (cell_size, cell_size))
    mine = pygame.image.load("assets/images/mine_medium.png")

    difficulty_level = 2

    ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
    gameFont = pygame.font.Font(OPEN_SANS, 30)

    fmove = None

    time.sleep(0.3)

def diff_hard():
    global HEIGHT
    global WIDTH
    global MINES
    global ai
    global choose_difficulty
    global cell_size
    global flag
    global mine
    global gameFont
    global difficulty_level
    global fmove

    HEIGHT = 16
    WIDTH = 16
    MINES = 48
    choose_difficulty = False

    cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))

    flag = pygame.transform.scale(asset_flag, (cell_size, cell_size))
    #mine = pygame.transform.scale(asset_mine, (cell_size, cell_size))
    mine = pygame.image.load("assets/images/mine_hard.png")
    
    difficulty_level = 3

    ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
    gameFont = pygame.font.Font(OPEN_SANS, 20)

    fmove = None
    
    time.sleep(0.3)

# Back to main menu
def diff_back():
    global choose_difficulty
    global instructions
    global main_menu

    instructions = True
    choose_difficulty = False
    main_menu = True
    
    time.sleep(0.3)

easy_button = Button(-75, "Easy", diff_easy)
medium_button = Button(0, "Medium", diff_medium)
hard_button = Button(75, "Hard", diff_hard)
diff_back_button = Button(150, "Back", diff_back)

#*************************************************************************************************************************************************************************

# Actual game runner
while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        #elif event.type == pygame.VIDEORESIZE:
            #size = width, height = event.w, event.h
            #screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    screen.fill(A)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Mindsweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        if ccc == 0:
            ccu = True
            changed_colour = E
        elif ccc == 200:
            ccu = False
            changed_colour = D

        if ccu == True:
            ccc += 1
        elif ccu == False:
            ccc -= 1
            
        title = mediumFont.render("A smarter version of Minesweeper!", True, changed_colour)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 100)
        screen.blit(title, titleRect)
        
        if main_menu:
            title = smallFont.render("Made by I play Minecraft#4015, Kame Blitz#0438, RedDragonNM#8729 and SecretSpectre#5909", True, B)
            titleRect = title.get_rect()
            titleRect.center = ((width / 2), 580)
            screen.blit(title, titleRect)

        if show_instructions:
            # Rules
            rules = [
                "Click a cell to reveal it",
                "Right-click a cell to mark it as a mine",
                "Right-click on a revealed cell to dig up all nearby cells if all nearby mines are flagged",
                "Mark all mines successfully to win!",
                "",
                "",
                "The AI Move button is there to get you out of a tricky situation",
                "The New Game button generates a new mine field",
                "The Reset button allows you to restart your game on the same mine field"       
            ]
            for i, rule in enumerate(rules):
                line = smallFont.render(rule, True, (255, 221, 128))
                lineRect = line.get_rect()
                lineRect.center = ((width / 2), 200 + 30 * i)
                screen.blit(line, lineRect)

        play_button.check_everything()
        quit_button.check_everything()
        rules_button.check_everything()

        pygame.display.update()
        continue

    if choose_difficulty:
        
        title = largeFont.render("Select the difficulty", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 100)
        screen.blit(title, titleRect)
        
        easy_button.check_everything()
        medium_button.check_everything()
        hard_button.check_everything()

        diff_back_button.check_everything()

        game = None
        fmove = None
        #won = False

        pygame.display.update()
        continue

    #######################################################################################################################################################

    if first_move == True or found == True:
        # Draw board
        cells = []
        for i in range(HEIGHT):
            row = []
            for j in range(WIDTH):

                # Draw rectangle for cell
                rect = pygame.Rect(
                    board_origin[0] + j * cell_size,
                    board_origin[1] + i * cell_size,
                    cell_size, cell_size
                )
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, WHITE, rect, int(height * width / 1000) // (HEIGHT * WIDTH))

                if not first_move:

                    # Add a mine, flag, or number if needed
                    if game.is_mine((i, j)) and lost:
                        screen.blit(mine, rect)
                    elif (i, j) in flags:
                        screen.blit(flag, rect)
                    elif (i, j) in revealed:
                        neighbors = gameFont.render(
                            str(game.nearby_mines((i, j))),
                            True, BLACK
                        )
                        neighborsTextRect = neighbors.get_rect()
                        neighborsTextRect.center = rect.center
                        screen.blit(neighbors, neighborsTextRect)

                row.append(rect)
            cells.append(row)

        # AI Move button
        aiButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
            (width / 3) - BOARD_PADDING * 2, 50
        )
        buttonText = mediumFont.render("AI Move", True, BLACK)
        buttonRect = buttonText.get_rect()
        buttonRect.center = aiButton.center

        if not won and not lost:
            if aiButton.collidepoint(pygame.mouse.get_pos()):
                color_ai = D
            else:
                color_ai = C
        else:
            color_ai = GRAY

        pygame.draw.rect(screen, color_ai, aiButton)
        screen.blit(buttonText, buttonRect)

        # New Game button
        ngButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
            (width / 3) - BOARD_PADDING * 2, 50
        )
        buttonText = mediumFont.render("New Game", True, BLACK)
        buttonRect = buttonText.get_rect()
        buttonRect.center = ngButton.center

        if game:
            if ngButton.collidepoint(pygame.mouse.get_pos()):
                color_ng = D
            else:
                color_ng = C
        else:
            color_ng = GRAY

        pygame.draw.rect(screen, color_ng, ngButton)
        screen.blit(buttonText, buttonRect)

        # Reset Button
        resetButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 90,
            (width / 3) - BOARD_PADDING * 2, 50
        )
        buttonText = mediumFont.render("Reset", True, BLACK)
        buttonRect = buttonText.get_rect()
        buttonRect.center = resetButton.center

        if fmove:
            if resetButton.collidepoint(pygame.mouse.get_pos()):
                color_reset = D
            else:
                color_reset = C
        else:
            color_reset = GRAY

        pygame.draw.rect(screen, color_reset, resetButton)
        screen.blit(buttonText, buttonRect)

        # Back to difficulty selection button
        backButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 250,
            (width / 3) - BOARD_PADDING * 2, 50
        )
        buttonText = mediumFont.render("Back", True, BLACK)
        buttonRect = buttonText.get_rect()
        buttonRect.center = backButton.center

        if backButton.collidepoint(pygame.mouse.get_pos()):
            color_ai = D
        else:
            color_ai = C

        pygame.draw.rect(screen, color_ai, backButton)
        screen.blit(buttonText, buttonRect)

    if not first_move and found == True:

        # Display text
        if game.mines == flags and won == False:
            won = True
            text = f"Won: {'{:.2f}'.format(time.time() - start_time)}s"
        elif won == True:
            pass
        else:
            text = "Lost" if lost else ""
        dtext = mediumFont.render(text, True, WHITE)
        textRect = dtext.get_rect()
        textRect.center = ((5 / 6) * width, (2 / 3) * height)
        screen.blit(dtext, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Search for a safe board
    if found == False and first_move == False:
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
            if move is None:
                flags = ai.mines.copy()
                #print("No moves left to make.")
            else:
                ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
                revealed = set()
                flags = set()
                lost = False
                game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, starting_position = fmove)
                move = fmove
                #print("Unsafe board")
        #else:
            #print("AI making safe move.")

    # Check for a right-click to toggle flagging
    elif right == 1 and not lost:
        if not first_move:

            mouse = pygame.mouse.get_pos()

            for i, j in [(x, y) for x in range(HEIGHT) for y in range(WIDTH)]:

                if cells[i][j].collidepoint(mouse):

                    if (i, j) not in revealed:

                        if (i, j) in flags:
                            flags.remove((i, j))
                        else:
                            flags.add((i, j))

                        time.sleep(0.1)
                        break

                    else:

                        if game.nearby_mines((i, j)) == nearby_flags((i, j)):
                            for a, b in [(x, y) for x in range(i-1, i+2) for y in range(j-1, j+2) if 0 <= x < HEIGHT and 0 <= y < WIDTH]:
                                if (a, b) not in revealed and (a, b) not in flags:
                                    if game.is_mine((a, b)):
                                        lost = True
                                    else:
                                        nearby = game.nearby_mines((a, b))
                                        if nearby == 0:
                                            cleared_squares = clear((a, b))
                                            for square in cleared_squares:
                                                revealed.add(square)
                                                if game.nearby_mines(square) == 0:
                                                    ai.moves_made.add(square)
                                                    ai.mark_safe(square)
                                                else:
                                                    ai.add_knowledge(square, game.nearby_mines(square))
                                        else:
                                            revealed.add((a, b))
                                            ai.add_knowledge((a, b), nearby)
                        time.sleep(0.1)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # If AI button clicked, make an AI move
        if aiButton.collidepoint(mouse) and not lost and not won:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    #if won == False:
                        #print("No moves left to make.")
                #else:
                    #print("No known safe moves, AI making random move.")
            #else:
                #print("AI making safe move.")
                
            if move is not None and first_move:
                fmove = copy.copy(move)
                game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, starting_position = fmove)
                screen.fill(BLACK)
                title = largeFont.render("Loading...", True, WHITE)
                titleRect = title.get_rect()
                titleRect.center = ((width / 2), 200)
                screen.blit(title, titleRect)
                title = mediumFont.render("Searching for a safe board", True, WHITE)
                titleRect = title.get_rect()
                titleRect.center = ((width / 2), 500)
                screen.blit(title, titleRect)
                pygame.display.update()
                first_move = False
            #time.sleep(0.2)

        # New Game
        elif ngButton.collidepoint(mouse) and game:
            game = None
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
            first_move = True
            revealed = set()
            flags = set()
            lost = False
            found = False
            won = False
            fmove = None
            time.sleep(0.1)
            continue

        elif resetButton.collidepoint(mouse) and fmove:
            if fmove:
                ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
                revealed = set()
                flags = set()
                lost = False
                move = fmove
                start_time = time.time()
                won = False
                time.sleep(0.2)

        elif backButton.collidepoint(mouse):
            first_move = True
            revealed = set()
            flags = set()
            lost = False
            found = False
            won = False
            choose_difficulty = True
            time.sleep(0.3)

        # User-made move
        elif not lost:
            for i, j in [(x, y) for x in range(HEIGHT) for y in range(WIDTH)]:
                if (cells[i][j].collidepoint(mouse)
                    and (i, j) not in flags
                    and (i, j) not in revealed):
                    move = (i, j)
                    if first_move:
                        fmove = copy.copy(move)
                        game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, starting_position = fmove)
                        screen.fill(BLACK)
                        title = largeFont.render("Loading...", True, WHITE)
                        titleRect = title.get_rect()
                        titleRect.center = ((width / 2), 200)
                        screen.blit(title, titleRect)
                        title = mediumFont.render("Searching for a safe board", True, WHITE)
                        titleRect = title.get_rect()
                        titleRect.center = ((width / 2), 500)
                        screen.blit(title, titleRect)
                        pygame.display.update()
                        first_move = False
                    break

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
        else:
            nearby = game.nearby_mines(move)
            if nearby == 0:
                cleared_squares = clear(move)
                for square in cleared_squares:
                    revealed.add(square)
                    if game.nearby_mines(square) == 0:
                        ai.moves_made.add(square)
                        ai.mark_safe(square)
                    else:
                        ai.add_knowledge(square, game.nearby_mines(square))
            else:
                revealed.add(move)
                ai.add_knowledge(move, nearby)

    try:
        if game.mines == flags and found == False:
            found = True
            revealed = set()
            flags = set()
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH, difficulty = difficulty_level)
            nearby = game.nearby_mines(fmove)
            if nearby == 0:
                cleared_squares = clear(fmove)
                for square in cleared_squares:
                    revealed.add(square)
                    if game.nearby_mines(square) == 0:
                        ai.moves_made.add(square)
                        ai.mark_safe(square)
                    else:
                        ai.add_knowledge(square, game.nearby_mines(square))
            start_time = time.time()
    except Exception:
        pass

    if first_move == True or found == True:
        pygame.display.update()
    
