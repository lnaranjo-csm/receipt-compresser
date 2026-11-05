import argparse, time, os, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from images import compress_image, save_image

# --- CONFIGURATION ---
# Set via CLI flags or environment variables (RECEIPTS_WATCH_DIR / RECEIPTS_SAVE_DIR).
# Defaults are filled in by main(); the save dir defaults to <watch dir>/Compressed.
FOLDER_TO_WATCH = ""
FOLDER_TO_SAVE = ""

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Ignore directory creation, we only care about files
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # --- YOUR CUSTOM CODE HERE ---
        print(f"New file detected: {filename}")
        compress_file(filepath)

def compress_file(path: str):
    files_compressed = os.listdir(FOLDER_TO_SAVE)
    filename = os.path.basename(path).split(".")[0]
    filename_compressed = f"{filename}.jpg"

    if filename_compressed in files_compressed:
        print(f"WARN: File {filename_compressed} has been compressed already")
        return

    img = compress_image(path)
    save_image(img, f"{FOLDER_TO_SAVE}/{filename_compressed}")
    print(f"File {filename_compressed} saved in {FOLDER_TO_SAVE}")

def compress_existing():
    files = os.listdir(FOLDER_TO_WATCH)
    files_compressed = os.listdir(FOLDER_TO_SAVE)

    print(f"Existing compressed files: ", files_compressed)

    for file_reg in files:
        filename = file_reg.split(".")[0]
        if not filename or os.path.isdir(f"{FOLDER_TO_WATCH}/{file_reg}"):
            print(f"WARN: File: {FOLDER_TO_WATCH}/{file_reg} does not exist or is a directory")
            continue

        filename_compressed = f"{filename}.jpg"

        if filename_compressed not in files_compressed:
            print(f'File {filename} not found in {FOLDER_TO_SAVE}')
            img = compress_image(f"{FOLDER_TO_WATCH}/{file_reg}")

            save_image(img, f"{FOLDER_TO_SAVE}/{filename_compressed}")

def main():
    global FOLDER_TO_WATCH, FOLDER_TO_SAVE

    parser = argparse.ArgumentParser(description="Compress new receipt images in a folder.")
    parser.add_argument("--watch", default=os.environ.get("RECEIPTS_WATCH_DIR", "~/Pictures/Receipts"),
                        help="Folder to watch (env: RECEIPTS_WATCH_DIR)")
    parser.add_argument("--save", default=os.environ.get("RECEIPTS_SAVE_DIR"),
                        help="Folder for compressed output (env: RECEIPTS_SAVE_DIR; default: <watch>/Compressed)")
    parser.add_argument("--existing", "--ex", action="store_true",
                        help="Compress files already in the watch folder first")
    parser.add_argument("legacy", nargs="?", help=argparse.SUPPRESS)  # old `monitor.py ex` form
    args = parser.parse_args()

    FOLDER_TO_WATCH = os.path.abspath(os.path.expanduser(args.watch))
    FOLDER_TO_SAVE = os.path.abspath(os.path.expanduser(args.save or os.path.join(FOLDER_TO_WATCH, "Compressed")))
    os.makedirs(FOLDER_TO_WATCH, exist_ok=True)
    os.makedirs(FOLDER_TO_SAVE, exist_ok=True)

    if args.existing or args.legacy == "ex":
        compress_existing()

    observer = Observer()
    observer.schedule(NewFileHandler(), FOLDER_TO_WATCH, recursive=False)
    observer.start()
    print(f"Monitoring started on {FOLDER_TO_WATCH}...", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
