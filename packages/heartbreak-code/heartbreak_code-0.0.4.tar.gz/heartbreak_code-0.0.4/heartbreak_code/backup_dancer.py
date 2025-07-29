import threading
import queue
import time

class BackupDancer(threading.Thread):
    def __init__(self, interpreter, verse_name, args, result_queue):
        super().__init__()
        self.interpreter = interpreter
        self.verse_name = verse_name
        self.args = args
        self.result_queue = result_queue
        self.exception = None

    def run(self):
        try:
            # Create a new interpreter instance for the thread to avoid scope conflicts
            # This is a simplified approach; a more robust solution might involve
            # deep copying the interpreter's state or carefully managing shared state.
            thread_interpreter = type(self.interpreter)()
            # Copy functions and albums to the new interpreter
            thread_interpreter.functions = self.interpreter.functions
            thread_interpreter.albums = self.interpreter.albums

            # Set up arguments in the thread's interpreter scope
            thread_interpreter.push_scope()
            for param_name, param_value in self.args.items():
                thread_interpreter.current_scope[param_name] = param_value

            # Execute the verse
            thread_interpreter.execute_verse_by_name(self.verse_name)
            self.result_queue.put((self.verse_name, thread_interpreter.return_value))
            thread_interpreter.pop_scope()
        except Exception as e:
            self.exception = e
            self.result_queue.put((self.verse_name, None, e)) # Put exception in queue

class BackupDancerManager:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.threads = {}
        self.result_queue = queue.Queue()

    def start_backup_dancer(self, verse_name, args):
        dancer = BackupDancer(self.interpreter, verse_name, args, self.result_queue)
        self.threads[verse_name] = dancer
        dancer.start()
        print(f"Backup Dancer '{verse_name}' started in parallel.")

    def get_backup_dancer_result(self, verse_name):
        # This is a blocking call. In a real app, you'd want a non-blocking way
        # to check for results or use a callback mechanism.
        while True:
            try:
                name, result, *exception = self.result_queue.get(timeout=0.1)
                if name == verse_name:
                    if exception:
                        raise exception[0]
                    return result
                else:
                    # Put it back if it's not for us
                    self.result_queue.put((name, result, *exception))
            except queue.Empty:
                # No result yet, maybe do something else or wait longer
                time.sleep(0.05) # Small delay to prevent busy-waiting
                continue
        return None # Should not be reached
