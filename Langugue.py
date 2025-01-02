# Lexical Analysis
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
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_number(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_identifier(self):
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
                if identifier in ['true', 'false']:
                    return Token('BOOLEAN', identifier == 'true')
                if identifier == 'if':
                    return Token('IF', identifier)
                if identifier == 'else':
                    return Token('ELSE', identifier)
                return Token('ID', identifier)

            if self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{')
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}')
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


# Abstract Syntax Tree nodes
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


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
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


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


# Parser
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def block(self):
        """Parse a block of statements between braces"""
        self.eat('LBRACE')
        statements = []
        while self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        self.eat('RBRACE')
        return Block(statements)

    def if_statement(self):
        """Parse if statement with optional else"""
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')

        if_block = self.block()

        else_block = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_block = self.block()

        return IfStatement(condition, if_block, else_block)

    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Num(token)
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

    def term(self):
        node = self.factor()
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
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

    def assignment(self):
        var = Variable(self.current_token)
        self.eat('ID')
        token = self.current_token
        self.eat('ASSIGN')
        expr = self.expr()
        self.eat('SEMICOLON')
        return Assign(var, token, expr)

    def statement(self):
        if self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'ID':
            return self.assignment()
        else:
            node = self.expr()
            self.eat('SEMICOLON')
            return node

    def program(self):
        """Parse a program (multiple statements)"""
        statements = []
        while self.current_token.type != 'EOF':
            statements.append(self.statement())
        return Block(statements)

    def parse(self):
        return self.program()


# Interpreter
class Interpreter:
    def __init__(self):
        self.variables = {}

    def visit_Block(self, node):
        for statement in node.statements:
            self.visit(statement)
        return None

    def visit_IfStatement(self, node):
        if self.visit(node.condition):
            return self.visit(node.if_block)
        elif node.else_block:
            return self.visit(node.else_block)
        return None

    def visit_BinOp(self, node):
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

    def visit_Boolean(self, node):
        return node.value

    def visit_Variable(self, node):
        var_name = node.value
        if var_name not in self.variables:
            raise NameError(f'Variable {var_name} is not defined')
        return self.variables[var_name]

    def visit_Assign(self, node):
        var_name = node.left.value
        self.variables[var_name] = self.visit(node.right)
        return self.variables[var_name]

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def interpret(self, tree):
        return self.visit(tree)


# Example usage
def main():
    # Test cases with if-else statements and blocks
    tests = [
        """
        x = 5;
        y = 3;
        if (x > y) {
            result = x + y;
            doubled = result * 2;
        } else {
            result = x - y;
            doubled = result * 2;
        }
        """,
        """
        a = 10;
        b = 20;
        if (a < b) {
            max = b;
            min = a;
        }
        diff = max - min;
        """
    ]

    interpreter = Interpreter()
    for test in tests:
        try:
            lexer = Lexer(test)
            parser = Parser(lexer)
            tree = parser.parse()
            result = interpreter.interpret(tree)
            print(f"Program:\n{test}")
            print(f"Variables: {interpreter.variables}\n")
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == '__main__':
    main()