import json
import requests

class ASTNode:
    pass

class AlbumDefinition(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class RecordInstantiation(ASTNode):
    def __init__(self, album_name, args):
        self.album_name = album_name
        self.args = args

class MemberAccess(ASTNode):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

class TryCatchFinally(ASTNode):
    def __init__(self, try_body, catch_body, finally_body):
        self.try_body = try_body
        self.catch_body = catch_body
        self.finally_body = finally_body

class LinerNotesLiteral(ASTNode):
    def __init__(self, pairs):
        self.pairs = pairs

class LinerNotesAccess(ASTNode):
    def __init__(self, liner_notes, key):
        self.liner_notes = liner_notes
        self.key = key

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

class SpeakNow(ASTNode):
    def __init__(self, value):
        self.value = value

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class String(ASTNode):
    def __init__(self, value):
        self.value = value

class IfStatement(ASTNode):
    def __init__(self, condition, body, else_if_blocks=None, else_block=None):
        self.condition = condition
        self.body = body
        self.else_if_blocks = else_if_blocks if else_if_blocks is not None else []
        self.else_block = else_block

class ElseIfStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ElseStatement(ASTNode):
    def __init__(self, body):
        self.body = body

class Comparison(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class FunctionDefinition(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class TracklistLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class TracklistAccess(ASTNode):
    def __init__(self, tracklist, index):
        self.tracklist = tracklist
        self.index = index

class WhileLoop(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop(ASTNode):
    def __init__(self, item_name, tracklist, body):
        self.item_name = item_name
        self.tracklist = tracklist
        self.body = body

class FunctionDefinition(ASTNode):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

class FeatureImport(ASTNode):
    def __init__(self, file_name):
        self.file_name = file_name

class WaitFor(ASTNode):
    def __init__(self, task, callback_body):
        self.task = task
        self.callback_body = callback_body

class DecodeMessage(ASTNode):
    def __init__(self, text, pattern):
        self.text = text
        self.pattern = pattern

class ReadTheLetter(ASTNode):
    def __init__(self, file_path):
        self.file_path = file_path

class WriteInTheDiary(ASTNode):
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content

class DoesTheVaultContain(ASTNode):
    def __init__(self, file_path):
        self.file_path = file_path

class SpillYourGuts(ASTNode):
    def __init__(self, variable_name):
        self.variable_name = variable_name

class SendMessage(ASTNode):
    def __init__(self, url, method, headers, body):
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body

class UntangleStory(ASTNode):
    def __init__(self, json_string):
        self.json_string = json_string

class WeaveStory(ASTNode):
    def __init__(self, liner_notes_or_tracklist):
        self.liner_notes_or_tracklist = liner_notes_or_tracklist

class LookInTheMirror(ASTNode):
    def __init__(self, target, aspect):
        self.target = target
        self.aspect = aspect

class InstallAlbum(ASTNode):
    def __init__(self, album_name):
        self.album_name = album_name

class PublishAlbum(ASTNode):
    def __init__(self, album_path):
        self.album_path = album_path

class SearchAlbums(ASTNode):
    def __init__(self, query):
        self.query = query

class DefineSetlistRoute(ASTNode):
    def __init__(self, method, path, handler_verse_name):
        self.method = method
        self.path = path
        self.handler_verse_name = handler_verse_name

class StartTheSetlist(ASTNode):
    def __init__(self, port):
        self.port = port

class StopTheSetlist(ASTNode):
    def __init__(self):
        pass

class SetlistResponseSend(ASTNode):
    def __init__(self, content):
        self.content = content

class SetlistResponseJson(ASTNode):
    def __init__(self, data):
        self.data = data

class SetlistResponseStatus(ASTNode):
    def __init__(self, code):
        self.code = code

class SetlistRequestPath(ASTNode):
    def __init__(self):
        pass

class SetlistRequestMethod(ASTNode):
    def __init__(self):
        pass

class SetlistRequestBody(ASTNode):
    def __init__(self):
        pass

class SetlistRequestHeader(ASTNode):
    def __init__(self, header_name):
        self.header_name = header_name

class LookInTheMirror(ASTNode):
    def __init__(self, target, aspect):
        self.target = target
        self.aspect = aspect

class OpenTheArchives(ASTNode):
    def __init__(self, db_name):
        self.db_name = db_name

class CloseTheArchives(ASTNode):
    def __init__(self):
        pass

class QueryTheArchives(ASTNode):
    def __init__(self, query, params):
        self.query = query
        self.params = params

class CreateArchiveTable(ASTNode):
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

class InsertIntoArchive(ASTNode):
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data

class SelectFromArchive(ASTNode):
    def __init__(self, table_name, columns, where_clause, params):
        self.table_name = table_name
        self.columns = columns
        self.where_clause = where_clause
        self.params = params

class UpdateArchive(ASTNode):
    def __init__(self, table_name, set_clause, where_clause, params):
        self.table_name = table_name
        self.set_clause = set_clause
        self.where_clause = where_clause
        self.params = params

class DeleteFromArchive(ASTNode):
    def __init__(self, table_name, where_clause, params):
        self.table_name = table_name
        self.where_clause = where_clause
        self.params = params

class TellMeWhy(ASTNode):
    def __init__(self):
        pass

class SoundcheckSuite(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class TestDefinition(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class BackupDancerDefinition(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class PerformInParallel(ASTNode):
    def __init__(self, verse_name, arguments):
        self.verse_name = verse_name
        self.arguments = arguments

class LSPStart(ASTNode):
    def __init__(self):
        pass

class LSPStop(ASTNode):
    def __init__(self):
        pass

class LSPProvideCompletions(ASTNode):
    def __init__(self):
        pass

class LSPDiagnose(ASTNode):
    def __init__(self):
        pass

class LSPGoToDefinition(ASTNode):
    def __init__(self):
        pass

class LSPHover(ASTNode):
    def __init__(self):
        pass

class GenericType(ASTNode):
    def __init__(self, type_param):
        self.type_param = type_param

class TypeOf(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class MatchStatement(ASTNode):
    def __init__(self, expression, cases, default_case=None):
        self.expression = expression
        self.cases = cases
        self.default_case = default_case

class CaseBlock(ASTNode):
    def __init__(self, pattern, body, alias=None):
        self.pattern = pattern
        self.body = body
        self.alias = alias

class DefaultCase(ASTNode):
    def __init__(self, body):
        self.body = body

class Assertion(ASTNode):
    def __init__(self, expression, assertion_type, expected_value=None):
        self.expression = expression
        self.assertion_type = assertion_type
        self.expected_value = expected_value

class GrantPermission(ASTNode):
    def __init__(self, permission_type):
        self.permission_type = permission_type

class RevokePermission(ASTNode):
    def __init__(self, permission_type):
        self.permission_type = permission_type

class GrantPermission(ASTNode):
    def __init__(self, permission_type):
        self.permission_type = permission_type

class RevokePermission(ASTNode):
    def __init__(self, permission_type):
        self.permission_type = permission_type

class DefineChoreography(ASTNode):
    def __init__(self, name, command):
        self.name = name
        self.command = command

class RunChoreography(ASTNode):
    def __init__(self, name):
        self.name = name

class RunHeartbreakCodeChoreography(ASTNode):
    def __init__(self, verse_name):
        self.verse_name = verse_name

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def advance(self):
        self.position += 1
        self.current_token = self.tokens[self.position] if self.position < len(self.tokens) else None

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def parse(self):
        statements = []
        while self.current_token:
            if self.current_token.type == "COMMENT":
                self.eat("COMMENT")
                continue
            statements.append(self.parse_statement())
        return Program(statements)

    def assignment_statement(self):
        self.eat("ASSIGN")
        identifier_token = self.current_token
        self.eat("IDENTIFIER")
        value = self.expression()
        return Assignment(identifier_token.value, value)

    def speak_now_statement(self):
        self.eat("SPEAK_NOW")
        value = self.expression()
        return SpeakNow(value)

    def expression(self):
        token = self.current_token
        if token.type == "STRING_SINGLE" or token.type == "STRING_DOUBLE":
            self.eat(token.type)
            return String(token.value.strip("'").strip('"'))
        elif token.type == "NUMBER":
            self.eat("NUMBER")
            return Number(int(token.value))
        elif token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
            if self.current_token and self.current_token.type == "L_BRACKET":
                return self.tracklist_access(Identifier(token.value))
            elif self.current_token and self.current_token.type == "DOT":
                return self.member_access(Identifier(token.value))
            return Identifier(token.value)
        elif token.type == "L_BRACKET":
            return self.tracklist_literal()
        elif token.type == "LINER_NOTES_ARE":
            return self.liner_notes_literal()
        elif token.type == "DECODE_MESSAGE":
            return self.decode_message_expression()
        elif token.type == "SEND_MESSAGE":
            return self.send_message_statement()
        elif token.type == "UNTANGLE_STORY":
            return self.untangle_story_statement()
        elif token.type == "WEAVE_STORY":
            return self.weave_story_statement()
        elif token.type == "LOOK_IN_THE_MIRROR":
            return self.look_in_the_mirror_statement()
        elif self.current_token.type == "SETLIST_REQUEST_PATH":
            return self.setlist_request_path_statement()
        elif self.current_token.type == "SETLIST_REQUEST_METHOD":
            return self.setlist_request_method_statement()
        elif self.current_token.type == "SETLIST_REQUEST_BODY":
            return self.setlist_request_body_statement()
        elif self.current_token.type == "SETLIST_REQUEST_HEADER":
            return self.setlist_request_header_statement()
        elif self.current_token.type == "TYPE_OF":
            return self.type_of_expression()
        # Soundcheck expressions
        elif self.current_token.type == "I_EXPECT":
            return self.assertion_statement()
        else:
            raise Exception(f"Expected an expression, got {token.type}")

    def soundcheck_suite_statement(self):
        self.eat("SOUNDCHECK")
        name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_SOUNDCHECK":
            body.append(self.parse_statement())
        self.eat("END_SOUNDCHECK")
        return SoundcheckSuite(name, Program(body))

    def test_definition_statement(self):
        self.eat("TEST")
        name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_TEST":
            body.append(self.parse_statement())
        self.eat("END_TEST")
        return TestDefinition(name, Program(body))

    def assertion_statement(self):
        self.eat("I_EXPECT")
        expression = self.expression()
        assertion_type = None
        expected_value = None

        if self.current_token.type == "TO_BE":
            self.eat("TO_BE")
            assertion_type = "to be"
            expected_value = self.expression()
        elif self.current_token.type == "TO_NOT_BE":
            self.eat("TO_NOT_BE")
            assertion_type = "to not be"
            expected_value = self.expression()
        elif self.current_token.type == "TO_BE_GREATER_THAN":
            self.eat("TO_BE_GREATER_THAN")
            assertion_type = "to be greater than"
            expected_value = self.expression()
        elif self.current_token.type == "TO_BE_LESS_THAN":
            self.eat("TO_BE_LESS_THAN")
            assertion_type = "to be less than"
            expected_value = self.expression()
        elif self.current_token.type == "TO_BE_TRUE":
            self.eat("TO_BE_TRUE")
            assertion_type = "to be true"
        elif self.current_token.type == "TO_BE_FALSE":
            self.eat("TO_BE_FALSE")
            assertion_type = "to be false"
        elif self.current_token.type == "TO_THROW_AN_ERROR":
            self.eat("TO_THROW_AN_ERROR")
            assertion_type = "to throw an error"
        else:
            raise Exception(f"Expected an assertion type, got {self.current_token.type}")
        
        return Assertion(expression, assertion_type, expected_value)

    def install_album_statement(self):
        self.eat("INSTALL_ALBUM")
        album_name = self.expression()
        return InstallAlbum(album_name)

    def publish_album_statement(self):
        self.eat("PUBLISH_ALBUM")
        album_path = self.expression()
        return PublishAlbum(album_path)

    def search_albums_statement(self):
        self.eat("SEARCH_ALBUMS")
        query = self.expression()
        return SearchAlbums(query)

    def define_setlist_route_statement(self):
        self.eat("DEFINE_SETLIST_ROUTE")
        method = self.expression()
        self.eat("STRING_SINGLE") # Assuming path is a string literal
        path = self.tokens[self.position - 1].value.strip("'").strip('"')
        self.eat("FOR_VERSE") # New token for 'for verse'
        self.eat("STRING_SINGLE") # Assuming handler verse name is a string literal
        handler_verse_name = self.tokens[self.position - 1].value.strip("'").strip('"')
        return DefineSetlistRoute(method, path, handler_verse_name)

    def start_the_setlist_statement(self):
        self.eat("START_THE_SETLIST")
        port = None
        if self.current_token and self.current_token.type == "ON_PORT":
            self.eat("ON_PORT")
            port = self.expression()
        return StartTheSetlist(port)

    def stop_the_setlist_statement(self):
        self.eat("STOP_THE_SETLIST")
        return StopTheSetlist()

    def setlist_response_send_statement(self):
        self.eat("SETLIST_RESPONSE_SEND")
        content = self.expression()
        return SetlistResponseSend(content)

    def setlist_response_json_statement(self):
        self.eat("SETLIST_RESPONSE_JSON")
        data = self.expression()
        return SetlistResponseJson(data)

    def setlist_response_status_statement(self):
        self.eat("SETLIST_RESPONSE_STATUS")
        code = self.expression()
        return SetlistResponseStatus(code)

    def setlist_request_path_statement(self):
        self.eat("SETLIST_REQUEST_PATH")
        return SetlistRequestPath()

    def setlist_request_method_statement(self):
        self.eat("SETLIST_REQUEST_METHOD")
        return SetlistRequestMethod()

    def setlist_request_body_statement(self):
        self.eat("SETLIST_REQUEST_BODY")
        return SetlistRequestBody()

    def setlist_request_header_statement(self):
        self.eat("SETLIST_REQUEST_HEADER")
        header_name = self.expression()
        return SetlistRequestHeader(header_name)

    def open_the_archives_statement(self):
        self.eat("OPEN_THE_ARCHIVES")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # db_name=
        self.eat("EQUALS")
        db_name = self.expression()
        return OpenTheArchives(db_name)

    def close_the_archives_statement(self):
        self.eat("CLOSE_THE_ARCHIVES")
        return CloseTheArchives()

    def query_the_archives_statement(self):
        self.eat("QUERY_THE_ARCHIVES")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # query=
        self.eat("EQUALS")
        query = self.expression()
        params = []
        if self.current_token and self.current_token.type == "COMMA":
            self.eat("COMMA")
            self.eat("IDENTIFIER") # params=
            self.eat("EQUALS")
            # Assuming params will be a tracklist literal for now
            if self.current_token and self.current_token.type == "L_BRACKET":
                params = self.tracklist_literal()
            else:
                raise Exception("Expected a tracklist for query parameters.")
        return QueryTheArchives(query, params)

    def create_archive_table_statement(self):
        self.eat("CREATE_ARCHIVE_TABLE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # table_name=
        self.eat("EQUALS")
        table_name = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # columns=
        self.eat("EQUALS")
        columns = self.liner_notes_literal()
        return CreateArchiveTable(table_name, columns)

    def insert_into_archive_statement(self):
        self.eat("INSERT_INTO_ARCHIVE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # table_name=
        self.eat("EQUALS")
        table_name = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # data=
        self.eat("EQUALS")
        data = self.liner_notes_literal()
        return InsertIntoArchive(table_name, data)

    def select_from_archive_statement(self):
        self.eat("SELECT_FROM_ARCHIVE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # table_name=
        self.eat("EQUALS")
        table_name = self.expression()
        columns = String('*') # Default to all columns
        if self.current_token and self.current_token.type == "COMMA":
            self.eat("COMMA")
            self.eat("IDENTIFIER") # columns=
            self.eat("EQUALS")
            columns = self.expression()
        where_clause = None
        params = []
        if self.current_token and self.current_token.type == "COMMA":
            self.eat("COMMA")
            self.eat("IDENTIFIER") # params=
            self.eat("EQUALS")
            if self.current_token and self.current_token.type == "L_BRACKET":
                params = self.tracklist_literal()
            else:
                raise Exception("Expected a tracklist for select parameters.")
        return SelectFromArchive(table_name, columns, where_clause, params)

    def update_archive_statement(self):
        self.eat("UPDATE_ARCHIVE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # table_name=
        self.eat("EQUALS")
        table_name = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # set_clause=
        self.eat("EQUALS")
        set_clause = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # where_clause=
        self.eat("EQUALS")
        where_clause = self.expression()
        params = []
        if self.current_token and self.current_token.type == "COMMA":
            self.eat("COMMA")
            self.eat("IDENTIFIER") # params=
            self.eat("EQUALS")
            if self.current_token and self.current_token.type == "L_BRACKET":
                params = self.tracklist_literal()
            else:
                raise Exception("Expected a tracklist for update parameters.")
        return UpdateArchive(table_name, set_clause, where_clause, params)

    def delete_from_archive_statement(self):
        self.eat("DELETE_FROM_ARCHIVES")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # table_name=
        self.eat("EQUALS")
        table_name = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # where_clause=
        self.eat("EQUALS")
        where_clause = self.expression()
        params = []
        if self.current_token and self.current_token.type == "COMMA":
            self.eat("COMMA")
            self.eat("IDENTIFIER") # params=
            self.eat("EQUALS")
            if self.current_token and self.current_token.type == "L_BRACKET":
                params = self.tracklist_literal()
            else:
                raise Exception("Expected a tracklist for delete parameters.")
        return DeleteFromArchive(table_name, where_clause, params)

    def function_definition(self):
        self.eat("DEFINE_VERSE")
        self.eat("STRING_SINGLE")
        name = self.tokens[self.position - 1].value.strip("''")
        parameters = []
        if self.current_token and self.current_token.type == "FEATURING":
            self.eat("FEATURING")
            while self.current_token and self.current_token.type == "IDENTIFIER":
                parameters.append(self.current_token.value)
                self.eat("IDENTIFIER")
                if self.current_token and self.current_token.type == "COMMA":
                    self.eat("COMMA")
        self.eat("COLON") # Eat the colon after function name/parameters
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_VERSE":
            body.append(self.parse_statement())
        self.eat("END_VERSE")
        return FunctionDefinition(name, parameters, Program(body))

    def function_call(self):
        self.eat("PERFORM")
        self.eat("STRING_SINGLE")
        name = self.tokens[self.position - 1].value.strip("''")
        arguments = {}
        if self.current_token and self.current_token.type == "FEATURING":
            self.eat("FEATURING")
            while self.current_token and self.current_token.type == "IDENTIFIER":
                param_name = self.current_token.value
                self.eat("IDENTIFIER")
                self.eat("EQUALS")
                param_value = self.expression()
                arguments[param_name] = param_value
                if self.current_token and self.current_token.type == "COMMA":
                    self.eat("COMMA")
        return FunctionCall(name, arguments)

    def return_statement(self):
        self.eat("THE_FINAL_WORD_IS")
        value = self.expression()
        return ReturnStatement(value)

    def album_definition(self):
        self.eat("DEFINE_ALBUM")
        name = self.current_token.value
        self.eat("IDENTIFIER")
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_ALBUM":
            body.append(self.parse_statement())
        self.eat("END_ALBUM")
        return AlbumDefinition(name, Program(body))

    def record_instantiation(self):
        self.eat("NEW_RECORD_OF")
        album_name = self.current_token.value
        self.eat("IDENTIFIER")
        args = {}
        if self.current_token and self.current_token.type == "FEATURING":
            self.eat("FEATURING")
            while self.current_token and self.current_token.type == "IDENTIFIER":
                param_name = self.current_token.value
                self.eat("IDENTIFIER")
                self.eat("EQUALS")
                param_value = self.expression()
                args[param_name] = param_value
                if self.current_token and self.current_token.type == "COMMA":
                    self.eat("COMMA")
        return RecordInstantiation(album_name, args)

    def try_catch_finally_statement(self):
        self.eat("THIS_IS_ME_TRYING")
        self.eat("SPEAK_NOW")
        try_body = []
        while self.current_token and self.current_token.type not in ("LOOK_WHAT_YOU_MADE_ME_DO", "ITS_OVER_NOW", "END_TRYING"):
            try_body.append(self.parse_statement())
        
        catch_body = None
        if self.current_token and self.current_token.type == "LOOK_WHAT_YOU_MADE_ME_DO":
            self.eat("LOOK_WHAT_YOU_MADE_ME_DO")
            self.eat("SPEAK_NOW")
            catch_body = []
            while self.current_token and self.current_token.type not in ("ITS_OVER_NOW", "END_TRYING"):
                catch_body.append(self.parse_statement())
            catch_body = Program(catch_body)

        finally_body = None
        if self.current_token and self.current_token.type == "ITS_OVER_NOW":
            self.eat("ITS_OVER_NOW")
            self.eat("SPEAK_NOW")
            finally_body = []
            while self.current_token and self.current_token.type != "END_TRYING":
                finally_body.append(self.parse_statement())
            finally_body = Program(finally_body)

        self.eat("END_TRYING")
        return TryCatchFinally(Program(try_body), catch_body, finally_body)

    def liner_notes_literal(self):
        self.eat("LINER_NOTES_ARE")
        self.eat("L_CURLY_BRACE")
        pairs = {}
        while self.current_token and self.current_token.type != "R_CURLY_BRACE":
            key = self.current_token.value
            self.eat("IDENTIFIER")
            self.eat("COLON")
            value = self.expression()
            pairs[key] = value
            if self.current_token and self.current_token.type == "COMMA":
                self.eat("COMMA")
        self.eat("R_CURLY_BRACE")
        return LinerNotesLiteral(pairs)

    def member_access(self, obj_node):
        self.eat("DOT")
        member_name = self.current_token.value
        self.eat("IDENTIFIER")
        return MemberAccess(obj_node, member_name)

    def parse_statement(self):
        if self.current_token.type == "ASSIGN":
            return self.assignment_statement()
        elif self.current_token.type == "SPEAK_NOW":
            return self.speak_now_statement()
        elif self.current_token.type == "WOULD_HAVE":
            return self.if_statement()
        elif self.current_token.type == "ON_REPEAT_AS_LONG_AS":
            return self.while_loop_statement()
        elif self.current_token.type == "FOR_EVERY":
            return self.for_loop_statement()
        elif self.current_token.type == "DEFINE_VERSE":
            return self.function_definition()
        elif self.current_token.type == "PERFORM":
            return self.function_call()
        elif self.current_token.type == "THE_FINAL_WORD_IS":
            return self.return_statement()
        elif self.current_token.type == "DEFINE_ALBUM":
            return self.album_definition()
        elif self.current_token.type == "NEW_RECORD_OF":
            return self.record_instantiation()
        elif self.current_token.type == "THIS_IS_ME_TRYING":
            return self.try_catch_finally_statement()
        elif self.current_token.type == "FEATURE":
            return self.feature_import_statement()
        elif self.current_token.type == "WAIT_FOR":
            return self.wait_for_statement()
        elif self.current_token.type == "READ_THE_LETTER":
            return self.read_the_letter_statement()
        elif self.current_token.type == "WRITE_IN_THE_DIARY":
            return self.write_in_the_diary_statement()
        elif self.current_token.type == "DOES_THE_VAULT_CONTAIN":
            return self.does_the_vault_contain_statement()
        elif self.current_token.type == "SPILL_YOUR_GUTS":
            return self.spill_your_guts_statement()
        elif self.current_token.type == "TELL_ME_WHY":
            return self.tell_me_why_statement()
        elif self.current_token.type == "SOUNDCHECK":
            return self.soundcheck_suite_statement()
        elif self.current_token.type == "TEST":
            return self.test_definition_statement()
        elif self.current_token.type == "INSTALL_ALBUM":
            return self.install_album_statement()
        elif self.current_token.type == "PUBLISH_ALBUM":
            return self.publish_album_statement()
        elif self.current_token.type == "SEARCH_ALBUMS":
            return self.search_albums_statement()
        elif self.current_token.type == "DEFINE_SETLIST_ROUTE":
            return self.define_setlist_route_statement()
        elif self.current_token.type == "START_THE_SETLIST":
            return self.start_the_setlist_statement()
        elif self.current_token.type == "STOP_THE_SETLIST":
            return self.stop_the_setlist_statement()
        elif self.current_token.type == "SETLIST_RESPONSE_SEND":
            return self.setlist_response_send_statement()
        elif self.current_token.type == "SETLIST_RESPONSE_JSON":
            return self.setlist_response_json_statement()
        elif self.current_token.type == "SETLIST_RESPONSE_STATUS":
            return self.setlist_response_status_statement()
        elif self.current_token.type == "OPEN_THE_ARCHIVES":
            return self.open_the_archives_statement()
        elif self.current_token.type == "CLOSE_THE_ARCHIVES":
            return self.close_the_archives_statement()
        elif self.current_token.type == "QUERY_THE_ARCHIVES":
            return self.query_the_archives_statement()
        elif self.current_token.type == "CREATE_ARCHIVE_TABLE":
            return self.create_archive_table_statement()
        elif self.current_token.type == "INSERT_INTO_ARCHIVE":
            return self.insert_into_archive_statement()
        elif self.current_token.type == "SELECT_FROM_ARCHIVE":
            return self.select_from_archive_statement()
        elif self.current_token.type == "UPDATE_ARCHIVE":
            return self.update_archive_statement()
        elif self.current_token.type == "DELETE_FROM_ARCHIVES":
            return self.delete_from_archive_statement()
        elif self.current_token.type == "BACKUP_DANCER":
            return self.backup_dancer_definition()
        elif self.current_token.type == "PERFORM_IN_PARALLEL":
            return self.perform_in_parallel_statement()
        elif self.current_token.type == "LSP_START":
            return self.lsp_start_statement()
        elif self.current_token.type == "LSP_STOP":
            return self.lsp_stop_statement()
        elif self.current_token.type == "LSP_PROVIDE_COMPLETIONS":
            return self.lsp_provide_completions_statement()
        elif self.current_token.type == "LSP_DIAGNOSE":
            return self.lsp_diagnose_statement()
        elif self.current_token.type == "LSP_GO_TO_DEFINITION":
            return self.lsp_go_to_definition_statement()
        elif self.current_token.type == "LSP_HOVER":
            return self.lsp_hover_statement()
        elif self.current_token.type == "MATCH":
            return self.match_statement()
        elif self.current_token.type == "DEFINE_CHOREOGRAPHY":
            return self.define_choreography_statement()
        elif self.current_token.type == "RUN_CHOREOGRAPHY":
            return self.run_choreography_statement()
        elif self.current_token.type == "RUN_HEARTBREAK_CODE_CHOREOGRAPHY":
            return self.run_heartbreak_code_choreography_statement()
        elif self.current_token.type == "GRANT_PERMISSION":
            return self.grant_permission_statement()
        elif self.current_token.type == "REVOKE_PERMISSION":
            return self.revoke_permission_statement()
        else:
            raise Exception(f"Unknown statement type: {self.current_token.type}")

    def match_statement(self):
        self.eat("MATCH")
        expression = self.expression()
        self.eat("SPEAK_NOW")
        cases = []
        default_case = None
        while self.current_token and self.current_token.type in ("CASE", "DEFAULT"):
            if self.current_token.type == "CASE":
                self.eat("CASE")
                pattern = self.expression()
                alias = None
                if self.current_token and self.current_token.type == "AS":
                    self.eat("AS")
                    alias = self.current_token.value
                    self.eat("IDENTIFIER")
                self.eat("SPEAK_NOW")
                body = []
                while self.current_token and self.current_token.type != "END_CASE":
                    body.append(self.parse_statement())
                self.eat("END_CASE")
                cases.append(CaseBlock(pattern, Program(body), alias))
            elif self.current_token.type == "DEFAULT":
                self.eat("DEFAULT")
                self.eat("SPEAK_NOW")
                body = []
                while self.current_token and self.current_token.type != "END_CASE":
                    body.append(self.parse_statement())
                self.eat("END_CASE")
                default_case = DefaultCase(Program(body))
        self.eat("END_MATCH")
        return MatchStatement(expression, cases, default_case)

    def if_statement(self):
        self.eat("WOULD_HAVE")
        condition = self.comparison_expression()
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type not in ("COULD_HAVE", "SHOULD_HAVE", "END_VERSE"):
            body.append(self.parse_statement())
        
        else_if_blocks = []
        while self.current_token and self.current_token.type == "COULD_HAVE":
            self.eat("COULD_HAVE")
            else_if_condition = self.comparison_expression()
            self.eat("SPEAK_NOW")
            else_if_body = []
            while self.current_token and self.current_token.type not in ("COULD_HAVE", "SHOULD_HAVE", "END_VERSE"):
                else_if_body.append(self.parse_statement())
            else_if_blocks.append(ElseIfStatement(else_if_condition, Program(else_if_body)))

        else_block = None
        if self.current_token and self.current_token.type == "SHOULD_HAVE":
            self.eat("SHOULD_HAVE")
            self.eat("SPEAK_NOW")
            else_body = []
            while self.current_token and self.current_token.type != "END_VERSE":
                else_body.append(self.parse_statement())
            else_block = ElseStatement(Program(else_body))
        
        self.eat("END_VERSE") # Assuming 'End Verse' closes the entire if-else-if-else block
        return IfStatement(condition, Program(body), else_if_blocks, else_block)

    def comparison_expression(self):
        left = self.expression()
        operator = self.current_token.value
        if self.current_token.type == "IS":
            self.eat("IS")
        elif self.current_token.type == "IS_NOT":
            self.eat("IS_NOT")
        elif self.current_token.type == "IS_GREATER_THAN":
            self.eat("IS_GREATER_THAN")
        elif self.current_token.type == "IS_LESS_THAN":
            self.eat("IS_LESS_THAN")
        elif self.current_token.type == "IS_GREATER_THAN_OR_EQUAL_TO":
            self.eat("IS_GREATER_THAN_OR_EQUAL_TO")
        elif self.current_token.type == "IS_LESS_THAN_OR_EQUAL_TO":
            self.eat("IS_LESS_THAN_OR_EQUAL_TO")
        else:
            raise Exception(f"Expected a comparison operator, got {self.current_token.type}")
        right = self.expression()
        return Comparison(left, operator, right)

    def tracklist_literal(self):
        self.eat("L_BRACKET")
        elements = []
        while self.current_token and self.current_token.type != "R_BRACKET":
            elements.append(self.expression())
            if self.current_token and self.current_token.type == "COMMA":
                self.eat("COMMA")
        self.eat("R_BRACKET")
        return TracklistLiteral(elements)

    def tracklist_access(self, tracklist_node):
        self.eat("L_BRACKET")
        index = self.expression()
        self.eat("R_BRACKET")
        return TracklistAccess(tracklist_node, index)

    def while_loop_statement(self):
        self.eat("ON_REPEAT_AS_LONG_AS")
        condition = self.comparison_expression()
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_REPEAT":
            body.append(self.parse_statement())
        self.eat("END_REPEAT")
        return WhileLoop(condition, Program(body))

    def for_loop_statement(self):
        self.eat("FOR_EVERY")
        item_name = self.current_token.value
        self.eat("IDENTIFIER")
        self.eat("IN")
        tracklist = self.expression()
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_TOUR":
            body.append(self.parse_statement())
        self.eat("END_TOUR")
        return ForLoop(item_name, tracklist, Program(body))

    def feature_import_statement(self):
        self.eat("FEATURE")
        file_name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        return FeatureImport(file_name)

    def wait_for_statement(self):
        self.eat("WAIT_FOR")
        task = self.expression()
        self.eat("THEN_SPEAK_NOW")
        callback_body = []
        while self.current_token and self.current_token.type != "END_AFTERGLOW":
            callback_body.append(self.parse_statement())
        self.eat("END_AFTERGLOW")
        return WaitFor(task, Program(callback_body))

    def decode_message_expression(self):
        self.eat("DECODE_MESSAGE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # text=
        self.eat("EQUALS")
        text = self.expression()
        self.eat("COMMA")
        self.eat("IDENTIFIER") # pattern=
        self.eat("EQUALS")
        pattern = self.expression()
        return DecodeMessage(text, pattern)

    def read_the_letter_statement(self):
        self.eat("READ_THE_LETTER")
        file_path = self.expression()
        return ReadTheLetter(file_path)

    def write_in_the_diary_statement(self):
        self.eat("WRITE_IN_THE_DIARY")
        file_path = self.expression()
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # content=
        self.eat("EQUALS")
        content = self.expression()
        return WriteInTheDiary(file_path, content)

    def does_the_vault_contain_statement(self):
        self.eat("DOES_THE_VAULT_CONTAIN")
        file_path = self.expression()
        return DoesTheVaultContain(file_path)

    def spill_your_guts_statement(self):
        self.eat("SPILL_YOUR_GUTS")
        variable_name = self.current_token.value
        self.eat("IDENTIFIER")
        return SpillYourGuts(variable_name)

    def tell_me_why_statement(self):
        self.eat("TELL_ME_WHY")
        return TellMeWhy()

    def send_message_statement(self):
        self.eat("SEND_MESSAGE")
        self.eat("TO_URL")
        url = self.expression()
        self.eat("WITH_METHOD")
        method = self.expression()
        headers = None
        if self.current_token and self.current_token.type == "WITH_HEADERS":
            self.eat("WITH_HEADERS")
            headers = self.expression()
        body = None
        if self.current_token and self.current_token.type == "WITH_BODY":
            self.eat("WITH_BODY")
            body = self.expression()
        return SendMessage(url, method, headers, body)

    def untangle_story_statement(self):
        self.eat("UNTANGLE_STORY")
        json_string = self.expression()
        return UntangleStory(json_string)

    def weave_story_statement(self):
        self.eat("WEAVE_STORY")
        liner_notes_or_tracklist = self.expression()
        return WeaveStory(liner_notes_or_tracklist)

    def look_in_the_mirror_statement(self):
        self.eat("LOOK_IN_THE_MIRROR")
        aspect = None
        if self.current_token and self.current_token.type in ("THE_TRACKLIST_IS", "THE_VERSES_ARE"):
            if self.current_token.type == "THE_TRACKLIST_IS":
                self.eat("THE_TRACKLIST_IS")
                aspect = "properties of"
            elif self.current_token.type == "THE_VERSES_ARE":
                self.eat("THE_VERSES_ARE")
                aspect = "verses of"
        target = self.expression()
        return LookInTheMirror(target, aspect)

    def backup_dancer_definition(self):
        self.eat("BACKUP_DANCER")
        name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        self.eat("SPEAK_NOW")
        body = []
        while self.current_token and self.current_token.type != "END_VERSE": # Assuming Backup Dancer uses End Verse
            body.append(self.parse_statement())
        self.eat("END_VERSE")
        return BackupDancerDefinition(name, Program(body))

    def perform_in_parallel_statement(self):
        self.eat("PERFORM_IN_PARALLEL")
        self.eat("STRING_SINGLE")
        verse_name = self.tokens[self.position - 1].value.strip("''")
        arguments = {}
        if self.current_token and self.current_token.type == "FEATURING":
            self.eat("FEATURING")
            while self.current_token and self.current_token.type == "IDENTIFIER":
                param_name = self.current_token.value
                self.eat("IDENTIFIER")
                self.eat("EQUALS")
                param_value = self.expression()
                arguments[param_name] = param_value
                if self.current_token and self.current_token.type == "COMMA":
                    self.eat("COMMA")
        return PerformInParallel(verse_name, arguments)

    def lsp_start_statement(self):
        self.eat("LSP_START")
        return LSPStart()

    def lsp_stop_statement(self):
        self.eat("LSP_STOP")
        return LSPStop()

    def lsp_provide_completions_statement(self):
        self.eat("LSP_PROVIDE_COMPLETIONS")
        return LSPProvideCompletions()

    def lsp_diagnose_statement(self):
        self.eat("LSP_DIAGNOSE")
        return LSPDiagnose()

    def lsp_go_to_definition_statement(self):
        self.eat("LSP_GO_TO_DEFINITION")
        return LSPGoToDefinition()

    def lsp_hover_statement(self):
        self.eat("LSP_HOVER")
        return LSPHover()

    def type_of_expression(self):
        self.eat("TYPE_OF")
        expression = self.expression()
        return TypeOf(expression)

    def define_choreography_statement(self):
        self.eat("DEFINE_CHOREOGRAPHY")
        name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        self.eat("FEATURING")
        self.eat("IDENTIFIER") # command=
        self.eat("EQUALS")
        command = self.expression()
        return DefineChoreography(name, command)

    def run_choreography_statement(self):
        self.eat("RUN_CHOREOGRAPHY")
        name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        return RunChoreography(name)

    def run_heartbreak_code_choreography_statement(self):
        self.eat("RUN_HEARTBREAK_CODE_CHOREOGRAPHY")
        verse_name = self.current_token.value.strip("'").strip('"')
        self.eat("STRING_SINGLE")
        return RunHeartbreakCodeChoreography(verse_name)

    def grant_permission_statement(self):
        self.eat("GRANT_PERMISSION")
        permission_type = self.expression()
        return GrantPermission(permission_type)

    def revoke_permission_statement(self):
        self.eat("REVOKE_PERMISSION")
        permission_type = self.expression()
        return RevokePermission(permission_type)

