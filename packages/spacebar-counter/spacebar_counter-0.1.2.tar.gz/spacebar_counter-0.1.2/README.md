# spacebar-counter

A simple Python CLI tool to count your spacebar presses per day and visualize your stats!

## Installation

Install from PyPI:
```bash
pip install spacebar-counter
```

Or install the latest version from GitHub:
```bash
pip install git+https://github.com/kalashb/spacebar-counter.git
```

## Usage

Start tracking your spacebar presses:
```bash
spacebar-counter start
```
- This will count your spacebar presses for the current day.
- The count resets automatically at midnight.
- **A file named `spacebar_stats.json` will be created in the directory where you run this command.**
- This file stores your daily spacebar stats (date, count, first and last press times).

Generate a dashboard:
```bash
spacebar-counter dashboard
```
- This creates `spacebar_dashboard.html` in the same directory.
- Open it in your browser to see your daily spacebar stats as a dot plot.

## Data Storage

- **`spacebar_stats.json`**: Stores your daily stats. Created/updated when you run `start`.
- **`spacebar_dashboard.html`**: The dashboard file. Created/updated when you run `dashboard`.
- Both files are created in the directory where you run the commands.
- Each user has their own local files; your stats are private and not shared.

## Requirements

- Python 3.7+
- `pynput`
- `plotly`
- `typer`

## License

MIT

---

**Tip:**  
- Add a "Features" section if you want to highlight more.
- Add a "Contributing" section if you want others to help improve your tool.

---

Would you like me to update your README.md for you? If so, let me know your GitHub username and repo name, or I can leave placeholders for you to fill in!