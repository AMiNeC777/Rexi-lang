# Analyse Lexicale - Transforme le texte source en tokens
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def error(self):
        raise Exception('Caractère invalide')

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        # Ignorer les espaces blancs
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_number(self):
        # Gérer les nombres entiers et réels
        result = ''
        is_float = False
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                is_float = True
            result += self.current_char
            self.advance()
        return float(result) if is_float else int(result)

    def get_identifier(self):
        # Récupérer les identifiants et mots-clés
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token('NUMBER', self.get_number())

            if self.current_char.isalpha():
                identifier = self.get_identifier()
                # Mots-clés du langage Rexi
                if identifier in ['YES', 'NO', '0', '1']:
                    return Token('BOOLEAN', identifier in ['YES', '1'])
                if identifier == 'if':
                    return Token('IF', identifier)
                if identifier == 'then':
                    return Token('THEN', identifier)
                if identifier == 'else':
                    return Token('ELSE', identifier)
                if identifier == 'end':
                    return Token('END', identifier)
                if identifier == 'output':
                    return Token('OUTPUT', identifier)
                if identifier in ['IN', 'IR', 'STR', 'BINARY', 'TAB']:
                    return Token('TYPE', identifier)
                return Token('ID', identifier)

            # Opérateurs et symboles
            if self.current_char == '"':
                self.advance()
                string = ''
                while self.current_char and self.current_char != '"':
                    string += self.current_char
                    self.advance()
                self.advance()  # Consommer le guillemet fermant
                return Token('STRING', string)

            if self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{')
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}')
            if self.current_char == '[':
                self.advance()
                return Token('LBRACKET', '[')
            if self.current_char == ']':
                self.advance()
                return Token('RBRACKET', ']')
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('EQUALS', '==')
                return Token('ASSIGN', '=')
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('GTE', '>=')
                return Token('GT', '>')
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('LTE', '<=')
                return Token('LT', '<')
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            if self.current_char == ';':
                self.advance()
                return Token('SEMICOLON', ';')

            self.error()

        return Token('EOF', None)

# Nœuds de l'arbre syntaxique abstrait
class AST:
    pass

class Block(AST):
    def __init__(self, statements):
        self.statements = statements

class IfStatement(AST):
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

class OutputStatement(AST):
    def __init__(self, expression):
        self.expression = expression

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Boolean(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Variable(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Declaration(AST):
    def __init__(self, type_node, var_node, value_node):
        self.type_node = type_node
        self.var_node = var_node
        self.value_node = value_node

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Erreur de syntaxe')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        """Point d'entrée du programme"""
        statements = []
        while self.current_token.type != 'EOF':
            statements.append(self.statement())
        return Block(statements)

    def statement(self):
        """Analyse d'une instruction"""
        if self.current_token.type == 'TYPE':
            return self.declaration()
        elif self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'OUTPUT':
            return self.output_statement()
        elif self.current_token.type == 'ID':
            return self.assignment()
        else:
            node = self.expr()
            self.eat('SEMICOLON')
            return node

    def declaration(self):
        """Analyse d'une déclaration de variable"""
        type_token = self.current_token
        self.eat('TYPE')
        var_token = self.current_token
        self.eat('ID')
        self.eat('ASSIGN')
        value_node = self.expr()
        self.eat('SEMICOLON')
        return Declaration(type_token, Variable(var_token), value_node)

    def assignment(self):
        """Analyse d'une assignation"""
        var = Variable(self.current_token)
        self.eat('ID')
        token = self.current_token
        self.eat('ASSIGN')
        expr = self.expr()
        self.eat('SEMICOLON')
        return Assign(var, token, expr)

    def if_statement(self):
        """Analyse d'une structure conditionnelle"""
        self.eat('IF')
        condition = self.expr()
        self.eat('THEN')
        if_block_statements = []
        while self.current_token.type not in ['END', 'ELSE']:
            if_block_statements.append(self.statement())
        if_block = Block(if_block_statements)

        else_block = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_block_statements = []
            while self.current_token.type != 'END':
                else_block_statements.append(self.statement())
            else_block = Block(else_block_statements)

        self.eat('END')
        return IfStatement(condition, if_block, else_block)

    def output_statement(self):
        """Analyse d'une instruction output"""
        self.eat('OUTPUT')
        expr = self.expr()
        self.eat('SEMICOLON')
        return OutputStatement(expr)

    def expr(self):
        """Analyse d'une expression"""
        node = self.term()
        while self.current_token.type in ('PLUS', 'MINUS', 'GT', 'LT', 'GTE', 'LTE', 'EQUALS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
            elif token.type == 'MINUS':
                self.eat('MINUS')
            elif token.type == 'GT':
                self.eat('GT')
            elif token.type == 'LT':
                self.eat('LT')
            elif token.type == 'GTE':
                self.eat('GTE')
            elif token.type == 'LTE':
                self.eat('LTE')
            elif token.type == 'EQUALS':
                self.eat('EQUALS')
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        """Analyse d'un terme"""
        node = self.factor()
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        """Analyse d'un facteur"""
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Num(token)
        elif token.type == 'STRING':
            self.eat('STRING')
            return String(token)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return Boolean(token)
        elif token.type == 'ID':
            self.eat('ID')
            return Variable(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        self.error()

    def parse(self):
        """Lance l'analyse syntaxique"""
        return self.program()


# Interpréteur - Exécute l'arbre syntaxique
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.output_buffer = []

    def visit_Block(self, node):
        """Exécute un bloc d'instructions"""
        for statement in node.statements:
            self.visit(statement)
        return None

    def visit_Declaration(self, node):
        """Gère la déclaration de variable avec type"""
        var_name = node.var_node.value
        var_value = self.visit(node.value_node)

        # Vérification de type
        type_name = node.type_node.value
        if type_name == 'IN' and not isinstance(var_value, int):
            raise TypeError(f"La variable {var_name} doit être de type IN")
        elif type_name == 'IR' and not isinstance(var_value, (int, float)):
            raise TypeError(f"La variable {var_name} doit être de type IR")
        elif type_name == 'STR' and not isinstance(var_value, str):
            raise TypeError(f"La variable {var_name} doit être de type STR")
        elif type_name == 'BINARY' and not isinstance(var_value, bool):
            raise TypeError(f"La variable {var_name} doit être de type BINARY")

        self.variables[var_name] = var_value
        return var_value

    def visit_IfStatement(self, node):
        """Exécute une structure conditionnelle"""
        if self.visit(node.condition):
            return self.visit(node.if_block)
        elif node.else_block:
            return self.visit(node.else_block)
        return None

    def visit_OutputStatement(self, node):
        """Exécute une instruction output"""
        value = self.visit(node.expression)
        self.output_buffer.append(str(value))
        return value

    def visit_BinOp(self, node):
        """Exécute une opération binaire"""
        if node.op.type == 'PLUS':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == 'MINUS':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == 'MULTIPLY':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == 'DIVIDE':
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == 'GT':
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == 'LT':
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == 'GTE':
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == 'LTE':
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == 'EQUALS':
            return self.visit(node.left) == self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_Boolean(self, node):
        return node.value

    def visit_Variable(self, node):
        var_name = node.value
        if var_name not in self.variables:
            raise NameError(f'Variable {var_name} non définie')
        return self.variables[var_name]

    def visit_Assign(self, node):
        var_name = node.left.value
        if var_name not in self.variables:
            raise NameError(f'Variable {var_name} non déclarée')
        self.variables[var_name] = self.visit(node.right)
        return self.variables[var_name]

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Pas de méthode visit_{type(node).__name__}')

    def interpret(self, tree):
        """Lance l'interprétation"""
        return self.visit(tree)


# Fonction principale d'exécution
def execute_rexi(source_code):
    try:
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        interpreter = Interpreter()

        tree = parser.parse()
        interpreter.interpret(tree)

        # Retourne les sorties et l'état final des variables
        return {
            'output': interpreter.output_buffer,
            'variables': interpreter.variables
        }
    except Exception as e:
        return {
            'error': str(e)
        }


# Exemple d'utilisation
def Run (source_code) :
    # Programme de test
    program = """
    IN age = 25;
    STR nom = "Alice";
    BINARY estMajeur = YES;

    if age >= 18 then
        output "Majeur";
        output nom;
    else
        output "Mineur";
    end
    """

    result = execute_rexi(source_code)
    if 'error' in result:
        out  = f"Erreur: {result['error']}\n"
    else:
        out = f"Sorties:{result['output']}\n"
        out += f"Variables:{result['variables']}\n"
    return out
