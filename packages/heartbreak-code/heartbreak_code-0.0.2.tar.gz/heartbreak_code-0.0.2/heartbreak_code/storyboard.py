
import re
from heartbreak_code.tokenizer import Tokenizer
from heartbreak_code.parser import Parser


class Storyboard:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def render(self, template_path: str, context: dict = None) -> str:
        """
        Renders a HeartbreakCode template file.
        :param template_path: Absolute path to the template file.
        :param context: A dictionary of variables to make available in the template's scope.
        :return: Rendered HTML content.
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            raise Exception(f"Template file not found: {template_path}")
        except Exception as e:
            raise Exception(f"Error reading template file {template_path}: {e}")

        # Push a new scope for the template context
        self.interpreter.push_scope()
        if context:
            for key, value in context.items():
                self.interpreter.assign_variable(key, value)

        rendered_content = []
        last_pos = 0

        # Regex to find {{ expression }} and {% statement %} blocks
        # This regex is designed to capture either type of block
        # Group 1: expression content (for {{...}})
        # Group 2: statement content (for {%...}})
        template_pattern = re.compile(r'\{\{\s*(.*?)\s*\}\}|\{\%\s*(.*?)\s*\%\}', re.DOTALL)

        for match in template_pattern.finditer(template_content):
            # Add the HTML content before the current match
            rendered_content.append(template_content[last_pos:match.start()])

            expression_content = match.group(1)
            statement_content = match.group(2)

            if expression_content is not None:
                # Handle {{ expression }}
                try:
                    # Tokenize, parse, and interpret the expression
                    # For expressions, we want to capture the return value of the last statement
                    # or the evaluation of the expression itself.
                    # We'll wrap it in a Speak Now to capture output.
                    hc_code = f"Speak Now: ({expression_content})"
                    output = self.interpreter.render_code(hc_code)
                    rendered_content.append(str(output).strip()) # Strip to remove potential newlines from Speak Now
                except Exception as e:
                    rendered_content.append(f"<!-- Error rendering expression: {e} -->")
            elif statement_content is not None:
                # Handle {% statement %}
                try:
                    # Tokenize, parse, and interpret the statement(s)
                    # Statements might produce output via Speak Now, or modify state.
                    # We'll capture any Speak Now output.
                    output = self.interpreter.render_code(statement_content)
                    if output:
                        rendered_content.append(str(output))
                except Exception as e:
                    rendered_content.append(f"<!-- Error executing statement: {e} -->")
            
            last_pos = match.end()

        # Add any remaining HTML content after the last match
        rendered_content.append(template_content[last_pos:])

        # Pop the scope after rendering
        self.interpreter.pop_scope()

        return "".join(rendered_content)

