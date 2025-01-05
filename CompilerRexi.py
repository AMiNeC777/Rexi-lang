from ply import lex, yacc

# --- Lexical Analysis ---
tokens = (
    # Keywords
    'IF', 'THEN', 'ELSE', 'END', 'WHILE', 'FOR', 'FUNCTION', 'RETURN', 'OUTPUT',
    # Types
    'TYPE',
    # Operators
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'ASSIGN',
    'GT', 'LT', 'GTE', 'LTE', 'EQUALS', 'NOTEQUALS',
    # Delimiters
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'SEMICOLON', 'COMMA',
    # Values
    'NUMBER', 'STRING', 'BOOLEAN', 'ID'
)

# Regular expressions for tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_GT = r'>'
t_LT = r'<'
t_GTE = r'>='
t_LTE = r'<='
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','

# Keywords
reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'end': 'END',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'output': 'OUTPUT',
    'IN': 'TYPE',
    'IR': 'TYPE',
    'STR': 'TYPE',
    'BINARY': 'TYPE',
    'TAB': 'TYPE',
}

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('left', 'GT', 'LT', 'GTE', 'LTE', 'EQUALS', 'NOTEQUALS'),
)
def t_COMMENT(t):
    r"""//.*"""
    pass

def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r"""\d*\.?\d+"""
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t


def t_STRING(t):
    r""""([^"\\]|\\.)*\""""
    t.value = t.value[1:-1]  # Remove quotes
    return t


def t_BOOLEAN(t):
    r"""YES|NO|true|false|0|1"""
    t.value = t.value in ('YES', 'true', '1')
    return t


# Ignored characters
t_ignore = ' \t'


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Base Node class
class Node:
    pass

# Program node
class Program(Node):
    def __init__(self, declarations):
        self.declarations = declarations

# Function node
class Function(Node):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

# Statement nodes
class WhileLoop(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop(Node):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class IfStatement(Node):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class Return(Node):
    def __init__(self, value):
        self.value = value

# Declaration nodes
class VarDeclaration(Node):
    def __init__(self, type_node, name, value):
        self.type_node = type_node
        self.name = name
        self.value = value

class ArrayDecl(Node):
    def __init__(self, type_node, name, size):
        self.type_node = type_node
        self.name = name
        self.size = size

# Expression nodes
class Assignment(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class ArrayAccess(Node):
    def __init__(self, array_name, index):
        self.array_name = array_name
        self.index = index

class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

# Value nodes
class Number(Node):
    def __init__(self, value):
        self.value = value

class String(Node):
    def __init__(self, value):
        self.value = value

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class Identifier(Node):
    def __init__(self, name):
        self.name = name


class SymbolTable:
    def __init__(self):
        # Initialize with global scope
        self.scopes = [{}]

    def enter_scope(self):
        """Create a new scope"""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope"""
        if len(self.scopes) > 1:  # Prevent exiting global scope
            self.scopes.pop()

    def declare(self, name, info):
        """Declare a new symbol in current scope"""
        if name in self.scopes[-1]:
            raise Exception(f"Symbol '{name}' already declared in current scope")
        self.scopes[-1][name] = info

    def lookup(self, name):
        """Look up a symbol in all accessible scopes"""
        # Search from innermost to outermost scope
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_in_current_scope(self, name):
        """Look up a symbol only in the current scope"""
        return self.scopes[-1].get(name)

    def update(self, name, info):
        """Update a symbol's information"""
        # Search from innermost to outermost scope
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = info
                return True
        raise Exception(f"Symbol '{name}' not found")

    def get_current_scope(self):
        """Get the current scope dictionary"""
        return self.scopes[-1]

    def get_all_symbols(self):
        """Get all accessible symbols from all scopes"""
        symbols = {}
        # Start from outermost scope
        for scope in self.scopes:
            symbols.update(scope)
        return symbols

# --- Règles d'analyse syntaxique complètes --- #

def p_program(p):
    """program : declarations"""
    p[0] = Program(p[1])

def p_declarations(p):
    """declarations : declaration
                   | declarations declaration"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaration(p):
    """declaration : var_declaration
                  | function_declaration
                  | statement"""
    p[0] = p[1]

def p_var_declaration(p):
    """var_declaration : TYPE ID ASSIGN expression SEMICOLON
                      | TYPE ID LBRACKET NUMBER RBRACKET SEMICOLON"""
    if len(p) == 6:
        p[0] = VarDeclaration(p[1], p[2], p[4])
    else:
        p[0] = ArrayDecl(p[1], p[2], p[4])

def p_function_declaration(p):
    """function_declaration : FUNCTION ID LPAREN param_list RPAREN TYPE block"""
    p[0] = Function(p[2], p[4], p[6], p[7])

def p_param_list(p):
    """param_list :
                 | param_list_not_empty"""
    p[0] = [] if len(p) == 1 else p[1]

def p_param_list_not_empty(p):
    """param_list_not_empty : param
                           | param_list_not_empty COMMA param"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    """param : TYPE ID"""
    p[0] = (p[1], p[2])

def p_block(p):
    """block : LBRACE statements RBRACE"""
    p[0] = p[2]

def p_statements(p):
    """statements :
                 | statement_list"""
    p[0] = [] if len(p) == 1 else p[1]

def p_statement_list(p):
    """statement_list : statement
                     | statement_list statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    """statement : var_declaration
                | assignment
                | if_statement
                | while_loop
                | for_loop
                | function_call SEMICOLON
                | return_statement
                | output_statement"""
    p[0] = p[1]

def p_assignment(p):
    """assignment : ID ASSIGN expression SEMICOLON
                 | array_access ASSIGN expression SEMICOLON"""
    if isinstance(p[1], str):
        p[0] = Assignment(p[1], p[3])
    else:
        p[0] = Assignment(p[1], p[3])

def p_if_statement(p):
    """if_statement : IF expression THEN block END
                   | IF expression THEN block ELSE block END"""
    if len(p) == 6:
        p[0] = IfStatement(p[2], p[4])
    else:
        p[0] = IfStatement(p[2], p[4], p[6])

def p_while_loop(p):
    """while_loop : WHILE expression block"""
    p[0] = WhileLoop(p[2], p[3])

def p_for_loop(p):
    """for_loop : FOR LPAREN assignment expression SEMICOLON assignment RPAREN block"""
    p[0] = ForLoop(p[3], p[4], p[6], p[8])

def p_expression(p):
    """expression : logical_or"""
    p[0] = p[1]

def p_logical_or(p):
    """logical_or : logical_and
                 | logical_or EQUALS logical_and
                 | logical_or NOTEQUALS logical_and"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinOp(p[1], p[2], p[3])

def p_logical_and(p):
    """logical_and : comparison
                  | logical_and GT comparison
                  | logical_and LT comparison
                  | logical_and GTE comparison
                  | logical_and LTE comparison"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinOp(p[1], p[2], p[3])

def p_comparison(p):
    """comparison : arithmetic"""
    p[0] = p[1]

def p_arithmetic(p):
    """arithmetic : term
                 | arithmetic PLUS term
                 | arithmetic MINUS term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinOp(p[1], p[2], p[3])

def p_term(p):
    """term : factor
            | term MULTIPLY factor
            | term DIVIDE factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinOp(p[1], p[2], p[3])

def p_factor(p):
    """factor : NUMBER
              | STRING
              | BOOLEAN
              | ID
              | array_access
              | function_call
              | LPAREN expression RPAREN"""
    if len(p) == 2:
        if isinstance(p[1], (int, float)):
            p[0] = Number(p[1])
        elif isinstance(p[1], bool):
            p[0] = Boolean(p[1])
        elif isinstance(p[1], str):
            if p[1] in ['true', 'false', 'YES', 'NO']:
                p[0] = Boolean(p[1] in ['true', 'YES'])
            else:
                p[0] = String(p[1]) if p[1].startswith('"') else Identifier(p[1])
        else:
            p[0] = p[1]
    else:
        p[0] = p[2]

def p_array_access(p):
    """array_access : ID LBRACKET expression RBRACKET"""
    p[0] = ArrayAccess(p[1], p[3])

def p_function_call(p):
    """function_call : ID LPAREN arg_list RPAREN"""
    p[0] = FunctionCall(p[1], p[3])

def p_arg_list(p):
    """arg_list :
                | arg_list_not_empty"""
    p[0] = [] if len(p) == 1 else p[1]

def p_arg_list_not_empty(p):
    """arg_list_not_empty : expression
                         | arg_list_not_empty COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_return_statement(p):
    """return_statement : RETURN expression SEMICOLON"""
    p[0] = Return(p[2])

def p_output_statement(p):
    """output_statement : OUTPUT expression SEMICOLON"""
    p[0] = Return(p[2])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")

# --- Code Generator amélioré --- #
class CodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0

    def generate_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def generate_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op, arg1=None, arg2=None, result_=None):
        instruction = (op, arg1, arg2, result_)
        self.code.append(instruction)
        return result_

    def generate_code(self, node):
        method_name = f'generate_{type(node).__name__.lower()}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        raise Exception(f"No visitor for {type(node).__name__}")

    def generate_program(self, node):
        for decl in node.declarations:
            self.generate_code(decl)
        return self.code

    def generate_function(self, node):
        # Function label
        func_label = self.emit('LABEL', node.name)

        # Generate code for function body
        for stmt in node.body:
            self.generate_code(stmt)

        # Add return if not present
        self.emit('RETURN', None)
        return func_label

    def generate_functioncall(self, node):
        # Generate code for arguments
        args = []
        for arg in node.args:
            arg_temp = self.generate_code(arg)
            args.append(arg_temp)

        # Call function and store result
        result = self.generate_temp()
        self.emit('CALL', node.name, args, result)
        return result

    def generate_vardeclaration(self, node):
        if node.value:
            value = self.generate_code(node.value)
            self.emit('ASSIGN', value, None, node.name)
        else:
            self.emit('DECLARE', node.name, node.type_node)
        return node.name

    def generate_assignment(self, node):
        value = self.generate_code(node.value)
        self.emit('ASSIGN', value, None, node.name)
        return node.name

    def generate_binop(self, node):
        left = self.generate_code(node.left)
        right = self.generate_code(node.right)
        result = self.generate_temp()
        self.emit(node.op, left, right, result)
        return result

    def generate_ifstatement(self, node):
        cond = self.generate_code(node.condition)
        else_label = self.generate_label()
        end_label = self.generate_label()

        self.emit('JUMPIF', cond, else_label)

        # Generate if body
        for stmt in node.if_body:
            self.generate_code(stmt)

        self.emit('JUMP', end_label)

        # Generate else body if exists
        self.emit('LABEL', else_label)
        if node.else_body:
            for stmt in node.else_body:
                self.generate_code(stmt)

        self.emit('LABEL', end_label)
        return None

    def generate_whileloop(self, node):
        start_label = self.generate_label()
        end_label = self.generate_label()

        self.emit('LABEL', start_label)
        cond = self.generate_code(node.condition)
        self.emit('JUMPIF', cond, end_label)

        # Generate loop body
        for stmt in node.body:
            self.generate_code(stmt)

        self.emit('JUMP', start_label)
        self.emit('LABEL', end_label)
        return None

    def generate_return(self, node):
        if node.value:
            value = self.generate_code(node.value)
            self.emit('RETURN', value)
        else:
            self.emit('RETURN', None)
        return None

    def generate_number(self, node):
        temp = self.generate_temp()
        self.emit('LOAD_CONST', node.value, None, temp)
        return temp

    def generate_string(self, node):
        temp = self.generate_temp()
        self.emit('LOAD_CONST', node.value, None, temp)
        return temp

    def generate_boolean(self, node):
        temp = self.generate_temp()
        self.emit('LOAD_CONST', node.value, None, temp)
        return temp

    def generate_identifier(self, node):
        temp = self.generate_temp()
        self.emit('LOAD', node.name, None, temp)
        return temp

    def generate_arrayaccess(self, node):
        index = self.generate_code(node.index)
        result = self.generate_temp()
        self.emit('ARRAY_ACCESS', node.array_name, index, result)
        return result


# --- Main compilation function ---
def compile_code(source_code):
    try:
        # Initialize lexer and parser
        lexer = lex.lex()
        parser = yacc.yacc()

        # Lexical and Syntax Analysis
        ast = parser.parse(source_code, lexer=lexer)
        if not ast:
            raise Exception("Parsing failed to produce an AST")
        # Code Generation
        code_generator = CodeGenerator()
        generated_code = code_generator.generate_code(ast)

        return generated_code

    except Exception as e:
        return f"Compilation error: {str(e)}"

# Test the compiler
test_program = """
function calculate(IN x, IN y) IN {
    IN result = x + y;
    return result;
}

IN a = 5;
IN b = 10;
IN sum = calculate(a, b);
output sum;
"""
def Run(source_code):
    out = ""
    result = compile_code(source_code)
    for instruction in result:
        out += f"{instruction}\n"
    return out
