import os
import curses
import random
from math import floor
import argparse as arg
from . import polyshapes as ps

# Try to import pygame for audio support
try:
    import pygame
    import numpy as np
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None
    np = None

# constants
BLOCK_CHAR = "█"
BORDER_CHAR = "║"
TOP_BOTTOM_BORDER_CHAR = "═"
CORNER_CHAR = "╔╗╚╝"
GAME_NAMES = ["Mono", "D", "Tr", "Tetr", "Pent", "Hex"]

# ASCII Art for menus
TETRIS_LOGO = [
    "  ███╗   ██╗      ██╗███████╗",
    "  ████╗  ██║      ██║██╔════╝",
    "  ██╔██╗ ██║█████╗██║███████╗",
    "  ██║╚██╗██║╚════╝██║╚════██║",
    "  ██║ ╚████║      ██║███████║",
    "  ╚═╝  ╚═══╝      ╚═╝╚══════╝"
]

GAME_OVER_ART = [
    "  ██████╗  █████╗ ███╗   ███╗███████╗",
    " ██╔════╝ ██╔══██╗████╗ ████║██╔════╝",
    " ██║  ███╗███████║██╔████╔██║█████╗  ",
    " ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ",
    " ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗",
    "  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝",
    "",
    "  ██████╗ ██╗   ██╗███████╗██████╗ ",
    " ██╔═══██╗██║   ██║██╔════╝██╔══██╗",
    " ██║   ██║██║   ██║█████╗  ██████╔╝",
    " ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗",
    " ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║",
    "  ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝"
]

PAUSE_ART = [
    " ██████╗  █████╗ ██╗   ██╗███████╗███████╗██████╗ ",
    " ██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██╔══██╗",
    " ██████╔╝███████║██║   ██║███████╗█████╗  ██║  ██║",
    " ██╔═══╝ ██╔══██║██║   ██║╚════██║██╔══╝  ██║  ██║",
    " ██║     ██║  ██║╚██████╔╝███████║███████╗██████╔╝",
    " ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═════╝ "
]

MENU_BORDER_TOP = "╔═══════════════════════════════════════════════════════════╗"
MENU_BORDER_BOTTOM = "╚═══════════════════════════════════════════════════════════╝"
MENU_BORDER_SIDE = "║"

# argument parsing
parser = arg.ArgumentParser(
    description="Dis/Tris/Tetris/Pentis/Hexis game implementation in Python using curses; use arrow keys to move blocks, 'q' to quit.")
parser.add_argument("n", type=int, nargs='?',
                    help="specifies the number of blocks in the game; use 2 for Distris (2 block), 3 for Tris (3 blocks), 4 for Tetris (4 blocks), and 5 for Pentis (5 blocks), 6 for Hexis (6 blocks)")
parser.add_argument("-e", action="store_true", help="enable 'fun' mode - additional pseudo-polyominos, also called polykings, its quite fun but also hard, only works for Dis, Tris and Tetris game,\
    there are 2 2-polykings, 6 3-polykings, 34 4-polykings and 166 5-polykings, but the game becomes unplayable with 166 pseudo-polyominos, so i only implemented up to 4-polykings")
parser.add_argument("-c", type=str, help="specifies the color of the blocks; use 'r' for red, 'g' for green, 'b' for blue, 'y' for yellow, 'm' for magenta, 'c' for cyan, or 'w' for white.\
    You are able to change those colors with j/k keys for background and u/i keys for main color during game. Number 0-255 are accepted as well")
parser.add_argument(
    "-bc", type=int, help="same as -c, but for background color, only numbers accepted.")
parser.add_argument("-m", action="store_true",
                    help="enable mix mode, includes polyominos/polykings with less than n blocks")

args = parser.parse_args()

# global game state
add_text = ""
level = 0
total_lines = 0
next_shape = None
held_shape = None
can_hold = True
combo_count = 0
last_action_was_clear = False
color, bcgd = curses.COLOR_WHITE, 0
sound_enabled = False
sound_on = True
is_paused = False
vol = 0


def init_sound(selected_music=None):
    """Initialize pygame mixer for sound effects."""
    global sound_enabled
    global vol

    if not PYGAME_AVAILABLE:
        sound_enabled = False
        return

    try:
        pygame.mixer.pre_init(frequency=22050, size=-
                              16, channels=2, buffer=512)
        pygame.mixer.init()
        vol = 0.05

        # Load background music based on selection
        music_folder = os.path.join(os.path.dirname(__file__), "music")

        if selected_music == 'korobeiniki - piano':
            music_file = os.path.join(
                music_folder, "tetris-theme-korobeiniki-arranged-for-piano-186249.mp3")
            vol = 0.7
        elif selected_music == 'korobeiniki - music box':
            music_file = os.path.join(
                music_folder, "tetris-theme-korobeiniki-rearranged-arr-for-music-box-184978.mp3")
            vol = 0.3
        elif selected_music == 'korobeiniki - strings':
            music_file = os.path.join(
                music_folder, "tetris-theme-korobeiniki-rearranged-arr-for-strings-185592.mp3")
            vol = 0.5
        else:
            music_file = os.path.join(
                music_folder, "Clair_de_lune_(Claude_Debussy)_Suite_bergamasque.ogg")
            vol = 0.95

        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        sound_enabled = True
    except (pygame.error, ImportError):
        sound_enabled = False


def cleanup_sound():
    """Clean up pygame mixer."""
    if sound_enabled and PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except (pygame.error, AttributeError):
            pass


def generate_simple_tone(frequency, duration, wave_type='sine', volume=0.15):
    """Generate a simple tone"""
    if not sound_enabled or not sound_on or not PYGAME_AVAILABLE:
        return None
    try:
        sample_rate = 22050  # i find this value good enough
        frames = int(duration * sample_rate / 1000)
        arr = np.zeros((frames, 2))

        for i in range(frames):
            t = i / sample_rate
            if wave_type == 'sine':
                wave = volume * np.sin(2 * np.pi * frequency * t)
            elif wave_type == 'triangle':
                wave = volume * \
                    (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1)
            elif wave_type == 'square':
                wave = volume * \
                    (1 if np.sin(2 * np.pi * frequency * t) >= 0 else -1)
            else:
                # Default to sine
                wave = volume * np.sin(2 * np.pi * frequency * t)

            arr[i] = [wave, wave]

        # convert to 16-bit integers
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    except:
        return None


def play_sound_effect(frequency, duration=100, wave_type='sine', volume=0.15):
    """Play a simple sound effect."""
    if not sound_enabled or not sound_on or not PYGAME_AVAILABLE:
        return
    try:
        sound = generate_simple_tone(frequency, duration, wave_type, volume)
        if sound:
            sound.play()
    except:
        pass


def sound_line_clear(lines):
    """play sounds for cleaning lines"""
    if not PYGAME_AVAILABLE:
        return
    if lines == 1:
        # Single line
        play_sound_effect(523, 120, 'triangle', 0.12)  # C5
    elif lines == 2:
        # Double
        play_sound_effect(523, 80, 'sine', 0.12)  # C5
        pygame.time.wait(40)
        play_sound_effect(659, 120, 'sine', 0.14)  # E5
    elif lines == 3:
        # Triple
        play_sound_effect(523, 70, 'triangle', 0.12)  # C5
        pygame.time.wait(30)
        play_sound_effect(659, 70, 'triangle', 0.14)  # E5
        pygame.time.wait(30)
        play_sound_effect(784, 150, 'sine', 0.16)  # G5
    elif lines >= 4:
        # Tetris/Pentis/Hexis
        notes = [523, 659, 784, 932]  # C5, E5, G5, Bb5
        for i, freq in enumerate(notes):
            play_sound_effect(freq, 60, 'triangle', 0.12)
            pygame.time.wait(25)
        pygame.time.wait(50)
        play_sound_effect(1047, 200, 'sine', 0.18)  # C6


def sound_piece_lock():
    """Play sound when piece locks."""
    play_sound_effect(196, 60, 'triangle', 0.06)  # G3


def sound_piece_move():
    """Play sound when piece moves."""
    play_sound_effect(330, 30, 'triangle', 0.04)  # E4


def sound_piece_rotate():
    """Play sound when piece rotates."""
    play_sound_effect(440, 40, 'triangle', 0.05)  # A4


def sound_level_up():
    """Play when level increases."""
    if not PYGAME_AVAILABLE:
        return
    notes = [(523, 80), (784, 80), (1047, 80)]  # C5, G5, C6

    for i, (freq, duration) in enumerate(notes):
        play_sound_effect(freq, duration, 'sine', 0.13 + i * 0.02)
        if i < len(notes) - 1:
            pygame.time.wait(35)

    pygame.time.wait(100)
    play_sound_effect(1047, 400, 'sine', 0.16)


def sound_game_over():
    """Play simplified dramatic game over arpeggio."""
    if not PYGAME_AVAILABLE:
        return
    if sound_enabled and sound_on:
        pygame.mixer.music.stop()

    notes = [(523, 200, 0.15), (415, 250, 0.11),
             (294, 300, 0.07)]  # freq, duration, volume

    for i, (freq, duration, vol) in enumerate(notes):
        play_sound_effect(freq, duration, 'sine', vol)
        if i < len(notes) - 1:
            pygame.time.wait(120)

    pygame.time.wait(200)
    play_sound_effect(196, 600, 'sine', 0.10)


def toggle_all_sound():
    """Toggle all sound effects and music on/off."""
    global sound_on
    if not sound_enabled or not PYGAME_AVAILABLE:
        return

    sound_on = not sound_on

    if sound_on:
        # resume music if it was playing
        music_file = os.path.join(os.path.dirname(__file__), "music.mp3")
        if os.path.exists(music_file):
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            except:
                pass
    else:
        # stop all sounds
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()  # stop all sound effects
        except:
            pass


def show_option_menu(stdscr, title, options, option_texts, selected_info=""):
    """show menu with options"""
    selected = 0
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        # draw decorative border
        stdscr.addstr(2, (max_x - len(MENU_BORDER_TOP)) // 2,
                      MENU_BORDER_TOP, curses.color_pair(1))

        # instructions
        instruction_text = "Use ↑↓ arrows to navigate, Enter to select, Q to quit"
        if 3 < max_y - 1 and len(instruction_text) < max_x:
            stdscr.addstr(3, (max_x - len(instruction_text)) //
                          2, instruction_text, curses.color_pair(2))

        # selected info
        start_y = 6
        if selected_info:
            info_lines = selected_info.split('\n')
            for i, line in enumerate(info_lines):
                if start_y + i < max_y - 1 and len(line) < max_x:
                    stdscr.addstr(start_y + i, (max_x - len(line)) //
                                  2, line, curses.color_pair(3))
            start_y += len(info_lines) + 2

        # title with decorative elements
        title_decorated = f"✦ {title} ✦"
        if start_y < max_y - 1 and len(title_decorated) < max_x:
            stdscr.addstr(start_y, (max_x - len(title_decorated)) //
                          2, title_decorated, curses.color_pair(1) | curses.A_BOLD)

        # menu options
        for i, text in enumerate(option_texts):
            option_y = start_y + 3 + i
            if option_y >= max_y - 1:
                break

            if i == selected:
                prefix = "▶ "
                suffix = " ◀"
                full_text = f"{prefix}{text}{suffix}"
                color = curses.color_pair(4) | curses.A_BOLD
            else:
                full_text = f"  {text}  "
                color = curses.color_pair(3)

            if len(full_text) < max_x:
                stdscr.addstr(option_y, (max_x - len(full_text)) //
                              2, full_text, color)

        # bottom border
        bottom_y = start_y + 5 + len(option_texts)
        if bottom_y < max_y - 1:
            stdscr.addstr(bottom_y, (max_x - len(MENU_BORDER_BOTTOM)) //
                          2, MENU_BORDER_BOTTOM, curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == 10:  # Enter
            return options[selected]
        elif key >= ord('1') and key <= ord('9'):
            n_value = key - ord('0')
            if n_value <= len(options):
                return options[n_value - 1]


def show_menu(stdscr):
    """Show enhanced menu with ASCII art to select n, ext and mix options."""
    global bcgd
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, bcgd)
    curses.init_pair(2, curses.COLOR_YELLOW, bcgd)
    curses.init_pair(3, curses.COLOR_GREEN, bcgd)
    curses.init_pair(4, curses.COLOR_RED, bcgd)
    curses.init_pair(5, curses.COLOR_MAGENTA, bcgd)

    # show welcome screen first
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    # display ASCII art logo
    logo_start_y = max(1, (max_y - len(TETRIS_LOGO) - 8) // 2)
    for i, line in enumerate(TETRIS_LOGO):
        if logo_start_y + i < max_y - 1 and len(line) < max_x:
            stdscr.addstr(logo_start_y + i, (max_x - len(line)) //
                          2, line, curses.color_pair(1) | curses.A_BOLD)

    # welcome message
    welcome_msg = "Welcome to N-is!"
    subtitle = "Generalized Tetris from Monois to Hexis"

    msg_y = logo_start_y + len(TETRIS_LOGO) + 2
    if msg_y < max_y - 3:
        stdscr.addstr(msg_y, (max_x - len(welcome_msg)) // 2,
                      welcome_msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(msg_y + 1, (max_x - len(subtitle)) //
                      2, subtitle, curses.color_pair(3))

    # continue prompt
    continue_msg = "Press any key to continue..."
    if msg_y + 4 < max_y - 1:
        stdscr.addstr(msg_y + 4, (max_x - len(continue_msg)) // 2,
                      continue_msg, curses.color_pair(1) | curses.A_BLINK)

    stdscr.refresh()
    stdscr.getch()  # wait for key press

    # select game type
    n_options = [1, 2, 3, 4, 5, 6]
    n_texts = [f"{n} - {GAME_NAMES[i]}is" for i, n in enumerate(n_options)]
    selected_n = show_option_menu(
        stdscr, "Select Game Type", n_options, n_texts)
    if selected_n is None:
        return None, None, None, None

    # select extended mode
    ext_options = [False, True]
    ext_texts = ["Standard Polyominos", "Extended Mode (+ Polykings)"]
    selected_info = f"Selected: {selected_n}-block {GAME_NAMES[selected_n-1]}is\n\nStandard mode uses classic polyominos\nExtended mode adds pseudo-polyominos (polykings)"
    selected_ext = show_option_menu(
        stdscr, "Choose Polyomino Set", ext_options, ext_texts, selected_info)
    if selected_ext is None:
        return None, None, None, None

    # select mix mode
    mix_options = [False, True]
    mix_texts = ["Pure Mode (single type)", "Mix Mode (multiple types)"]
    mix_info = f"Selected: {selected_n}-block {GAME_NAMES[selected_n-1]}is\nMode: {'Extended' if selected_ext else 'Standard'}\n\nPure mode uses only {selected_n}-block pieces\nMix mode includes pieces with fewer blocks too"
    selected_mix = show_option_menu(
        stdscr, "Select Piece Variety", mix_options, mix_texts, mix_info)
    if selected_mix is None:
        return None, None, None, None

    # select music
    music_options = ['korobeiniki - piano', 'korobeiniki - music box',
                     'korobeiniki - strings', 'clair de lune']
    music_texts = ['Korobeiniki - Piano', 'Korobeiniki - Music Box',
                   'Korobeiniki - Strings', 'Clair de Lune']
    music_info = f"Selected: {selected_n}-block {GAME_NAMES[selected_n-1]}is\nMode: {'Extended' if selected_ext else 'Standard'}\nVariety: {'Mix' if selected_mix else 'Pure'}\n\nChoose background music for your game"
    selected_music = show_option_menu(
        stdscr, "Select Music Theme", music_options, music_texts, music_info)
    if selected_music is None:
        return None, None, None, None

    return selected_n, selected_ext, selected_mix, selected_music


def initialize_shapes_and_dimensions():
    """Initialize SHAPES, COLS, ROWS, name_of_game, and add_text based on args."""
    global SHAPES, COLS, ROWS, name_of_game, add_text

    if not args.m:
        SHAPES = ps.poly[2*args.n - 1] if args.e else ps.poly[2*args.n - 2]
    else:
        SHAPES = []
        for k in range(1, 1+args.n):
            SHAPES = SHAPES + \
                ps.poly[2*k - 1] if args.e else SHAPES + ps.poly[2*k - 2]

    name_of_game = GAME_NAMES[args.n - 1] if 1 <= args.n <= 6 else "Mono"
    add_text = "with extended polyominos" if args.e else ""

    e = args.n if args.e else 0
    one = 1 if args.n == 1 else 0
    m = -1 if args.m else 0
    COLS = (3 * args.n) + e - 1 + one + m
    ROWS = (5 * args.n) + e


# initialize game settings
if args.n is None:
    # show menu to select n, ext and mix
    try:
        selected_n, selected_ext, selected_mix, selected_music = curses.wrapper(
            show_menu)
        if selected_n is None:
            exit(0)
        args.n = selected_n
        args.e = selected_ext
        args.m = selected_mix
        args.music = selected_music  # Store selected music
    except curses.error as e:
        print("Error running curses menu.")
        print("Your terminal may not be supported.")
        print(f"Curses error: {e}")
        exit(1)
else:
    args.music = None  # No music selection when using command line args

initialize_shapes_and_dimensions()


def rotate_piece(piece):
    # rotates a piece clockwise by transposing and reversing rows... matrices proved to be useful lol
    return [list(row) for row in zip(*piece[::-1])]


def check_collision(board, piece, offset):
    """
    Check if the piece at the given offset collides with the board
    or goes out of bounds.
    """
    off_x, off_y = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board_x = x + off_x
                board_y = y + off_y
                if not (0 <= board_x < COLS and board_y < ROWS):
                    return True  # out of bounds
                if board_y >= 0 and board[board_y][board_x]:
                    return True  # collision with another piece
    return False


def create_board():
    # creates an empty game board
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def new_piece():
    """Returns a new random piece dictionary."""
    global next_shape
    shape = next_shape
    next_shape = random.choice(SHAPES)
    for _ in range(random.randint(0, 3)):
        next_shape = rotate_piece(next_shape)

    offset = 0
    if args.n < 4:
        # this makes the game *slightly* more interesting for smaller n
        offset = random.randint(-1, 1)

    return {
        "shape": shape,
        "x": COLS // 2 - len(shape[0]) // 2 + offset,
        "y": 0,
    }


def lock_piece(board, piece):
    """Locks the piece onto the board."""
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                board_y = piece["y"] + y
                board_x = piece["x"] + x
                if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                    board[board_y][board_x] = 1
    return board


def clear_lines(board):
    """Clears completed lines and returns the number of lines cleared."""
    new_board = [row for row in board if not all(row)]
    lines_cleared = ROWS - len(new_board)
    # add new empty lines at the top for each cleared line
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(COLS)])
    return new_board, lines_cleared


def try_wall_kick(board, piece, rotated_shape):
    """Try wall kick positions for rotation."""
    # wall kick offsets to try
    kick_offsets = [
        (0, 0),   # no kick (original position)
        (-1, 0),  # left kick
        (1, 0),   # right kick
        (-2, 0),  # left kick 2
        (2, 0),   # right kick 2
        (-3, 0),  # left kick 2
        (3, 0),   # right kick 2
    ]

    for dx, dy in kick_offsets:
        new_x = piece["x"] + dx
        new_y = piece["y"] + dy

        # check if the new position is valid
        if not check_collision(board, rotated_shape, (new_x, new_y)):
            return new_x, new_y, rotated_shape

    # if no wall kick works, return None
    return None


def calculate_score(lines_cleared, level, combo_count):
    """Calculate score based on Tetris scoring system with level and combo bonuses."""
    if lines_cleared == 0:
        return 0

    # base scores for different line clears
    base_scores = {
        1: 60,    # single
        2: 120,   # double
        3: 360,   # triple
        4: 1200,  # tetris (4 lines)
        5: 4096,  # pentis (5 lines)
        6: 16384,  # hexis (6 lines)
    }

    # get base score
    base_score = base_scores.get(lines_cleared)

    # level multiplier (level + 1 to avoid 0 multiplication)
    level_multiplier = level + 1

    # combo bonus
    combo_bonus = combo_count * 50 * level_multiplier * \
        (1+max(0, 4*(args.n - 4))) if combo_count > 0 else 0

    # calculate total score
    total_score = (base_score * level_multiplier) + combo_bonus

    return total_score


def get_ghost_piece_position(board, piece):
    """Calculate where the piece would land if hard dropped."""
    ghost_y = piece["y"]

    # keep moving down until collision
    while not check_collision(board, piece["shape"], (piece["x"], ghost_y + 1)):
        ghost_y += 1

    return ghost_y


def draw_progress_bar(stdscr, y, x, width, current, target, label=""):
    """Draw a progress bar showing current/target with visual indicator."""
    if target == 0:
        percentage = 0
    else:
        percentage = min(current / target, 1.0)

    filled_width = int(width * percentage)

    # draw the bar
    bar = "█" * filled_width + "░" * (width - filled_width)
    try:
        stdscr.addstr(y, x, f"{label}[{bar}] {current}/{target}")
    except curses.error:
        pass


def draw_hold_piece(stdscr, start_y, start_x):
    """Draw the held piece in a designated area."""
    global held_shape

    try:
        stdscr.addstr(start_y, start_x, "HOLD:")
        if held_shape:
            for y, row in enumerate(held_shape):
                for x, cell in enumerate(row):
                    if cell:
                        stdscr.addstr(start_y + 1 + y, start_x +
                                      x * 2, BLOCK_CHAR * 2)
    except curses.error:
        pass


def draw_game_info(stdscr, score):
    """Draw enhanced game information with better styling."""
    global total_lines, combo_count, color, bcgd

    try:
        # main title with decorative elements
        title = f"Score: {score} | Playing {name_of_game}is {add_text}"
        stdscr.addstr(0, 0, title)

        # level information
        stdscr.addstr(args.n + 2, 3+COLS*2, f"Level: {level}")

        # progress bar
        draw_progress_bar(stdscr, args.n + 3, 3+COLS*2, 15,
                          total_lines, 5+level, "Progress: ")

        # combo display
        if combo_count > 0:
            stdscr.addstr(args.n + 4, 3+COLS*2, f"COMBO: {combo_count}x")
            stdscr.addstr(args.n + 5, 3+COLS*2, f"Colors: {color}/{bcgd}")
            return args.n + 7
        else:
            stdscr.addstr(args.n + 4, 3+COLS*2, f"Colors: {color}/{bcgd}")
            return args.n + 6
    except curses.error:
        return args.n + 6


def draw_border(stdscr):
    """Draw enhanced game border with decorative elements."""
    try:
        # top border
        top_border = CORNER_CHAR[0] + \
            TOP_BOTTOM_BORDER_CHAR * (COLS * 2) + CORNER_CHAR[1]
        stdscr.addstr(1, 0, top_border)

        # side borders
        for y in range(ROWS):
            stdscr.addstr(y + 2, 0, BORDER_CHAR)
            stdscr.addstr(y + 2, COLS * 2 + 1, BORDER_CHAR)

        # bottom border
        bottom_border = CORNER_CHAR[2] + \
            TOP_BOTTOM_BORDER_CHAR * (COLS * 2) + CORNER_CHAR[3]
        stdscr.addstr(ROWS + 2, 0, bottom_border)
    except curses.error:
        pass


def draw_next_piece_box(stdscr):
    """Draw a decorative box for the next piece."""
    start_x = 3 + COLS * 2
    start_y = 1

    # box border
    stdscr.addstr(start_y, start_x, "┌─ NEXT ─┐")
    for i in range(1, 6):
        stdscr.addstr(start_y + i, start_x, "│        │")
    stdscr.addstr(start_y + 6, start_x, "└────────┘")


def draw_game(stdscr, board, piece, score):
    """Draws the enhanced game state to the screen."""
    stdscr.clear()

    # draw enhanced game info and get hold position
    hold_y = draw_game_info(stdscr, score)

    # draw enhanced border
    draw_border(stdscr)

    # draw the board with locked pieces
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                try:
                    stdscr.addstr(y + 2, x * 2 + 1, BLOCK_CHAR * 2)
                except curses.error:
                    pass

    # draw ghost piece (where current piece will land)
    if piece:
        ghost_y = get_ghost_piece_position(board, piece)
        # only draw ghost if it's different from current position
        if ghost_y != piece["y"]:
            for y, row in enumerate(piece["shape"]):
                for x, cell in enumerate(row):
                    if not cell:
                        continue
                    ghost_board_y = ghost_y + y
                    ghost_board_x = piece["x"] + x
                    # check bounds and if position is empty
                    if (0 <= ghost_board_y < ROWS and 0 <= ghost_board_x < COLS and
                            not board[ghost_board_y][ghost_board_x]):
                        try:
                            stdscr.addstr(ghost_board_y + 2,
                                          ghost_board_x * 2 + 1, "░░")
                        except curses.error:
                            pass

    # draw the current falling piece
    if piece:
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    if piece["y"] + y >= 0:
                        try:
                            stdscr.addstr(
                                piece["y"] + y + 2, (piece["x"] + x) * 2 + 1, BLOCK_CHAR * 2)
                        except curses.error:
                            pass

    # draw next piece
    try:
        stdscr.addstr(1, 3+COLS*2, "NEXT:")
        for y, row in enumerate(next_shape):
            for x, cell in enumerate(row):
                if cell:
                    stdscr.addstr(y + 2, 3+COLS*2 + (x * 2), BLOCK_CHAR * 2)
    except curses.error:
        pass

    # draw held piece
    draw_hold_piece(stdscr, hold_y, 3+COLS*2)

    stdscr.refresh()


def setup_colors():
    """Setup color configuration based on arguments."""
    global color, bcgd

    bcgd = args.bc if args.bc is not None else 0

    if args.c is not None:
        if args.c.isdigit():
            color = int(args.c)
        else:
            color_map = {
                'r': curses.COLOR_RED,
                'g': curses.COLOR_GREEN,
                'b': curses.COLOR_BLUE,
                'y': curses.COLOR_YELLOW,
                'c': curses.COLOR_CYAN,
                'm': curses.COLOR_MAGENTA
            }
            color = color_map.get(args.c, curses.COLOR_WHITE)


def handle_piece_movement(board, piece, key):
    """Handle piece movement keys."""
    if key == curses.KEY_LEFT:
        if not check_collision(board, piece["shape"], (piece["x"] - 1, piece["y"])):
            piece["x"] -= 1
            sound_piece_move()
    elif key == curses.KEY_RIGHT:
        if not check_collision(board, piece["shape"], (piece["x"] + 1, piece["y"])):
            piece["x"] += 1
            sound_piece_move()
    elif key == curses.KEY_DOWN:
        if not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
            piece["y"] += 1
            return 1  # soft drop bonus
    elif key == curses.KEY_UP:
        rotated = rotate_piece(piece["shape"])
        wall_kick_result = try_wall_kick(board, piece, rotated)
        if wall_kick_result:
            new_x, new_y, new_shape = wall_kick_result
            piece["x"] = new_x
            piece["y"] = new_y
            piece["shape"] = new_shape
            sound_piece_rotate()
    return 0


def handle_hold_piece(piece):
    """Handle piece holding."""
    global can_hold, held_shape
    if can_hold:
        if held_shape is None:
            held_shape = piece["shape"]
            piece.update(new_piece())
        else:
            temp_shape = piece["shape"]
            piece["shape"] = held_shape
            held_shape = temp_shape
            piece["x"] = COLS // 2 - len(piece["shape"][0]) // 2
            piece["y"] = 0
        can_hold = False


def handle_color_change(stdscr, key):
    """Handle color change keys."""
    global color, bcgd

    if key == ord('j') or key == ord('k'):
        bcgd += 1 if key == ord('k') else -1
    if key == ord('u') or key == ord('i'):
        color += 1 if key == ord('u') else -1

    bcgd = bcgd % curses.COLORS
    color = color % curses.COLORS
    curses.init_pair(1, color, bcgd)
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)


def handle_hard_drop(board, piece):
    """Handle hard drop and return score bonus."""
    cells_dropped = 0
    while not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
        piece["y"] += 1
        cells_dropped += 1
    return cells_dropped * 2


def show_game_over_screen(stdscr, score):
    """Display enhanced game over screen."""
    global bcgd
    stdscr.nodelay(0)
    curses.start_color()
    curses.init_pair(6, curses.COLOR_RED, bcgd)
    curses.init_pair(7, curses.COLOR_YELLOW, bcgd)
    curses.init_pair(8, curses.COLOR_CYAN, bcgd)

    max_y, max_x = stdscr.getmaxyx()

    # Display game over ASCII art
    art_start_y = max(1, (max_y - len(GAME_OVER_ART) - 8) // 2)
    for i, line in enumerate(GAME_OVER_ART):
        if art_start_y + i < max_y - 1 and len(line) < max_x:
            color = curses.color_pair(6) if i < 6 else curses.color_pair(7)
            stdscr.addstr(art_start_y + i, (max_x - len(line)) //
                          2, line, color | curses.A_BOLD)

    # Score and stats
    final_score_text = f"✦ Final Score: {score:,} ✦"
    level_text = f"Level Reached: {level}"
    lines_text = f"Total Lines: {total_lines}"

    stats_y = art_start_y + len(GAME_OVER_ART) + 2
    if stats_y < max_y - 4:
        stdscr.addstr(stats_y, (max_x - len(final_score_text)) //
                      2, final_score_text, curses.color_pair(8) | curses.A_BOLD)
        stdscr.addstr(stats_y + 1, (max_x - len(level_text)) //
                      2, level_text, curses.color_pair(7))
        stdscr.addstr(stats_y + 2, (max_x - len(lines_text)) //
                      2, lines_text, curses.color_pair(7))

    # Exit instruction
    exit_text = "Press 'Q' to quit"
    if stats_y + 4 < max_y - 1:
        stdscr.addstr(stats_y + 4, (max_x - len(exit_text)) // 2,
                      exit_text, curses.color_pair(6) | curses.A_BLINK)

    stdscr.refresh()

    # wait for 'q' key specifically
    while True:
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break


def show_pause_screen(stdscr):
    """Display enhanced pause screen."""
    global is_paused
    global vol
    global bcgd
    is_paused = True

    # reduce music volume during pause
    if sound_enabled and sound_on and PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(vol/8)  # Reduced volume
        except:
            pass

    stdscr.nodelay(0)
    curses.start_color()
    curses.init_pair(9, curses.COLOR_YELLOW, bcgd)
    curses.init_pair(10, curses.COLOR_CYAN, bcgd)

    max_y, max_x = stdscr.getmaxyx()

    # display pause ASCII art
    art_start_y = max(1, (max_y - len(PAUSE_ART) - 6) // 2)
    for i, line in enumerate(PAUSE_ART):
        if art_start_y + i < max_y - 1 and len(line) < max_x:
            stdscr.addstr(art_start_y + i, (max_x - len(line)) //
                          2, line, curses.color_pair(9) | curses.A_BOLD)

    # instructions
    resume_text = "Press any key to resume..."
    quit_text = "Or press 'Q' to quit"

    inst_y = art_start_y + len(PAUSE_ART) + 2
    if inst_y < max_y - 3:
        stdscr.addstr(inst_y, (max_x - len(resume_text)) // 2,
                      resume_text, curses.color_pair(10) | curses.A_BLINK)
        stdscr.addstr(inst_y + 1, (max_x - len(quit_text)) //
                      2, quit_text, curses.color_pair(10))

    stdscr.refresh()

    # wait for any key to resume or q to quit
    key = stdscr.getch()
    if key == ord('q') or key == ord('Q'):
        exit(0)

    # restore normal state when unpausing
    is_paused = False

    # restore music volume to normal
    if sound_enabled and sound_on and PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(vol)  # Restore original volume
        except:
            pass

    # restore non-blocking input
    stdscr.nodelay(1)
    stdscr.timeout(20)


def main(stdscr):
    global next_shape
    global vol
    next_shape = random.choice(SHAPES)  # initialize the first piece
    """Main game loop."""
    # setup curses
    curses.curs_set(0)
    global level, total_lines, combo_count, last_action_was_clear, can_hold

    # initialize sound with selected music
    init_sound(getattr(args, 'music', None))

    setup_colors()
    curses.start_color()
    curses.init_pair(1, color, bcgd)  # set color pair for blocks
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    stdscr.nodelay(1)
    stdscr.timeout(20)  # game tick speed like PAL

    # game state initialization
    board = create_board()
    piece = new_piece()
    score = 0
    game_over = False
    fall_counter = 0
    fall_speed = 36  # starting speed, lower is faster

    if args.n < 4:
        fall_speed = 36 - 6*(4-args.n)

    while not game_over:
        key = stdscr.getch()
        fall_counter += 1

        # --- handle user input ---
        if key == ord('q') or key == ord('Q'):
            break
        elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP]:
            if key == curses.KEY_DOWN:
                fall_counter = 0  # reset fall counter for soft drop
            score += handle_piece_movement(board, piece, key)
        elif key == ord('c') or key == ord('C'):
            handle_hold_piece(piece)
        elif key in [ord('k'), ord('j'), ord('u'), ord('i')]:
            handle_color_change(stdscr, key)
        elif key == 10:  # hard drop
            fall_counter = fall_speed
            score += handle_hard_drop(board, piece)
        elif key == ord('p') or key == ord('P'):
            show_pause_screen(stdscr)
        elif key == ord('m') or key == ord('M'):
            # Toggle all sound on/off
            toggle_all_sound()
        elif key == curses.KEY_PPAGE or key == curses.KEY_NPAGE:
            # Volume control with Page Up/Page Down
            if PYGAME_AVAILABLE:
                vol += 0.1 if key == curses.KEY_PPAGE else -0.1
                if vol > 1 or vol < 0:
                    vol = max(0, min(1, vol))
                    play_sound_effect(440, 100)
                if sound_enabled and sound_on:
                    try:
                        pygame.mixer.music.set_volume(vol)
                    except:
                        pass

        # --- game logic (automatic drop) ---
        if fall_counter >= fall_speed:
            fall_counter = 0
            if not check_collision(board, piece["shape"], (piece["x"], piece["y"] + 1)):
                piece["y"] += 1
            else:
                # piece has landed, lock it
                sound_piece_lock()
                board = lock_piece(board, piece)
                board, lines_cleared = clear_lines(board)

                # handle scoring with combo system
                if lines_cleared > 0:

                    if lines_cleared + total_lines < 5+level:
                        sound_line_clear(lines_cleared)
                    # if last action was also a line clear, increment combo
                    if last_action_was_clear:
                        combo_count += 1
                    else:
                        combo_count = 0  # reset combo if previous action wasn't a clear

                    # calculate score with level and combo bonuses
                    line_score = calculate_score(
                        lines_cleared, level, combo_count)
                    score += line_score
                    total_lines += lines_cleared
                    last_action_was_clear = True
                else:
                    # no lines cleared, reset combo
                    combo_count = 0
                    last_action_was_clear = False

                # get new piece and allow holding again
                piece = new_piece()
                can_hold = True

                # check for game over
                if check_collision(board, piece["shape"], (piece["x"], piece["y"])):
                    game_over = True

        if total_lines >= 5+level:
            old_level = level
            level += 1
            total_lines -= 4+level
            # increase speed every 10 lines cleared
            fall_speed = max(2, floor(fall_speed * 0.855))
            if level != old_level:
                sound_level_up()

        # draw game
        draw_game(stdscr, board, piece, score)

    # game over
    sound_game_over()
    show_game_over_screen(stdscr, score)
    cleanup_sound()

def run():
    try:
        curses.wrapper(main)
    except curses.error as e:
        print("Error running curses.")
        print("Your terminal may not be supported, or it probably is too small.")
        print(f"Curses error: {e}")
        cleanup_sound()
    except KeyboardInterrupt:
        cleanup_sound()
    finally:
        cleanup_sound()

if __name__ == "__main__":
    run()
