import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Tokenizer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.position = 0
        self.token_specs = [
            ("SKIP", r"\s+"),
            ("COMMENT", r"#.*"),

            # Multi-word keywords - ordered from longest to shortest to avoid partial matches
            ("IS_GREATER_THAN_OR_EQUAL_TO", r"is greater than or equal to"),
            ("IS_LESS_THAN_OR_EQUAL_TO", r"is less than or equal to"),
            ("ON_REPEAT_AS_LONG_AS", r"On Repeat as long as"),
            ("LOOK_WHAT_YOU_MADE_ME_DO", r"Look what you made me do:"),
            ("THIS_IS_ME_TRYING", r"This is me trying:"),
            ("DOES_THE_VAULT_CONTAIN", r"Does The Vault Contain"),
            ("THE_FINAL_WORD_IS", r"The final word is"),
            ("THEN_SPEAK_NOW", r"Then Speak Now:"),
            ("NEW_RECORD_OF", r"a new Record of"),
            ("LINER_NOTES_ARE", r"Liner Notes are"),
            ("READ_THE_LETTER", r"Read The Letter"),
            ("WRITE_IN_THE_DIARY", r"Write In The Diary"),
            ("SPILL_YOUR_GUTS", r"Spill Your Guts"),
            ("TELL_ME_WHY", r"Tell Me Why"),
            ("UNTANGLE_STORY", r"Untangle The Story"),
            ("WEAVE_STORY", r"Weave The Story"),
            ("LOOK_IN_THE_MIRROR", r"Look In The Mirror"),
            ("DECODE_MESSAGE", r"Decode The Message"),
            ("SEND_MESSAGE", r"Send Message"),
            ("TO_URL", r"to URL"),
            ("WITH_METHOD", r"with method"),
            ("WITH_HEADERS", r"with headers"),
            ("WITH_BODY", r"with body"),
            ("OPEN_THE_ARCHIVES", r"Open The Archives"),
            ("CLOSE_THE_ARCHIVES", r"Close The Archives"),
            ("QUERY_THE_ARCHIVES", r"Query The Archives"),
            ("CREATE_ARCHIVE_TABLE", r"Create Archive Table"),
            ("INSERT_INTO_ARCHIVE", r"Insert Into Archive"),
            ("SELECT_FROM_ARCHIVE", r"Select From Archive"),
            ("UPDATE_ARCHIVE", r"Update Archive"),
            ("DELETE_FROM_ARCHIVES", r"Delete From Archives"),
            ("INSTALL_ALBUM", r"Install Album"),
            ("PUBLISH_ALBUM", r"Publish Album"),
            ("SEARCH_ALBUMS", r"Search Albums"),
            ("DEFINE_SETLIST_ROUTE", r"Define Setlist Route"),
            ("START_THE_SETLIST", r"Start The Setlist"),
            ("STOP_THE_SETLIST", r"Stop The Setlist"),
            ("SETLIST_RESPONSE_SEND", r"Setlist Response Send"),
            ("SETLIST_RESPONSE_JSON", r"Setlist Response JSON"),
            ("SETLIST_RESPONSE_STATUS", r"Setlist Response Status"),
            ("SETLIST_REQUEST_PATH", r"Setlist Request Path"),
            ("SETLIST_REQUEST_METHOD", r"Setlist Request Method"),
            ("SETLIST_REQUEST_BODY", r"Setlist Request Body"),
            ("SETLIST_REQUEST_HEADER", r"Setlist Request Header"),
            ("FOR_VERSE", r"for verse"),
            ("ON_PORT", r"on port"),

            # The Choreography: Build Automation and Task Runner
            ("DEFINE_CHOREOGRAPHY", r"Define Choreography"),
            ("RUN_CHOREOGRAPHY", r"Run Choreography"),
            ("RUN_HEARTBREAK_CODE_CHOREOGRAPHY", r"Run HeartbreakCode Choreography"),

            # Mastermind Structural Pattern Matching
            ("MATCH", r"Match"),
            ("CASE", r"Case"),
            ("AS", r"as"),
            ("DEFAULT", r"Default"),
            ("END_CASE", r"End Case"),
            ("END_MATCH", r"End Match"),

            # Safe & Sound Runtime Security Sandbox
            ("GRANT_PERMISSION", r"Grant Permission"),
            ("REVOKE_PERMISSION", r"Revoke Permission"),

            # Concurrency keywords
            ("BACKUP_DANCER", r"Backup Dancer"),
            ("PERFORM_IN_PARALLEL", r"Perform in Parallel"),

            # LSP keywords
            ("LSP_START", r"Start The Producer's Notes"),
            ("LSP_STOP", r"Stop The Producer's Notes"),
            ("LSP_PROVIDE_COMPLETIONS", r"Provide Completions"),
            ("LSP_DIAGNOSE", r"Diagnose"),
            ("LSP_GO_TO_DEFINITION", r"Go To Definition"),
            ("LSP_HOVER", r"Hover Over"),

            # Generics keywords
            ("GENERIC", r"Generic"),
            ("TYPE_OF", r"type of"),

            # Soundcheck keywords
            ("END_SOUNDCHECK", r"End Soundcheck"),
            ("END_TEST", r"End Test"),
            ("I_EXPECT", r"I expect"),
            ("TO_BE_GREATER_THAN", r"to be greater than"),
            ("TO_BE_LESS_THAN", r"to be less than"),
            ("TO_NOT_BE", r"to not be"),
            ("TO_BE", r"to be"),
            ("TO_BE_TRUE", r"to be true"),
            ("TO_BE_FALSE", r"to be false"),
            ("TO_THROW_AN_ERROR", r"to throw an error"),
            ("SOUNDCHECK", r"Soundcheck"),
            ("TEST", r"Test"),

            # Two-word keywords
            ("IS_GREATER_THAN", r"is greater than"),
            ("IS_LESS_THAN", r"is less than"),
            ("DEFINE_VERSE", r"Define Verse"),
            ("END_VERSE", r"End Verse"),
            ("END_REPEAT", r"End Repeat"),
            ("FOR_EVERY", r"For every"),
            ("END_TOUR", r"End Tour"),
            ("DEFINE_ALBUM", r"Define Album"),
            ("END_ALBUM", r"End Album"),
            ("END_AFTERGLOW", r"End Afterglow"),
            ("ITS_OVER_NOW", r"It's over now:"),
            ("THE_TRACKLIST_IS", r"The tracklist is"),
            ("THE_VERSES_ARE", r"The verses are"),
            ("ASSIGN", r"The story of us is"),

            # Single-word keywords and operators
            ("SPEAK_NOW", r"Speak Now:"),
            ("WOULD_HAVE", r"Would've"),
            ("COULD_HAVE", r"Could've"),
            ("SHOULD_HAVE", r"Should've"),
            ("PERFORM", r"Perform"),
            ("FEATURING", r"Featuring"),
            ("IS_NOT", r"is not"),
            ("IS", r"is"),
            ("IN", r"in"),
            ("FEATURE", r"Feature"),
            ("WAIT_FOR", r"wait for"),
            ("PLUS", r"\+"),
            ("MINUS", r"-"),
            ("MULTIPLY", r"\*"),
            ("DIVIDE", r"/"),
            ("EXCLAMATION", r"!"),
            ("ON", r"on"),
            ("EQUALS", r"="),
            ("DOT", r"\."),
            ("COLON", r":"),
            ("COMMA", r","),
            ("L_BRACKET", r"\["),
            ("R_BRACKET", r"\]"),
            ("L_CURLY_BRACE", r"\{"),
            ("R_CURLY_BRACE", r"\}"),

            # Literals
            ("STRING_SINGLE", r"'(?:[^']|.)*'"),
            ("STRING_DOUBLE", r'"(?:[^"]|.)*"'),
            ("NUMBER", r"\d+"),

            # Catch-all for identifiers (must be last)
            ("WILDCARD", r"_"),
            ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("UNKNOWN", r"."),
        ]

    def tokenize(self):
        while self.position < len(self.source_code):
            match = None
            for token_type, pattern in self.token_specs:
                regex = re.compile(pattern)
                m = regex.match(self.source_code, self.position)
                if m:
                    match = m
                    if token_type != "SKIP":
                        self.tokens.append(Token(token_type, m.group(0)))
                    break
            if match:
                self.position = match.end(0)
            else:
                raise Exception(f"Unexpected character: {self.source_code[self.position]}")
        return self.tokens