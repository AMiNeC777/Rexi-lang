Digits = '0123456789'

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MULT = 'MULT'
TT_DIV = 'DIV'
TT_RPAR = 'RPAR'
TT_LPAR = 'LPAR'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


class Error:
    def __init__(self,spos, epos,  error_name, details):
        self.spos = spos
        self.epos = epos
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'File {self.spos} , line {self.epos}'
        return result



class IllegalCharError(Error):
    def __init__(self,spos, epos, details):
        super().__init__(spos, epos , 'IllegalCharError', details)

class Position :
    def __init__(self,idx, col,ln ,fname, ftext):
        self.idx=idx
        self.fname = fname
        self.ftext  = ftext
        self.col=col
        self.ln = ln
    def advance(self,curr_char):
        self.idx += 1
        self.col += 1
        if curr_char == '\n' :
            self.ln += 1
            self.idx = 0
            return self
    def copy(self):
        return Position(self.idx,self.col,self.ln,self.fname,self.ftext)


class Lexer:
    def __init__(self, fn ,text):
        self.text = text
        self.fn = fn
        self.pos = Position(-1,-1,0 , fn, text)
        self.curr_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.curr_char)
        self.curr_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.curr_char is not None:
            if self.curr_char in ' \t':
                self.advance()
            elif self.curr_char in Digits or self.curr_char == '.':
                tokens.append(self.make_number())
            elif self.curr_char == '+':
                tokens.append(Token(TT_PLUS, self.curr_char))
                self.advance()
            elif self.curr_char == '-':
                tokens.append(Token(TT_MINUS, self.curr_char))
                self.advance()
            elif self.curr_char == '*':
                tokens.append(Token(TT_MULT, self.curr_char))
                self.advance()
            elif self.curr_char == '/':
                tokens.append(Token(TT_DIV, self.curr_char))
                self.advance()
            elif self.curr_char == '(':
                tokens.append(Token(TT_LPAR, self.curr_char))
                self.advance()
            elif self.curr_char == ')':
                tokens.append(Token(TT_RPAR, self.curr_char))
                self.advance()
            else:
                spos = self.pos.copy()
                char = self.curr_char
                self.advance()
                return [], IllegalCharError(spos,self.pos,f"'{char}' {self.make_tokens()}" )
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.curr_char is not None and (self.curr_char in Digits or self.curr_char == '.'):
            if self.curr_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += self.curr_char
            else:
                num_str += self.curr_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

class NumNode :
    def __init__(self, tok):
        self.tok = tok
    def __repr__(self):
        return f'{self.tok}'
class BinOpNode :
    def __init__(self , leftnode , op , rightnode):
        self.leftnode = leftnode
        self.rightnode = rightnode
        self.op = op
    def __repr__(self):
        return f'{self.rightnode} , {self.op} , {self.leftnode} '

class Paraser :
    def __init__(self ,tokens_):
        self.tokens = tokens_
        self.tok_idx = 1
        self.advance()
        self.curr_tok = None
    def advance (self) :
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens) :
            self.curr_tok = self.tokens[self.tok_idx]
        return  self.curr_tok
    def factor (self , ):
        tok = self.curr_tok
        if tok.type in (TT_INT , TT_FLOAT) :
            self.advance()
            return NumNode(tok)

    def terme (self ,) :
        left








def run(fn ,text):
    lexer = Lexer(fn ,text)
    tokens, error = lexer.make_tokens()
    return tokens, error