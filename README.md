# receipt-compresser

Watches a folder for new receipt images and saves downsized JPEG copies to an output folder. Supports HEIC/HEIF (iPhone photos) as well as any format Pillow can open.

## How it works

- Watches a folder (non-recursive) using [watchdog](https://github.com/gorakhargosh/watchdog).
- For each new file, resizes it to fit within **800×800 px** (aspect ratio preserved, LANCZOS) and converts it to RGB.
- Saves the result as `<original-name>.jpg` in the save folder.
- Skips files whose compressed `.jpg` already exists, so it never overwrites or duplicates work.
- Original files are left untouched.

## Requirements

- Python 3
- macOS for the background service (`install.sh` uses launchd). `monitor.py` itself runs anywhere watchdog does.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python monitor.py
```

By default this watches `~/Pictures/Receipts` and writes to `~/Pictures/Receipts/Compressed`. Both folders are created if missing.

### Options

| Flag | Env var | Default | Description |
|------|---------|---------|-------------|
| `--watch DIR` | `RECEIPTS_WATCH_DIR` | `~/Pictures/Receipts` | Folder to watch |
| `--save DIR` | `RECEIPTS_SAVE_DIR` | `<watch>/Compressed` | Folder for compressed output |
| `--existing`, `--ex` | n/a | off | Compress files already in the watch folder before watching |

Example:

```bash
python monitor.py --watch ~/Desktop/receipts --save ~/Desktop/receipts-small --existing
```

## Run at login (macOS)

`install.sh` sets up a launchd LaunchAgent that starts at login and restarts if it crashes. It creates a `.venv` in the project and installs the dependencies.

```bash
./install.sh                          # defaults
./install.sh WATCH_DIR [SAVE_DIR]     # custom folders
./install.sh --uninstall              # remove the agent
```

The agent runs with `--existing`, so anything added while it wasn't running is compressed at startup.

- Label: `com.receipt-compresser`
- Plist: `~/Library/LaunchAgents/com.receipt-compresser.plist` (generated from [launchd/com.receipt-compresser.plist.template](launchd/com.receipt-compresser.plist.template))
- Logs: `~/Library/Logs/receipt-compresser.log`

Useful commands:

```bash
tail -f ~/Library/Logs/receipt-compresser.log
launchctl print gui/$(id -u)/com.receipt-compresser
```

## Project layout

| File | Purpose |
|------|---------|
| [monitor.py](monitor.py) | CLI entry point: folder watcher and batch compression |
| [images.py](images.py) | Image resizing and saving (Pillow + pillow-heif) |
| [install.sh](install.sh) | Install/uninstall the launchd agent |
| [launchd/](launchd) | LaunchAgent plist template |
| [requirements.txt](requirements.txt) | Pinned dependencies |

## Notes

- Output name is the original name up to the first `.`, plus `.jpg`. Two files that differ only after the first dot (e.g. `a.b.png` and `a.heic`) would collide.
- The max size (800×800) is set in `images.py` (`max_size`).
