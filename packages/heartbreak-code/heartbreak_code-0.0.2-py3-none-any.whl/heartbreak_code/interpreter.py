
import json
import requests
import os
import re
import time # For simulating async operations
import sys
import io
import threading
import queue

from heartbreak_code.greatest_hits import GreatestHits
from heartbreak_code.tokenizer import Tokenizer
from heartbreak_code.parser import Parser, Identifier

from heartbreak_code.the_setlist import Setlist
from heartbreak_code.backup_dancer import BackupDancerManager
from heartbreak_code.security_sandbox import SecuritySandbox
from heartbreak_code.choreography import Choreography
from heartbreak_code.chart_topper import ChartTopper
from heartbreak_code.passing_notes import PassingNotes
from heartbreak_code.music_video import MusicVideo
from heartbreak_code.final_draft import FinalDraft
from heartbreak_code.eras import ErasSystem
from heartbreak_code.unplugged_session import UnpluggedSession
from heartbreak_code.narrative_arc import NarrativeArc

class Interpreter:
    def __init__(self):
        self.scopes = [{}]
        self.functions = {}
        self.albums = {}
        self.return_value = None
        self.the_setlist = Setlist(self)
        self.greatest_hits = GreatestHits(self, self.the_setlist)
        self.backup_dancer_manager = BackupDancerManager(self)
        self.security_sandbox = SecuritySandbox()
        self.choreography = Choreography(self)
        self.chart_topper = ChartTopper()
        self.passing_notes = PassingNotes()
        self.music_video = MusicVideo()
        self.final_draft = FinalDraft()
        self.current_request = None # For The Setlist
        self.current_response = None # For The Setlist

    def execute_verse_by_name(self, verse_name):
        """Executes a HeartbreakCode verse by its name."""
        if verse_name not in self.functions:
            raise Exception(f"Undefined verse: {verse_name}")
        function_node = self.functions[verse_name]
        self.push_scope()
        # No arguments are passed when called from Setlist for now
        self.return_value = None
        self.visit(function_node.body)
        self.pop_scope()

    def visit_GrantPermission(self, node):
        self.security_sandbox.grant_permission(self.visit(node.permission_type))

    def visit_RevokePermission(self, node):
        self.security_sandbox.revoke_permission(self.visit(node.permission_type))

    def visit_DefineChoreography(self, node):
        self.choreography.define_task(self.visit(node.name), self.visit(node.command))

    def visit_RunChoreography(self, node):
        result = self.choreography.run_task(self.visit(node.name))
        # You might want to store the result in a variable or handle it further
        print(f"Choreography task result: {result}")

    def visit_RunHeartbreakCodeChoreography(self, node):
        result = self.choreography.run_heartbreak_code_task(self.visit(node.verse_name))
        print(f"HeartbreakCode Choreography task result: {result}")

    def visit_RunHeartbreakCodeChoreography(self, node):
        result = self.choreography.run_heartbreak_code_task(self.visit(node.verse_name))
        print(f"HeartbreakCode Choreography task result: {result}")

    def visit_VisualizeChart(self, node):
        vis_type = self.visit(node.visualization_type)
        data = self.visit(node.data)
        kwargs = {self.visit(k): self.visit(v) for k, v in node.kwargs.items()}
        self.chart_topper.visualize(vis_type, data, **kwargs)

    def visit_PassNote(self, node):
        channel = self.visit(node.channel)
        message = self.visit(node.message)
        self.passing_notes.pass_note(channel, message)

    def visit_ListenForNote(self, node):
        channel = self.visit(node.channel)
        return self.passing_notes.listen_for_note(channel)

    def visit_StartMusicVideoEngine(self, node):
        self.music_video = MusicVideo() # Re-initialize for a fresh start
        print("Music Video engine started.")

    def visit_AddSprite(self, node):
        sprite_name = self.visit(node.sprite_name)
        initial_position = self.visit(node.initial_position) if node.initial_position else (0, 0)
        return self.music_video.add_sprite(sprite_name, initial_position)

    def visit_AnimateSprite(self, node):
        sprite = self.visit(node.sprite)
        animation_frames = self.visit(node.animation_frames)
        duration = self.visit(node.duration)
        self.music_video.animate_sprite(sprite, animation_frames, duration)

    def visit_HandleEvent(self, node):
        event_type = self.visit(node.event_type)
        handler_verse = self.visit(node.handler_verse)
        # Need to wrap the handler_verse in a callable that the music_video engine can use
        def event_handler_wrapper(*args, **kwargs):
            # This is a simplified approach. In a real scenario, you'd need to map
            # the event arguments from the engine to the HeartbreakCode verse parameters.
            print(f"HeartbreakCode event handler for {event_type} triggered.")
            # For now, we'll just call the verse without passing specific args
            # A more robust solution would involve passing args to the verse
            # self.execute_verse_by_name(handler_verse)
            # For now, let's just print the args received from the engine
            print(f"  Engine args: {args}, kwargs: {kwargs}")
            # If the verse expects specific parameters, you'd need to extract them from args/kwargs
            # and set them in a new scope before executing the verse.
            # For the example in main.py, the verse expects 'event_type' and 'key'.
            # We'll simulate passing these by setting them in a temporary scope.
            self.push_scope()
            self.current_scope['event_type'] = args[0] if args else None
            self.current_scope['key'] = args[1] if len(args) > 1 else None
            self.execute_verse_by_name(handler_verse)
            self.pop_scope()

        self.music_video.handle_event(event_type, event_handler_wrapper)

    def visit_StartGameLoop(self, node):
        self.music_video.start_game_loop()

    def visit_AnalyzeCode(self, node):
        code_content = self.visit(node.code)
        issues = self.final_draft.analyze_code(code_content)
        return self.final_draft.generate_report()

    @property
    def current_scope(self):
        return self.scopes[-1]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def resolve_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Undefined variable: {name}")

    def assign_variable(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        self.current_scope[name] = value

    def interpret(self, ast):
        self.visit(ast)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.assign_variable(node.identifier, value)

    def visit_SpeakNow(self, node):
        value = self.visit(node.value)
        # Use sys.stdout.write to ensure output is captured by StringIO
        sys.stdout.write(str(value) + "\n")

    def render_code(self, source_code: str) -> str:
        """
        Executes HeartbreakCode and captures its output.
        Useful for templating engines or evaluating expressions.
        """
        # Save original stdout
        original_stdout = sys.stdout
        # Redirect stdout to a string buffer
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            tokenizer = Tokenizer(source_code)
            tokens = tokenizer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            self.interpret(ast)
            return captured_output.getvalue()
        finally:
            # Restore original stdout
            sys.stdout = original_stdout

    def visit_Identifier(self, node):
        return self.resolve_variable(node.name)

    def visit_Number(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_Comparison(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        operator = node.operator

        if operator == "is":
            return left_val == right_val
        elif operator == "is not":
            return left_val != right_val
        elif operator == "is greater than":
            return left_val > right_val
        elif operator == "is less than":
            return left_val < right_val
        elif operator == "is greater than or equal to":
            return left_val >= right_val
        elif operator == "is less than or equal to":
            return left_val <= right_val
        else:
            raise Exception(f"Unknown comparison operator: {operator}")

    def visit_IfStatement(self, node):
        if self.visit(node.condition):
            self.visit(node.body)
        else:
            executed_else_if = False
            for else_if_block in node.else_if_blocks:
                if self.visit(else_if_block.condition):
                    self.visit(else_if_block.body)
                    executed_else_if = True
                    break
            if not executed_else_if and node.else_block:
                self.visit(node.else_block)

    def visit_ElseIfStatement(self, node):
        # This will be handled by visit_IfStatement
        pass

    def visit_ElseStatement(self, node):
        self.visit(node.body)

    def visit_TracklistLiteral(self, node):
        return [self.visit(element) for element in node.elements]

    def visit_TracklistAccess(self, node):
        tracklist = self.visit(node.tracklist)
        index = self.visit(node.index)
        if not isinstance(tracklist, list):
            raise Exception(f"Type error: {tracklist} is not a tracklist.")
        if not isinstance(index, int):
            raise Exception(f"Type error: Tracklist index must be an integer, got {type(index).__name__}.")
        if index < 0 or index >= len(tracklist):
            raise Exception(f"Index out of bounds: Tracklist has {len(tracklist)} elements, but index {index} was requested.")
        return tracklist[index]

    def visit_WhileLoop(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_ForLoop(self, node):
        tracklist = self.visit(node.tracklist)
        if not isinstance(tracklist, list):
            raise Exception(f"Type error: Cannot iterate over non-tracklist type {type(tracklist).__name__}.")
        for item in tracklist:
            self.push_scope()
            self.current_scope[node.item_name] = item
            self.visit(node.body)
            self.pop_scope()

    def visit_FunctionDefinition(self, node):
        self.functions[node.name] = node

    def visit_FunctionCall(self, node):
        # Check if it's a built-in Greatest Hits function
        if hasattr(self.greatest_hits, node.name):
            method = getattr(self.greatest_hits, node.name)
            # Prepare arguments for the Greatest Hits method
            args = []
            kwargs = {}
            # Assuming Greatest Hits functions take positional arguments or keyword arguments
            # This part needs to be carefully aligned with how GreatestHits methods are defined
            # For simplicity, we'll pass all arguments as keyword arguments if they are named
            # Otherwise, we'll try to pass them positionally if the method expects it.
            # A more robust solution would involve inspecting the method signature.
            for param_name, param_value_node in node.arguments.items():
                kwargs[param_name] = self.visit(param_value_node)
            
            try:
                return method(**kwargs)
            except TypeError as e:
                # If keyword arguments don't match, try positional if no kwargs were intended
                if not kwargs and node.arguments:
                    # This is a heuristic and might need refinement based on actual GreatestHits methods
                    positional_args = [self.visit(arg_node) for arg_node in node.arguments.values()]
                    return method(*positional_args)
                else:
                    raise Exception(f"Error calling Greatest Hits function '{node.name}': {e}")

        if node.name not in self.functions:
            raise Exception(f"Undefined function: {node.name}")

        function_node = self.functions[node.name]
        self.push_scope()
        
        # Assign arguments to parameters in the new scope
        if len(node.arguments) != len(function_node.parameters):
            raise Exception(f"Function '{node.name}' expects {len(function_node.parameters)} arguments, but {len(node.arguments)} were provided.")

        for param_name in function_node.parameters:
            if param_name not in node.arguments:
                raise Exception(f"Missing argument for parameter '{param_name}' in function call to '{node.name}'.")
            self.current_scope[param_name] = self.visit(node.arguments[param_name])

        self.return_value = None  # Reset return value before function execution
        self.visit(function_node.body)
        self.pop_scope()
        return self.return_value

    def visit_ReturnStatement(self, node):
        self.return_value = self.visit(node.value)
        # In a real interpreter, you might want to stop execution of the current function here
        # For simplicity, we'll just set the return_value and let the function continue if there's more code
        # A more robust solution would involve raising a special exception to unwind the stack.

    def visit_AlbumDefinition(self, node):
        self.albums[node.name] = node

    def visit_RecordInstantiation(self, node):
        if node.album_name not in self.albums:
            raise Exception(f"Undefined Album: {node.album_name}")

        album_node = self.albums[node.album_name]
        record_instance = {"__type__": "Record", "__album_name__": node.album_name}
        
        self.push_scope() # New scope for record properties
        self.current_scope["this"] = record_instance # 'this' refers to the current record instance

        # Process album body to define properties and methods
        self.visit(album_node.body)

        # Assign arguments to record properties
        for param_name, param_value_node in node.args.items():
            record_instance[param_name] = self.visit(param_value_node)

        self.pop_scope()
        return record_instance

    def visit_MemberAccess(self, node):
        obj = self.visit(node.obj)
        member = node.member

        if isinstance(obj, dict) and obj.get("__type__") == "Record":
            if member in obj:
                return obj[member]
            elif member in self.functions: # Check for methods defined globally
                # For now, methods are just global functions. In a more complex system,
                # methods would be defined within the AlbumDefinition.
                return self.functions[member]
            else:
                raise Exception(f"Undefined member '{member}' for Record of Album '{obj.get('__album_name__')}'")
        elif isinstance(obj, dict) and obj.get("__type__") == "LinerNotes":
            if member in obj:
                return obj[member]
            else:
                raise Exception(f"Undefined key '{member}' in Liner Notes.")
        else:
            raise Exception(f"Cannot access members of type {type(obj).__name__}")

    def visit_TryCatchFinally(self, node):
        try:
            self.visit(node.try_body)
        except Exception as e:
            if node.catch_body:
                self.push_scope()
                self.current_scope["error"] = str(e) # Make error message available in catch block
                self.visit(node.catch_body)
                self.pop_scope()
            else:
                raise e # Re-raise if no catch block
        finally:
            if node.finally_body:
                self.visit(node.finally_body)

    def visit_LinerNotesLiteral(self, node):
        liner_notes = {"__type__": "LinerNotes"}
        for key, value_node in node.pairs.items():
            liner_notes[key] = self.visit(value_node)
        return liner_notes

    def visit_LinerNotesAccess(self, node):
        liner_notes = self.visit(node.liner_notes)
        key = self.visit(node.key)
        if not isinstance(liner_notes, dict) or liner_notes.get("__type__") != "LinerNotes":
            raise Exception(f"Type error: {liner_notes} is not Liner Notes.")
        if key not in liner_notes:
            raise Exception(f"Key '{key}' not found in Liner Notes.")
        return liner_notes[key]

    def visit_FeatureImport(self, node):
        file_path = node.file_name
        # Assuming HeartbreakCode files have a .hc extension and are in the same directory
        full_path = os.path.join(os.path.dirname(__file__), f"{file_path}.hc")
        if not os.path.exists(full_path):
            raise Exception(f"Module not found: {full_path}")

        with open(full_path, "r") as f:
            module_code = f.read()

        # Tokenize and parse the imported module
        tokenizer = Tokenizer(module_code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        module_ast = parser.parse()

        # Create a new interpreter instance for the module to avoid scope pollution
        module_interpreter = Interpreter()
        module_interpreter.interpret(module_ast)

        # Expose module's global variables, functions, and albums
        # This is a simplified approach; a real module system might be more selective
        for var_name, var_value in module_interpreter.scopes[0].items():
            self.assign_variable(var_name, var_value)
        for func_name, func_node in module_interpreter.functions.items():
            self.functions[func_name] = func_node
        for album_name, album_node in module_interpreter.albums.items():
            self.albums[album_name] = album_node

    def visit_WaitFor(self, node):
        # Simulate an asynchronous task
        task_result = self.visit(node.task)
        print(f"Performing asynchronous task: {task_result}")
        time.sleep(1) # Simulate delay
        print("Asynchronous task completed.")

        # Execute the callback body
        self.push_scope()
        self.visit(node.callback_body)
        self.pop_scope()

    def visit_DecodeMessage(self, node):
        text = self.visit(node.text)
        pattern = self.visit(node.pattern)

        if not isinstance(text, str) or not isinstance(pattern, str):
            raise Exception("Type error: 'Decode The Message' expects strings for text and pattern.")

        match = re.search(pattern, text)
        if match:
            return match.group(0) # Return the first match
        return None # No match found

    def visit_ReadTheLetter(self, node):
        self.security_sandbox.check_permission("file_system_read")
        file_path = self.visit(node.file_path)
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Read The Letter' expects a string for file path.")
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")

    def visit_WriteInTheDiary(self, node):
        self.security_sandbox.check_permission("file_system_write")
        file_path = self.visit(node.file_path)
        content = self.visit(node.content)
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Write In The Diary' expects a string for file path.")
        if not isinstance(content, str):
            raise Exception("Type error: 'Write In The Diary' expects a string for content.")
        try:
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Error writing to file {file_path}: {e}")

    def visit_DoesTheVaultContain(self, node):
        self.security_sandbox.check_permission("file_system_read")
        file_path = self.visit(node.file_path)
        if not isinstance(file_path, str):
            raise Exception("Type error: 'Does The Vault Contain' expects a string for file path.")
        return os.path.exists(file_path)

    def visit_SpillYourGuts(self, node):
        user_input = input()
        self.assign_variable(node.variable_name, user_input)

    def visit_TellMeWhy(self, node):
        print("\n--- Debugger (Tell Me Why) ---")
        print("Current variables:")
        for scope in self.scopes:
            for var_name, var_value in scope.items():
                print(f"  {var_name}: {var_value}")
        print("-----------------------------")
        while True:
            command = input("Debugger (type 'continue' to resume): ").strip()
            if command == "continue":
                break
            elif command.startswith("inspect "):
                var_name = command.split(" ", 1)[1]
                try:
                    value = self.resolve_variable(var_name)
                    print(f"  {var_name}: {value}")
                except Exception as e:
                    print(f"  Error: {e}")
            else:
                print("Unknown command. Type 'continue' to resume or 'inspect <variable_name>' to inspect a variable.")
        print("--- Resuming execution ---")

    

    

    def visit_MatchStatement(self, node):
        value_to_match = self.visit(node.expression)
        matched = False
        for case in node.cases:
            pattern = self.visit(case.pattern)
            if self._match_pattern(value_to_match, pattern):
                self.push_scope()
                if case.alias:
                    self.assign_variable(case.alias, value_to_match)
                self.visit(case.body)
                self.pop_scope()
                matched = True
                break
        if not matched and node.default_case:
            self.push_scope()
            self.visit(node.default_case.body)
            self.pop_scope()

    def _match_pattern(self, value, pattern):
        # Simple pattern matching for now: direct equality or type checking
        if isinstance(pattern, dict) and pattern.get("__type__") == "LinerNotes":
            # Match Liner Notes (dictionaries)
            if not (isinstance(value, dict) and value.get("__type__") == "LinerNotes"):
                return False
            for key, p_val in pattern.items():
                if key == "__type__":
                    continue
                if key not in value or not self._match_pattern(value[key], p_val):
                    return False
            return True
        elif isinstance(pattern, list):
            # Match Tracklists (lists)
            if not isinstance(value, list) or len(value) != len(pattern):
                return False
            for i in range(len(pattern)):
                if not self._match_pattern(value[i], pattern[i]):
                    return False
            return True
        elif isinstance(pattern, Identifier) and pattern.name == "_": # Wildcard
            return True
        else:
            return value == pattern

    def visit_Assertion(self, node):
        expression_value = self.visit(node.expression)
        assertion_type = node.assertion_type
        expected_value = self.visit(node.expected_value) if node.expected_value else None

        if assertion_type == "to be":
            if expression_value != expected_value:
                raise Exception(f"Assertion Failed: Expected {expression_value} to be {expected_value}")
        elif assertion_type == "to not be":
            if expression_value == expected_value:
                raise Exception(f"Assertion Failed: Expected {expression_value} to not be {expected_value}")
        elif assertion_type == "to be greater than":
            if not (expression_value > expected_value):
                raise Exception(f"Assertion Failed: Expected {expression_value} to be greater than {expected_value}")
        elif assertion_type == "to be less than":
            if not (expression_value < expected_value):
                raise Exception(f"Assertion Failed: Expected {expression_value} to be less than {expected_value}")
        elif assertion_type == "to be true":
            if not bool(expression_value):
                raise Exception(f"Assertion Failed: Expected {expression_value} to be true")
        elif assertion_type == "to be false":
            if bool(expression_value):
                raise Exception(f"Assertion Failed: Expected {expression_value} to be false")
        elif assertion_type == "to throw an error":
            # This assertion requires special handling, as it asserts that an error *will* occur.
            # It's typically handled by wrapping the asserted code in a try-catch block within the test runner.
            # For now, we'll assume the interpreter will catch and report errors, and this assertion will pass if an error is caught.
            # A more robust implementation would involve a mechanism to check if an exception was raised during the evaluation of `node.expression`.
            pass
        else:
            raise Exception(f"Unknown assertion type: {assertion_type}")

    
