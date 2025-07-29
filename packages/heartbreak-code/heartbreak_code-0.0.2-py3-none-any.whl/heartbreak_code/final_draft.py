
# heartbreak_code/final_draft.py

class FinalDraft:
    """
    'The Final Draft': A Static Analysis and Linting Tool.
    Performs static analysis on HeartbreakCode projects to enforce code quality
    and find potential bugs before runtime.
    """
    def __init__(self):
        self.issues = []
        print("Final Draft linter initialized.")

    def analyze_code(self, code_content):
        """
        Analyzes the provided HeartbreakCode content for common anti-patterns and style violations.
        """
        self.issues = [] # Reset issues for each analysis
        print("Analyzing code for 'Final Draft'...")

        # Example checks (these would be much more sophisticated in a real linter)
        if "Would've, Could've, Should've" in code_content and "The story of us is..." not in code_content:
            self.issues.append({
                "type": "Style Warning",
                "message": "Consider defining variables before using conditional logic. 'The story of us is...' seems to be missing.",
                "lyrical_suggestion": "Every good story needs a beginning. Define your variables first."
            })

        if code_content.count("Perform 'Verse'") > 5:
            self.issues.append({
                "type": "Performance Hint",
                "message": "Excessive function calls might indicate a need for refactoring. Consider consolidating 'Verse' performances.",
                "lyrical_suggestion": "Too many encores can tire the audience. Streamline your performance."
            })

        if "unreachable_code_pattern" in code_content: # Placeholder for actual unreachable code detection
            self.issues.append({
                "type": "Bug Risk",
                "message": "Potential unreachable code detected. This code path may never be executed.",
                "lyrical_suggestion": "Don't leave any lyrics unsung. Ensure all your code can be reached."
            })

        print(f"Analysis complete. Found {len(self.issues)} issues.")
        return self.issues

    def generate_report(self):
        """
        Generates a lyrical report of the analysis findings.
        """
        if not self.issues:
            return "Your HeartbreakCode is a flawless masterpiece! No notes, just pure artistry."

        report = "\n--- The Final Draft Report ---\n"
        for i, issue in enumerate(self.issues):
            report += f"\nIssue {i+1}: {issue['type']}\n"
            report += f"  Message: {issue['message']}\n"
            report += f"  Lyrical Suggestion: {issue['lyrical_suggestion']}\n"
        report += "\n--- End of Report ---\n"
        return report


