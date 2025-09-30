# Thymer ⏱️

A beautiful, interactive terminal-based timer app built for productive developers.

![Thymer Demo](https://img.shields.io/badge/status-beta-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🎯 Multiple parallel timers
- ⌨️ Single-key controls
- 🚀 Fast navigation with arrow keys
- 📊 Lap/split tracking
- 🎨 Clean TUI interface
- ⚡ Zero-config start

## Demo

```
╭─ → Timer 1 ────────────────────────────────── Laps: 2  ─╮
│ Timer:               Timer 1                            │
│ Time:                00:01:23.45                        │
│ Status:              ▶ RUNNING                          │
│                                                         │
│ Laps:                2 recorded                         │
│   Lap 1:             00:00:30.12                        │
│   Lap 2:             00:00:53.33                        │
╰─────────────────────────────────────────────────────────╯

Press Space to pause/play • L for lap • N for new timer
```

## Installation

### Option 1: Global Installation

```bash
git clone https://github.com/itzsrikanth/thymer.git
cd thymer
pip install .
# Now you can run: thymer
```

### Option 2: Virtual Environment (Recommended)

```bash
git clone https://github.com/itzsrikanth/thymer.git
cd thymer
make install-venv
source venv/bin/activate
# Now you can run: thymer
```

### Option 3: Run Without Installing

```bash
git clone https://github.com/itzsrikanth/thymer.git
cd thymer
make run-direct
# or: pip install -r requirements.txt && python -m thymer
```

### Binary Release

Download the latest binary from [Releases](https://github.com/itzsrikanth/thymer/releases) for your platform.

## Usage

Start Thymer:

```bash
thymer
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Space` | Play/Pause current timer |
| `L` | Record a lap/split |
| `R` | Reset current timer |
| `N` | Create new timer |
| `D` | Delete current timer |
| `↑/↓` | Navigate between timers |
| `Q` | Quit application |

## Development

### Setup

```bash
git clone https://github.com/itzsrikanth/thymer.git
cd thymer
make install  # or: pip install -e ".[dev]"
```

### Run

```bash
make run  # or: python -m thymer
```

### Build Binary

```bash
make build  # or: python build.py
```

Binary will be in `dist/` directory.

### Quick Commands

```bash
make install    # Install in dev mode
make run        # Run the app
make build      # Build binary
make clean      # Clean build artifacts
```

## Contributing

Contributions welcome! Open an issue or submit a PR.

## License

MIT License - see [LICENSE](LICENSE) file.

## Credits

Built with [Textual](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/).
