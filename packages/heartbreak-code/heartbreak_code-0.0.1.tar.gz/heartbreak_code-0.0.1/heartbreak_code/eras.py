import os
import shutil
import datetime

class ErasSystem:
    def __init__(self, project_root):
        self.project_root = project_root
        self.eras_dir = os.path.join(project_root, ".eras")
        self._ensure_eras_dir()

    def _ensure_eras_dir(self):
        """Ensures the .eras directory exists."""
        if not os.path.exists(self.eras_dir):
            os.makedirs(self.eras_dir)
            print(f"Initialized Eras System at {self.eras_dir}")

    def _get_current_era_path(self, era_name):
        """Returns the path for a specific era."""
        return os.path.join(self.eras_dir, era_name)

    def _get_timestamp(self):
        """Generates a timestamp for commits."""
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def create_era(self, era_name):
        """Creates a new era (branch)."""
        era_path = self._get_current_era_path(era_name)
        if os.path.exists(era_path):
            print(f"Era '{era_name}' already exists.")
            return False
        os.makedirs(era_path)
        print(f"Created new era: '{era_name}'")
        return True

    def record_memory(self, era_name, message=""):
        """Records a memory (commit snapshot) in the specified era."""
        era_path = self._get_current_era_path(era_name)
        if not os.path.exists(era_path):
            print(f"Era '{era_name}' does not exist. Create it first.")
            return False

        timestamp = self._get_timestamp()
        memory_path = os.path.join(era_path, f"memory_{timestamp}")
        os.makedirs(memory_path)

        # Copy relevant project files to the memory snapshot
        # For simplicity, let's copy all .py files in heartbreak_code/ and main.py, README.md, requirements.txt
        files_to_snapshot = [
            os.path.join(self.project_root, "main.py"),
            os.path.join(self.project_root, "README.md"),
            os.path.join(self.project_root, "requirements.txt"),
        ]
        for root, _, files in os.walk(os.path.join(self.project_root, "heartbreak_code")):
            for file in files:
                if file.endswith(".py") and "__pycache__" not in root:
                    files_to_snapshot.append(os.path.join(root, file))

        for f in files_to_snapshot:
            if os.path.exists(f):
                dest_path = os.path.join(memory_path, os.path.relpath(f, self.project_root))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(f, dest_path)
        
        # Store commit message
        with open(os.path.join(memory_path, "message.txt"), "w") as f:
            f.write(message)

        print(f"Recorded memory in era '{era_name}' at {timestamp} with message: '{message}'")
        return True

    def review_story_so_far(self, era_name):
        """Reviews the story so far (history) for a given era."""
        era_path = self._get_current_era_path(era_name)
        if not os.path.exists(era_path):
            print(f"Era '{era_name}' does not exist.")
            return

        memories = sorted([d for d in os.listdir(era_path) if os.path.isdir(os.path.join(era_path, d)) and d.startswith("memory_")])
        if not memories:
            print(f"No memories recorded yet for era '{era_name}'.")
            return

        print(f"Story so far for era '{era_name}':")
        for memory in memories:
            memory_path = os.path.join(era_path, memory)
            message_file = os.path.join(memory_path, "message.txt")
            message = "(No message)"
            if os.path.exists(message_file):
                with open(message_file, "r") as f:
                    message = f.read().strip()
            print(f"- {memory.replace('memory_', '')}: {message}")

    def list_eras(self):
        """Lists all available eras."""
        if not os.path.exists(self.eras_dir):
            print("No eras initialized yet.")
            return

        eras = [d for d in os.listdir(self.eras_dir) if os.path.isdir(os.path.join(self.eras_dir, d))]
        if not eras:
            print("No eras found.")
            return

        print("Available Eras:")
        for era in eras:
            print(f"- {era}")

if __name__ == "__main__":
    # Example Usage (for testing purposes)
    # This block will only run if eras.py is executed directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_example = os.path.abspath(os.path.join(current_dir, "..")) # Assuming project root is one level up

    eras_system = ErasSystem(project_root_example)

    print("""--- Listing Eras ---""")
    eras_system.list_eras()

    print("""--- Creating Era 'Fearless' ---""")
    eras_system.create_era("Fearless")

    print("""--- Recording Memory in 'Fearless' ---""")
    eras_system.record_memory("Fearless", "Initial project setup")

    print("""--- Creating Era 'Red' ---""")
    eras_system.create_era("Red")

    print("""--- Recording Memory in 'Red' ---""")
    eras_system.record_memory("Red", "Added new feature X")

    print("""--- Listing Eras Again ---""")
    eras_system.list_eras()

    print("""--- Reviewing Story So Far for 'Fearless' ---""")
    eras_system.review_story_so_far("Fearless")

    print("""--- Reviewing Story So Far for 'Red' ---""")
    eras_system.review_story_so_far("Red")