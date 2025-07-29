import subprocess
import os

class Choreography:
    def __init__(self, interpreter=None):
        self.tasks = {}
        self.interpreter = interpreter

    def define_task(self, name, command):
        self.tasks[name] = command

    def run_task(self, name):
        if name not in self.tasks:
            raise Exception(f"Task '{name}' not defined.")
        command = self.tasks[name]
        print(f"Running choreography task: {name} - {command}")
        try:
            # Execute shell command
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Stdout:", result.stdout)
            print("Stderr:", result.stderr)
            return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            print("Command failed with error:", e)
            print("Stdout:", e.stdout)
            print("Stderr:", e.stderr)
            return {"status": "failed", "stdout": e.stdout, "stderr": e.stderr, "error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"status": "failed", "error": str(e)}

    def run_heartbreak_code_task(self, verse_name):
        if not self.interpreter:
            raise Exception("Interpreter not provided for running HeartbreakCode tasks.")
        print(f"Running HeartbreakCode task: {verse_name}")
        try:
            self.interpreter.execute_verse_by_name(verse_name)
            return {"status": "success"}
        except Exception as e:
            print(f"HeartbreakCode task failed: {e}")
            return {"status": "failed", "error": str(e)}
