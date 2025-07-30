# KeyPractice

KeyPractice is a slim, cross-platform terminal-based typing trainer. It allows you to practice custom exercises defined in YAML files, and tracks your analytics (best times, streaks, session data, etc.).

## Features
- Easily extensible: add your own YAML exercise files
- Tracks your best times, streaks, and session history
- Tracks speed (WPM), error counts, and improvements over time
- View analytics for each exercise (best time, best speed, lowest errors, streak, last 5 sessions)
- Minimal dependencies (just Python and PyYAML)
- Works on Windows, Mac, and Linux

## Installation

### From PyPI (Recommended)
```sh
pip install keypractice
```

### From Source
1. Ensure you have Python 3.7+ installed.
2. Install dependencies:
   ```sh
   pip install -r maintenance/requirements.txt
   ```
3. Install as a module:
   ```sh
   pip install -e .
   ```

## Usage

1. Place your YAML exercise files in the `exercises/` folder.
2. Run KeyPractice:
   ```sh
   keypractice
   # or from source:
   python -m keypractice
   ```
3. Select an exercise and start practicing!
4. To view analytics for an exercise, choose the analytics option in the menu.

## Project Structure

```
KeyPractice/
├── keypractice/           # Software code
│   ├── __init__.py
│   ├── __main__.py       # Main entry point
│   ├── core.py           # Core typing logic
│   ├── analytics.py      # Analytics tracking
│   └── data/             # Analytics data
├── exercises/            # Your exercise files
│   ├── special_characters.yaml
│   └── home_row.yaml
└── maintenance/         # Development files
    ├── setup.py
    ├── requirements.txt
    └── publish scripts
```

## Creating Custom YAML Exercises

Each exercise is a YAML file in the `exercises/` folder. Example:

```yaml
name: Home Row
items:
  - a
  - s
  - d
  - f
  - j
  - k
  - l
  - ;
```

- `name`: The name of the exercise (shown in the menu).
- `items`: A list of strings to practice typing. Each item will be shown one at a time.

You can create as many YAML files as you like. Each will appear as a separate exercise in the menu.

## Analytics
The software tracks and displays:
- **Best time** per exercise (in seconds)
- **Best speed** (WPM - Words Per Minute)
- **Lowest error count** per exercise
- **Streak** (consecutive days practiced)
- **Last session date** and time
- **Last 5 sessions** with detailed breakdown:
  - Date and time
  - Time taken (seconds)
  - Error count
  - Speed (WPM)

## Context
This was originally created to practice with the Lynxware keyboard-mouse hardware. Since the workshop no longer services devices and the store shut down, I overhauled the program's identity to test any keypress — whatever unusual hardware you're using.

 I hate the institute of the mouse with a burning passion. I use a wide range of strange hardware to have alternatives for a mouse in some scenarios. In such cases, sometimes you have to adjust to a custom layout. The tool was created to manage the practice and provide analytics of my performance and improvement.

You're encouraged to use it, modify it, and distribute it as you see fit. If you'd like to contribute question sets or support further development, your involvement is welcome.

Stephen