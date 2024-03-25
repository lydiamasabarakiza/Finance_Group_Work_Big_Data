import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# Define the base directory and file structure
base_dir = 'my_distributed'
master_dir = os.path.join(base_dir, 'master')
child_dirs = [os.path.join(base_dir, f'data_node_{i}') for i in range(1, 3)]

# Initialize the file structure
def initialize_files():
    os.makedirs(master_dir, exist_ok=True)
    for child_dir in child_dirs:
        os.makedirs(child_dir, exist_ok=True)

# File event handler for synchronization
class FileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            # Exclude files labeled 'main'
            if 'main' not in file_name:
                for child_dir in child_dirs:
                    dest_path = os.path.join(child_dir, file_name)
                    shutil.copy2(event.src_path, dest_path)
                    print(f'File {file_name} copied to {child_dir}')

# Setup file monitoring
def monitor_files():
    event_handler = FileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, master_dir, recursive=False)  # Monitor only the master directory directly
    observer.start()
    return observer

# Main function to setup and monitor
def main():
    initialize_files()
    observer = monitor_files()
    print("Monitoring changes... Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
