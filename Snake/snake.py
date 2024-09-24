import tkinter
import random
import pygame
import time
from PIL import Image, ImageTk

ROWS = 25
COLS = 25
TILE_SIZE = 25

WINDOW_WIDTH = TILE_SIZE * ROWS
WINDOW_HEIGHT = TILE_SIZE * COLS

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Musique
pygame.mixer.init()
music_files = ['Music/level1.mp3', 'Music/level2.mp3', 'Music/level3.mp3']
pygame.mixer.music.load(music_files[0])
pygame.mixer.music.play(-1)

# Game Window
window = tkinter.Tk()
window.title("Snake")
window.resizable(False, False)

canvas = tkinter.Canvas(window, bg="black", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, borderwidth=0, highlightthickness=0)
canvas.pack()
window.update()

# center window
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (screen_height/2))

window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

# Initialize the game
snake = Tile(5*TILE_SIZE, 5*TILE_SIZE)  # Snake Head
food = Tile(10*TILE_SIZE, 10*TILE_SIZE)
snake_body = []

velocityX = 0
velocityY = 0

game_over = False
score = 0
level = 1
level_threshold = 5
game_speed = 100
level_up_display_time = 3
level_up_time = None

mines = []

# Load explosion GIF
explosion_gif_path = 'Image/giphy.gif'
explosion_frames = []
gif = Image.open(explosion_gif_path)
for frame in range(gif.n_frames):
    gif.seek(frame)
    explosion_frames.append(ImageTk.PhotoImage(gif.resize((TILE_SIZE, TILE_SIZE), Image.BICUBIC)))

def reset_game():
    global snake, food, snake_body, velocityX, velocityY, game_over, score, level, game_speed, level_up_time, mines
    snake = Tile(5*TILE_SIZE, 5*TILE_SIZE)  # Snake Head
    food = Tile(10*TILE_SIZE, 10*TILE_SIZE)
    snake_body = []
    velocityX = 0
    velocityY = 0
    game_over = False
    score = 0
    level = 1
    game_speed = 100
    level_up_time = None
    mines = []
    pygame.mixer.music.load(music_files[0])
    pygame.mixer.music.play(-1)

def change_direction(e):  # e = event
    global velocityX, velocityY, game_over
    if game_over:
        if e.keysym == "space":
            reset_game()
        return

    if (e.keysym == "Up" and velocityY != 1):
        velocityX = 0
        velocityY = -1
    elif (e.keysym == "Down" and velocityY != -1):
        velocityX = 0
        velocityY = 1
    elif (e.keysym == "Left" and velocityX != 1):
        velocityX = -1
        velocityY = 0
    elif (e.keysym == "Right" and velocityX != -1):
        velocityX = 1
        velocityY = 0

def move():
    global snake, food, snake_body, game_over, score
    if game_over:
        return

    if snake.x < 0 or snake.x >= WINDOW_WIDTH or snake.y < 0 or snake.y >= WINDOW_HEIGHT:
        game_over = True
        return

    for tile in snake_body:
        if snake.x == tile.x and snake.y == tile.y:
            game_over = True
            return

    for mine in mines:
        if snake.x == mine.x and snake.y == mine.y:
            animate_explosion(mine.x, mine.y)
            game_over = True
            return

    if snake.x == food.x and snake.y == food.y:
        snake_body.append(Tile(food.x, food.y))
        food.x = random.randint(0, COLS - 1) * TILE_SIZE
        food.y = random.randint(0, ROWS - 1) * TILE_SIZE
        score += 1

    for i in range(len(snake_body) - 1, -1, -1):
        tile = snake_body[i]
        if i == 0:
            tile.x = snake.x
            tile.y = snake.y
        else:
            prev_tile = snake_body[i - 1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y

    snake.x += velocityX * TILE_SIZE
    snake.y += velocityY * TILE_SIZE

def update_level():
    global level, score, game_speed, level_up_time
    if score >= level * level_threshold:
        level += 1
        level_up_time = time.time()
        if level <= len(music_files):
            pygame.mixer.music.load(music_files[level - 1])
            pygame.mixer.music.play(-1)
        if level == 2:
            game_speed = 80
            place_mines(5)
        elif level == 3:
            game_speed = 60
            place_mines(5)

def place_mines(num_mines):
    global mines
    mines = []
    for _ in range(num_mines):
        while True:
            mine_x = random.randint(0, COLS - 1) * TILE_SIZE
            mine_y = random.randint(0, ROWS - 1) * TILE_SIZE
            if (mine_x, mine_y) != (snake.x, snake.y) and all(mine_x != t.x or mine_y != t.y for t in snake_body) and (mine_x, mine_y) != (food.x, food.y):
                mines.append(Tile(mine_x, mine_y))
                break

def animate_explosion(x, y):
    for frame in explosion_frames:
        canvas.create_image(x, y, anchor=tkinter.NW, image=frame)
        window.update()
        time.sleep(0.1)
        canvas.delete("all")

def draw():
    global snake, food, snake_body, game_over, score
    move()
    update_level()

    canvas.delete("all")

    if level == 1:
        canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="black")
    elif level == 2:
        canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="blue")
    elif level == 3:
        canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="purple")

    canvas.create_oval(food.x, food.y, food.x + TILE_SIZE, food.y + TILE_SIZE, fill="red")

    snake_color = "lime green"
    snake_border_color = "white"
    snake_border_width = 1
    canvas.create_rectangle(snake.x, snake.y, snake.x + TILE_SIZE, snake.y + TILE_SIZE,
                            fill=snake_color, outline=snake_border_color, width=snake_border_width)
    for tile in snake_body:
        canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE,
                                fill=snake_color, outline=snake_border_color, width=snake_border_width)

    for mine in mines:
        canvas.create_rectangle(mine.x, mine.y, mine.x + TILE_SIZE, mine.y + TILE_SIZE, fill="gray")

    if game_over:
        canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, font="Arial 20", text=f"Game Over: {score}", fill="white")
    else:
        canvas.create_text(30, 20, font="Arial 10", text=f"Level: {level} \nScore: {score}", fill="white")
        if level_up_time and (time.time() - level_up_time < level_up_display_time):
            canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, font="Arial 30", text=f"Level {level}", fill="yellow")

    window.after(game_speed, draw)

draw()

window.bind("<KeyRelease>", change_direction)
window.mainloop()
