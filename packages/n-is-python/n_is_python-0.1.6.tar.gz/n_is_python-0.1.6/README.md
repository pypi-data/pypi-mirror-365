# N-is: A Generalized Tetris Game

N-is is a terminal-based puzzle game that generalizes the classic Tetris concept to work with polyominos and polykings of any size from 1 to 6 blocks. Play traditional Tetris (4 blocks) or experiment with Tris (3 blocks), Dis (2 blocks), Pentis (5 blocks), or even Hexis (6 blocks)!
Made for [Summer of Making](https://summer.hackclub.com/)

## Features

- **Flexible Block Size**: Choose your game style with different block counts:
  - **1**: "Monois" (single blocks)
  - **2**: "Dis" (domino shapes) 
  - **3**: "Tris" (triomino shapes)
  - **4**: "Tetris" (classic tetromino shapes)
  - **5**: "Pentis" (pentomino shapes - more challenging)
  - **6**: "Hexis" (hexomino shapes - extremely challenging, nearly unplayable)

  Heptis will probably never be made because even hexis is not very fun, and heptis just simply has no reason to exist.

- **Interactive Menu System**: Run without arguments to access a user-friendly curses-based menu for selecting game options

- **Extended Mode**: Enable with `-e` flag to add non-standard polyominos (polykings) that can connect at vertices

- **Mix Mode**: Enable with `-m` flag to include polyominos of lower order (e.g., in Tetris mode, also get Tris, Dis and monois pieces)

- **Advanced Gameplay Features**:
  - **Hold System**: Hold pieces for later use with 'c' key
  - **Ghost Piece**: See where your piece will land
  - **Hard Drop**: Instantly drop pieces with Enter key
  - **Combo System**: Chain line clears for bonus points

- **Customizable Appearance**: 
  - Choose block and background colors with `-c` and `-bc` flags
  - Change colors during gameplay with j/k and u/i

- **Progressive Difficulty**: 
  - Fall speed increases with each level by around 14.5%
  - Scoring system with level and combo multipliers

- **Background Music**: Multiple music options available in the interactive menu

**Arguments:**
- `N` (optional): Number of blocks (1-6). If omitted, interactive menu appears
- `-e`: Enable extended mode (polykings/pseudo-polyominos)
- `-m`: Enable mix mode (include lower-order polyominos)
- `-c COLOR`: Block color (`r`, `g`, `b`, `y`, `m`, `c`, `w` or 0-255)
- `-bc NUMBER`: Background color (0-255)
- `-h`: Show help message

**Examples:**
```bash
n_is              # Interactive menu
n_is 4            # Classic Tetris
n_is 3 -e         # Tris with polykings
n_is 5 -c g -bc 0 # Green Pentis on black background
n_is 4 -m         # Tetris with Tris and Dis pieces included
```
## How to run:
```
n-is
```

or

```
n_is
```

## Game Controls

### Movement & Rotation
- **Left/Right Arrow**: Move piece horizontally
- **Down Arrow**: Soft drop (faster fall + 1 point per cell)
- **Up Arrow**: Rotate piece clockwise
- **Enter**: Hard drop (instant drop + 2 points per cell)

### Game Features
- **C**: Hold current piece (swap with held piece)
- **P**: Pause game (press any key to resume)
- **Q**: Quit game

### Audio Controls
- **M**: Toggle all sound and music on/off
- **Page Up/Page Down**: Adjust music volume

### Visual Customization (During Game)
- **U/I**: Change main block color (previous/next)
- **J/K**: Change background color (previous/next)

## Game Mechanics

### Scoring System
- **Line Clears**: Points based on number of lines cleared simultaneously
  - 1 line: 60 × (level + 1)
  - 2 lines: 120 × (level + 1)  
  - 3 lines: 360 × (level + 1)
  - 4 lines: 1200 × (level + 1)
  - 5 lines: 4096 × (level + 1)
  - 6 lines: 16384 × (level + 1)
- **Combo Bonus**: Additional points for consecutive line clears
- **Drop Bonus**: 1 point per cell for soft drop, 2 points per cell for hard drop

### Level Progression
- Fall speed increases by ~14.5% each level
- Minimum fall speed prevents game from becoming unplayable

## Music Attribution

The game includes background music from the following sources:

- **Clair de lune (Claude Debussy) Suite bergamasque** by [Laurens Goedhart](https://en.wikipedia.org/wiki/File:Clair_de_lune_(Claude_Debussy)_Suite_bergamasque.ogg) is licensed under [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/)

- **Tetris Theme (Korobeiniki) arrangements** by [GregorQuendel](https://pixabay.com/users/gregorquendel-19912121/) are licensed under the [Pixabay License](https://pixabay.com/service/license-summary/):
  - Piano arrangement
  - Music box arrangement  
  - String arrangement

## Compatibility

| Operating System | Status | Notes |
|------------------|--------|-------|
| Linux | ✅ Fully Supported | Tested on Fedora 42 |
| Windows 11 | ❌️ wont work on windows because of lack of support with curses library|
| macOS | ❓ Expected to work | Unix-compatible, but untested |

## Troubleshooting

**Error: "Your terminal may not be supported, or it probably is too small"**
- Solution: Increase your terminal window size, or make font smaller
- For higher N values, larger terminals may be required

**Colors not displaying correctly:**
- Try different color values (0-255)
- Some terminals may have limited color support
