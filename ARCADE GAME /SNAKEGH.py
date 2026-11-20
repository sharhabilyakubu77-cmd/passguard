"""
SNAKEGH - A CLASSIC ARCADE GAME
    LAB 2 PYTHON LEVEL (200)
    Name: Sharhabil yakubu Anamzoya | Index No :< 2526400394 >

"""

import tkinter as tk
import random
import os
import struct
import wave
import shutil
import subprocess
import threading

try:
    import winsound
except ImportError:
    winsound = None

BORDER= 24
COLUMN =25
ROWS = 20
WIDTH = BORDER * COLUMN
HEIGHT = BORDER * ROWS
START_SPEED = 150
SNAKE_HIGHEST_SCORE= "SNAKE_HIGH_SCORE.txt"
SNAKE_HIGHEST_SCORE_NOWALLS = "SNAKE_HIGH_SCORE_NOWALLS.txt"
BONUS_EVERY = 5
BONUS_TIME = 40
TUNE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_tune.wav")


CONTROLS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
KEYS = {"up": "Up", "w": "Up", "down": "Down", "s": "Down",
        "left": "Left", "a": "Left", "right": "Right", "d": "Right"}
def next_head(head,controls):
    dx,dy=CONTROLS[controls]
    x,y=head
    return x+dx ,y+dy
def hits_wall(cell):
    x, y = cell
    return x < 0 or x >= COLUMN or y < 0 or y >= ROWS
def hits_self(head, snake):
    return head in snake[:-1]
def random_food(snake, avoid=()):
    free = [(x, y) for x in range(COLUMN) for y in range(ROWS)
            if (x, y) not in snake and (x, y) not in avoid]
    return random.choice(free) if free else None
def level_for(score):
    return score//5+1
def speed_for(level):
    return max(60,START_SPEED-(level-1 )*15)
def bonus_points(time_left):

    return max(1, time_left * 10 // BONUS_TIME)
def score_file():
    return SNAKE_HIGHEST_SCORE if walls else SNAKE_HIGHEST_SCORE_NOWALLS
def load_highest_score():
    try:
        with open(score_file(),"r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0
def save_highest_score(score):
    with open(score_file(),"w") as file:

        file.write(str(score))



def midi_freq(note):

    return 440 * 2 ** ((note - 69) / 12)


def make_tune(path):

    rate = 22050
    n = int(rate * 0.2)
    lead = [72, 76, 79, 76, 72, 76, 79, 84,
            69, 72, 76, 72, 69, 72, 76, 81,
            65, 69, 72, 69, 65, 69, 72, 77,
            67, 71, 74, 71, 67, 71, 74, 79]
    roots = [48, 45, 41, 43]
    frames = bytearray()
    for i, note in enumerate(lead):
        lead_freq = midi_freq(note)
        bass_freq = midi_freq(roots[i // 8])
        for k in range(n):
            t = k / rate
            bass_pos = (i % 4) * n + k       # position inside the current half bar
            lead_wave = 1 if (lead_freq * t) % 1 < 0.5 else -1
            bass_wave = 1 if (bass_freq * bass_pos / rate) % 1 < 0.5 else -1
            lead_vol = 0.25 * min(1, k / 150) * (1 - 0.6 * k / n)
            bass_vol = 0.20 * (1 - 0.3 * bass_pos / (4 * n))
            frames += struct.pack("<h", int((lead_wave * lead_vol + bass_wave * bass_vol) * 32767))
    with wave.open(path, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes(bytes(frames))


def find_backend():

    if winsound is not None:
        return "winsound", None
    for command in (["afplay"], ["paplay"], ["aplay", "-q"],
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]):
        if shutil.which(command[0]):
            return command[0], command
    return None, None


backend, backend_command = find_backend()
tune_stop = threading.Event()
tune_process = None


def loop_external(stop):

    global tune_process
    while not stop.is_set():
        tune_process = subprocess.Popen(backend_command + [TUNE_PATH],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tune_process.wait()
        if tune_process.returncode not in (0, -15):    # player failed: don't spin forever
            break


def start_tune():
    global tune_stop
    if backend == "winsound":
        winsound.PlaySound(TUNE_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    else:
        tune_stop = threading.Event()
        threading.Thread(target=loop_external, args=(tune_stop,), daemon=True).start()


def stop_tune():
    if backend == "winsound":
        winsound.PlaySound(None, winsound.SND_PURGE)
    else:
        tune_stop.set()
        if tune_process is not None and tune_process.poll() is None:
            tune_process.terminate()


snake = [ ]
direction = "Right"
next_direction = "Right"
food = (0, 0)
score = 0
level = 1
walls = True
high_score = load_highest_score()
running = False
paused = False
loop_id = None
foods_eaten = 0
bonus = None
bonus_left = 0
sound_on = True
music_playing = False

def sync_music():

    global music_playing, backend
    if backend is None:
        return
    want = sound_on and running and not paused
    try:
        if want and not music_playing:
            start_tune()
            music_playing = True
        elif not want and music_playing:
            stop_tune()
            music_playing = False
    except (RuntimeError, OSError):
        backend = None
        music_playing = False


def draw_grid():

    for x in range(0, WIDTH, BORDER):
        canvas.create_line(x, 0, x, HEIGHT, fill="#1e1e1e")
    for y in range(0, HEIGHT, BORDER):
        canvas.create_line(0, y, WIDTH, y, fill="#1e1e1e")


def draw_border():

    canvas.delete("border")
    if walls:
        canvas.create_rectangle(2, 2, WIDTH - 2, HEIGHT - 2, outline="#e53935", width=4, tags="border")
    else:
        canvas.create_rectangle(2, 2, WIDTH - 2, HEIGHT - 2, outline="#00e5ff", width=2,
                                dash=(6, 6), tags="border")


def update_labels():
    score_label.config(text=f"Score: {score}   Level: {level}   Best: {high_score}")
    if backend is None:
        music = "NO AUDIO PLAYER FOUND"
    else:
        music = ("ON" if sound_on else "OFF") + f" [{backend}]"
    status_label.config(text=f"Walls: {'ON' if walls else 'OFF'} (T, before a game)     Music: {music} (M)")


def draw():

    canvas.delete("piece", "message")
    if food:
        fx, fy = food
        canvas.create_oval(fx * BORDER + 4, fy * BORDER + 4, fx * BORDER + BORDER - 4, fy * BORDER + BORDER - 4,
                           fill="#e53935", outline="", tags="piece")
    if bonus:

        canvas.create_rectangle(0, 0, WIDTH * bonus_left // BONUS_TIME, 6,
                                fill="#ffd600", outline="", tags="piece")

        if bonus_left > BONUS_TIME // 4 or bonus_left % 2 == 0:
            bx, by = bonus
            cx, cy = bx * BORDER + BORDER // 2, by * BORDER + BORDER // 2
            r = BORDER // 2 - 1
            canvas.create_polygon(cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy,
                                  fill="#ffd600", outline="#fff59d", width=2, tags="piece")
    for index, (x, y) in enumerate(snake):
        colour = "red" if index == 0 else "red"
        canvas.create_rectangle(x * BORDER + 1, y * BORDER + 1,
                                x * BORDER + BORDER - 1, y * BORDER + BORDER - 1,
                                fill=colour, outline="", tags="piece")
    if snake:
        hx, hy = snake[0]
        px, py = hx * BORDER, hy * BORDER
        eyes = {"Right": [(16, 6), (16, 18)], "Left": [(8, 6), (8, 18)],
                "Up": [(6, 8), (18, 8)], "Down": [(6, 16), (18, 16)]}
        for ex, ey in eyes[direction]:
            canvas.create_oval(px + ex - 3, py + ey - 3, px + ex + 3, py + ey + 3,
                               fill="white", outline="", tags="piece")
    update_labels()


def show_message(title, subtitle):

    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, text=title, fill="white",
                       font=("Segoe UI", 28, "bold"), tags="message")
    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, text=subtitle, fill="#bbbbbb",
                       font=("Segoe UI", 12), tags="message")


def start_game(event=None):
    global snake, direction, next_direction, food, score, level, running, paused, loop_id
    global foods_eaten, bonus, bonus_left
    if loop_id is not None:
        root.after_cancel(loop_id)
    snake = [(5, 10), (4, 10), (3, 10)]
    direction = "Right"
    next_direction = "Right"
    food = random_food(snake)
    score = 0
    level = 1
    foods_eaten = 0
    bonus = None
    bonus_left = 0
    running = True
    paused = False
    sync_music()
    draw()
    loop_id = root.after(speed_for(level), game_loop)


def game_loop():

    global direction, food, score, level, loop_id, foods_eaten, bonus, bonus_left
    direction = next_direction
    head = next_head(snake[0], direction)
    if not walls:
        head = (head[0] % COLUMN, head[1] % ROWS)
    if hits_wall(head) or hits_self(head, snake):
        game_over()
        return
    snake.insert(0, head)
    if head == food:
        score += 1
        foods_eaten += 1
        level = level_for(score)
        food = random_food(snake, [bonus] if bonus else [])
        if foods_eaten % BONUS_EVERY == 0 and bonus is None:
            bonus = random_food(snake, [food] if food else [])
            bonus_left = BONUS_TIME
    elif bonus and head == bonus:

        score += bonus_points(bonus_left)
        level = level_for(score)
        bonus = None
    else:
        snake.pop()
    if bonus:
        bonus_left -= 1
        if bonus_left <= 0:
            bonus = None
    draw()
    loop_id = root.after(speed_for(level), game_loop)


def on_key(event):

    global next_direction
    new_direction = KEYS.get(event.keysym.lower())
    if new_direction is None or not running or paused:
        return
    if new_direction != OPPOSITE[direction]:
        next_direction = new_direction


def on_space(event=None):
    if not running:
        start_game()


def toggle_pause(event=None):
    global paused, loop_id
    if not running:
        return
    paused = not  paused
    sync_music()
    if paused:
        root.after_cancel(loop_id)
        show_message("PAUSED", "Press P to continue")
    else:
        canvas.delete("message")
        loop_id = root.after(speed_for(level), game_loop)


def toggle_walls(event=None):
    global walls, high_score
    if running:
        return
    walls = not walls
    high_score = load_highest_score()
    draw_border()
    update_labels()


def toggle_sound(event=None):
    global sound_on
    sound_on = not sound_on
    sync_music()
    update_labels()


def game_over():
    global running, high_score
    running = False
    sync_music()
    if score > high_score:
        high_score = score
        save_highest_score(high_score)
        show_message("NEW HIGH SCORE!", f"You scored {score}. Press Space to play again")
    else:
        show_message("GAME OVER", f"You scored {score}. Press Space to play again")
    update_labels()


def on_close():
    if backend is not None and music_playing:
        stop_tune()
    root.destroy()


if backend is not None and not os.path.exists(TUNE_PATH):
    make_tune(TUNE_PATH)

root = tk.Tk()
root.title("SnakeGH - Classic Arcade Game")
root.resizable(False, False)
root.configure(bg="#0d1b2a")
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="SnakeGH", font=("Segoe UI", 22, "bold"),
         fg="#66bb6a", bg="#0d1b2a").pack(pady=(10, 0))
score_label = tk.Label(root, text="Score: 0   Level: 1   Best: 0",
                       font=("Consolas", 13, "bold"), fg="white", bg="#0d1b2a")
score_label.pack(pady=(0, 8))

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#121212", highlightthickness=0)
canvas.pack(padx=15)

status_label = tk.Label(root, text="", font=("Consolas", 11, "bold"), fg="#ffd600", bg="#0d1b2a")
status_label.pack(pady=(8, 0))
tk.Label(root, text="Arrows / W A S D = move     P = pause     Space = start\n"
                    "Gold diamond = timed bonus food. Grab it fast for up to 10 points!",
         fg="#90a4ae", bg="#0d1b2a").pack(pady=8)

root.bind("<Key>", on_key)
root.bind("<space>", on_space)
root.bind("p", toggle_pause)
root.bind("P", toggle_pause)
root.bind("t", toggle_walls)
root.bind("T", toggle_walls)
root.bind("m", toggle_sound)
root.bind("M", toggle_sound)

draw_grid()
draw_border()
update_labels()
show_message("SnakeGH", "Press Space to start")
root.mainloop()