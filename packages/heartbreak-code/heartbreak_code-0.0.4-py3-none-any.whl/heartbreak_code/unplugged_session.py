import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class UnpluggedSession:
    def __init__(self, project_root, music_video_engine=None):
        self.project_root = project_root
        self.music_video_engine = music_video_engine
        self.observer = None
        self.event_handler = None
        self.running = False
        print("Unplugged Session initialized. Ready for live coding.")

    def _reload_code(self, file_path):
        """Simulates hot-reloading of code."""
        print(f"\n--- Hot-reloading: {file_path} ---")
        # In a real scenario, this would involve:
        # 1. Unloading the old module/function
        # 2. Reloading the new module/function
        # 3. Updating references in the running application
        # For this simulation, we'll just print a message.
        if file_path.endswith('.py'):
            module_name = os.path.basename(file_path).replace('.py', '')
            print(f"Attempting to reload Python module: {module_name}")
            # Example: You might want to re-import the module
            # import importlib
            # if module_name in sys.modules:
            #     importlib.reload(sys.modules[module_name])
            # else:
            #     importlib.import_module(module_name)
        elif self.music_video_engine and (file_path.endswith('.html') or file_path.endswith('.css') or file_path.endswith('.js')):
            print(f"Notifying Music Video Engine to update for: {file_path}")
            # self.music_video_engine.update_visuals(file_path) # Placeholder for actual engine call
        print("Reload complete (simulated).")

    def start_watching(self, path_to_watch):
        """Starts monitoring a directory for file changes."""
        if self.running:
            print("Unplugged Session is already running.")
            return

        print(f"Starting Unplugged Session: Watching for changes in {path_to_watch}...")
        self.event_handler = ChangeHandler(self._reload_code)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path_to_watch, recursive=True)
        self.observer.start()
        self.running = True
        print("Unplugged Session started. Press Ctrl+C to stop.")

    def stop_watching(self):
        """Stops monitoring for file changes."""
        if self.running and self.observer:
            print("Stopping Unplugged Session...")
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("Unplugged Session stopped.")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.callback(event.dest_path)

if __name__ == "__main__":
    # Example Usage (for testing purposes)
    # This block will only run if unplugged_session.py is executed directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_example = os.path.abspath(os.path.join(current_dir, "..")) # Assuming project root is one level up

    # Create a dummy directory and file for testing
    test_dir = os.path.join(project_root_example, "test_live_code")
    os.makedirs(test_dir, exist_ok=True)
    test_file = os.path.join(test_dir, "test_verse.py")
    with open(test_file, "w") as f:
        f.write("print('Initial verse')")

    unplugged_session = UnpluggedSession(project_root_example)
    unplugged_session.start_watching(test_dir)

    try:
        print(f"\nModify '{test_file}' to see hot-reloading in action. (e.g., add a comment, save)")
        print("Or create a new file in 'test_live_code'.")
        while True:
            time.sleep(1) # Keep the main thread alive
    except KeyboardInterrupt:
        unplugged_session.stop_watching()
        print("\nUnplugged Session example finished.")
        # Clean up dummy directory and file
        shutil.rmtree(test_dir)
