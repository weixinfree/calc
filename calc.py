from ply import lex

from default_funcs import UNARY, BINARY, CONSTANT


class CalcException(BaseException):
    pass


'''
lex
'''

tokens = (
    'NAME',
    'NUMBER',
    'EQUAL',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'POWER'
)

t_POWER = r'\*\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUAL = r'\='
t_COMMA = r','


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t


def t_NUMBER(t: lex.LexToken):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t


t_ignore = ' \t\n;'


def t_newline(t):
    r'\n+'
    print('error', t)
    t.lexer.lineno += len(t.value)


def t_error(t: lex.LexToken):
    print('t_error', t)
    t.lexer.skip(1)


lexer = lex.lex()

'''
yacc
'''

precedence = (
    ('right', 'POWER'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS')
)

names = {}
names.update(CONSTANT)


def p_statement_assign(t):
    'statement : NAME EQUAL expression'
    _, name, _, value = t
    names[name] = value
    print(f'assign: {name} = {value}')


def p_statement_expr(t):
    'statement : expression'
    names['_'] = t[1]
    print(f'expr: {t[1]}')


binop_map = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y
}


def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]


def p_expression_biary_func(t):
    'expression : NAME LPAREN expression COMMA expression RPAREN'
    func = t[1]
    if func not in BINARY:
        raise CalcException(f"不支持的二元函数 {func}")
    t[0] = BINARY[func](t[3], t[5])


def p_expression_unary_func(t):
    'expression : NAME LPAREN expression RPAREN'
    func = t[1]
    if func not in UNARY:
        raise CalcException(f"不支持的一元函数 {func}")

    t[0] = UNARY[func](t[3])


def p_expresion_power(t):
    "expression : expression POWER expression"
    t[0] = t[1] ** t[3]


def p_expression_binop(t):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression"""
    _, left, op, right = t
    t[0] = binop_map[op](left, right)


def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = - t[2]


def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]


def p_exression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError as e:
        print(f'unknown name: {t[1]}')
        t[0] = 0


def p_error(t):
    print('error', t)


from ply import yacc

parser = yacc.yacc()

if __name__ == '__main__':
    while True:
        try:
            s = input('calc > ')
            if s.strip() == 'exit':
                exit(0)

            parser.parse(s)
        except CalcException as e:
            print(e)
        except EOFError:
            break
