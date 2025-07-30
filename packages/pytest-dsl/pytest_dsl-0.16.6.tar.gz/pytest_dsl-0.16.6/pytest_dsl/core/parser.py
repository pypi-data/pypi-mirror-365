import ply.yacc as yacc
from pytest_dsl.core.lexer import tokens


class Node:
    def __init__(self, type, children=None, value=None, line_number=None,
                 column=None):
        self.type = type
        self.children = children if children else []
        self.value = value
        self.line_number = line_number  # 添加行号信息
        self.column = column  # 添加列号信息

    def set_position(self, line_number, column=None):
        """设置节点位置信息"""
        self.line_number = line_number
        self.column = column
        return self

    def get_position_info(self):
        """获取位置信息的字符串表示"""
        if self.line_number is not None:
            if self.column is not None:
                return f"行{self.line_number}:列{self.column}"
            else:
                return f"行{self.line_number}"
        return "位置未知"


# 定义优先级和结合性
precedence = (
    ('left', 'COMMA'),
    ('left', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE'),  # 比较运算符优先级
    ('left', 'PLUS', 'MINUS'),  # 加减运算符优先级
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),  # 乘除模运算符优先级
    ('right', 'EQUALS'),
)


def p_start(p):
    '''start : metadata statements teardown
             | metadata statements
             | statements teardown
             | statements'''

    # 获取起始行号
    line_number = getattr(p.slice[1], 'lineno', 1) if len(p) > 1 else 1

    if len(p) == 4:
        p[0] = Node('Start', [p[1], p[2], p[3]], line_number=line_number)
    elif len(p) == 3:
        # 判断第二个元素是teardown还是statements
        if p[2].type == 'Teardown':
            p[0] = Node('Start', [Node('Metadata', [],
                                       line_number=line_number), p[1], p[2]],
                        line_number=line_number)
        else:
            p[0] = Node('Start', [p[1], p[2]], line_number=line_number)
    else:
        # 没有metadata和teardown
        p[0] = Node('Start', [Node('Metadata', [],
                    line_number=line_number), p[1]], line_number=line_number)


def p_metadata(p):
    '''metadata : metadata_items
                | empty'''
    if p[1]:
        p[0] = Node('Metadata', p[1])
    else:
        p[0] = Node('Metadata', [])


def p_empty(p):
    '''empty :'''
    p[0] = None


def p_metadata_items(p):
    '''metadata_items : metadata_item metadata_items
                     | metadata_item'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_metadata_item(p):
    '''metadata_item : NAME_KEYWORD COLON metadata_value
                    | DESCRIPTION_KEYWORD COLON metadata_value
                    | TAGS_KEYWORD COLON LBRACKET tags RBRACKET
                    | AUTHOR_KEYWORD COLON metadata_value
                    | DATE_KEYWORD COLON DATE
                    | DATE_KEYWORD COLON STRING
                    | DATA_KEYWORD COLON data_source
                    | IMPORT_KEYWORD COLON STRING
                    | REMOTE_KEYWORD COLON STRING AS ID'''
    if p[1] == '@tags':
        p[0] = Node(p[1], value=p[4])
    elif p[1] == '@data':
        # 对于数据驱动测试，将数据源信息存储在节点中
        data_info = p[3]  # 这是一个包含 file 和 format 的字典
        p[0] = Node(p[1], value=data_info, children=None)
    elif p[1] == '@import':
        # 检查是否是远程导入格式
        p[0] = Node(p[1], value=p[3])
    elif p[1] == '@remote':
        # 对于远程关键字导入，存储URL和别名
        print(f"解析远程关键字导入: URL={p[3]}, 别名={p[5]}")
        p[0] = Node('RemoteImport', value={'url': p[3], 'alias': p[5]})
    else:
        p[0] = Node(p[1], value=p[3])


def p_metadata_value(p):
    '''metadata_value : STRING
                     | ID'''
    p[0] = p[1]


def p_tags(p):
    '''tags : tag COMMA tags
            | tag'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_tag(p):
    '''tag : STRING
           | ID'''
    p[0] = Node('Tag', value=p[1])


def p_statements(p):
    '''statements : statement statements
                  | statement'''
    if len(p) == 3:
        p[0] = Node('Statements', [p[1]] + p[2].children)
    else:
        p[0] = Node('Statements', [p[1]])


def p_statement(p):
    '''statement : assignment
                | keyword_call
                | remote_keyword_call
                | loop
                | custom_keyword
                | return_statement
                | if_statement
                | break_statement
                | continue_statement'''
    p[0] = p[1]


def p_assignment(p):
    '''assignment : ID EQUALS expression
                 | ID EQUALS keyword_call
                 | ID EQUALS remote_keyword_call'''
    line_number = getattr(p.slice[1], 'lineno', None)

    if isinstance(p[3], Node) and p[3].type == 'KeywordCall':
        p[0] = Node('AssignmentKeywordCall', [p[3]],
                    p[1], line_number=line_number)
    elif isinstance(p[3], Node) and p[3].type == 'RemoteKeywordCall':
        p[0] = Node('AssignmentRemoteKeywordCall', [
                    p[3]], p[1], line_number=line_number)
    else:
        p[0] = Node('Assignment', value=p[1], children=[
                    p[3]], line_number=line_number)


def p_expression(p):
    '''expression : expr_atom
                  | comparison_expr
                  | arithmetic_expr'''
    # 如果是比较表达式或其他复合表达式，则已经是一个Node对象
    if isinstance(p[1], Node):
        p[0] = p[1]
    else:
        p[0] = Node('Expression', value=p[1])


def p_expr_atom(p):
    '''expr_atom : NUMBER
                 | STRING
                 | PLACEHOLDER
                 | ID
                 | boolean_expr
                 | list_expr
                 | dict_expr
                 | LPAREN expression RPAREN'''
    if p[1] == '(':
        # 处理括号表达式，直接返回括号内的表达式节点
        p[0] = p[2]
    elif isinstance(p[1], Node):
        p[0] = p[1]
    else:
        # 为基本表达式设置行号信息和类型信息
        expr_line = getattr(p.slice[1], 'lineno', None)

        # 根据token类型创建不同的节点类型
        token_type = p.slice[1].type
        if token_type == 'STRING':
            # 字符串字面量
            expr_node = Node('StringLiteral', value=p[1])
        elif token_type == 'NUMBER':
            # 数字字面量
            expr_node = Node('NumberLiteral', value=p[1])
        elif token_type == 'ID':
            # 变量引用
            expr_node = Node('VariableRef', value=p[1])
        elif token_type == 'PLACEHOLDER':
            # 变量占位符 ${var}
            expr_node = Node('PlaceholderRef', value=p[1])
        else:
            # 其他类型，保持原来的行为
            expr_node = Node('Expression', value=p[1])

        if expr_line is not None:
            expr_node.set_position(expr_line)
        p[0] = expr_node


def p_boolean_expr(p):
    '''boolean_expr : TRUE
                    | FALSE'''
    p[0] = Node('BooleanExpr', value=True if p[1] == 'True' else False)


def p_list_expr(p):
    '''list_expr : LBRACKET list_items RBRACKET
                 | LBRACKET RBRACKET'''
    if len(p) == 4:
        p[0] = Node('ListExpr', children=p[2])
    else:
        p[0] = Node('ListExpr', children=[])  # 空列表


def p_list_items(p):
    '''list_items : list_item
                  | list_item COMMA list_items'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_list_item(p):
    '''list_item : expression'''
    p[0] = p[1]


def p_dict_expr(p):
    '''dict_expr : LBRACE dict_items RBRACE
                 | LBRACE RBRACE'''
    if len(p) == 4:
        p[0] = Node('DictExpr', children=p[2])
    else:
        p[0] = Node('DictExpr', children=[])  # 空字典


def p_dict_items(p):
    '''dict_items : dict_item
                  | dict_item COMMA dict_items'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_dict_item(p):
    '''dict_item : expression COLON expression'''
    p[0] = Node('DictItem', children=[p[1], p[3]])


def p_loop(p):
    '''loop : FOR ID IN RANGE LPAREN expression COMMA expression RPAREN DO statements END
            | FOR ID IN expression DO statements END
            | FOR ID COMMA ID IN expression DO statements END'''  # noqa: E501
    line_number = getattr(p.slice[1], 'lineno', None)

    if len(p) == 13:
        # 传统range语法: for i in range(0, 5) do ... end
        p[0] = Node('ForRangeLoop', [p[6], p[8], p[11]], p[2], line_number=line_number)
    elif len(p) == 8:
        # 单变量遍历语法: for item in array do ... end
        p[0] = Node('ForItemLoop', [p[4], p[6]], p[2], line_number=line_number)
    else:
        # 双变量遍历语法: for key, value in dict do ... end
        p[0] = Node('ForKeyValueLoop', [p[6], p[8]], {'key_var': p[2], 'value_var': p[4]}, line_number=line_number)


def p_keyword_call(p):
    '''keyword_call : LBRACKET ID RBRACKET COMMA parameter_list
                   | LBRACKET ID RBRACKET'''
    line_number = getattr(p.slice[1], 'lineno', None)

    if len(p) == 6:
        # 对于有参数的关键字调用，尝试获取更精确的行号
        # 优先使用关键字名称的行号，其次是左括号的行号
        keyword_line = getattr(p.slice[2], 'lineno', None)
        if keyword_line is not None:
            line_number = keyword_line

        keyword_node = Node('KeywordCall', [p[5]], p[2],
                            line_number=line_number)

        # 为参数列表中的每个参数也设置行号信息（如果可用）
        if p[5] and isinstance(p[5], list):
            for param in p[5]:
                if (hasattr(param, 'set_position') and
                        not hasattr(param, 'line_number')):
                    # 如果参数没有行号，使用关键字的行号作为默认值
                    param.set_position(line_number)

        p[0] = keyword_node
    else:
        # 对于无参数的关键字调用，也优先使用关键字名称的行号
        keyword_line = getattr(p.slice[2], 'lineno', None)
        if keyword_line is not None:
            line_number = keyword_line
        p[0] = Node('KeywordCall', [[]], p[2], line_number=line_number)


def p_parameter_list(p):
    '''parameter_list : parameter_items'''
    p[0] = p[1]


def p_parameter_items(p):
    '''parameter_items : parameter_item COMMA parameter_items
                     | parameter_item'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_parameter_item(p):
    '''parameter_item : ID COLON expression'''
    # 获取参数名的行号
    param_line = getattr(p.slice[1], 'lineno', None)
    param_node = Node('ParameterItem', value=p[1], children=[p[3]])

    # 设置参数节点的行号
    if param_line is not None:
        param_node.set_position(param_line)

    p[0] = param_node


def p_teardown(p):
    '''teardown : TEARDOWN DO statements END'''
    p[0] = Node('Teardown', [p[3]])


def p_data_source(p):
    '''data_source : STRING USING ID'''
    p[0] = {'file': p[1], 'format': p[3]}


def p_custom_keyword(p):
    '''custom_keyword : FUNCTION ID LPAREN param_definitions RPAREN DO statements END'''  # noqa: E501
    p[0] = Node('CustomKeyword', [p[4], p[7]], p[2])


def p_param_definitions(p):
    '''param_definitions : param_def_list
                        | '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = []


def p_param_def_list(p):
    '''param_def_list : param_def COMMA param_def_list
                     | param_def'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_param_def(p):
    '''param_def : ID EQUALS STRING
                | ID EQUALS NUMBER
                | ID'''
    if len(p) == 4:
        p[0] = Node('ParameterDef', [Node('Expression', value=p[3])], p[1])
    else:
        p[0] = Node('ParameterDef', [], p[1])


def p_return_statement(p):
    '''return_statement : RETURN expression'''
    p[0] = Node('Return', [p[2]])


def p_break_statement(p):
    '''break_statement : BREAK'''
    p[0] = Node('Break', [])


def p_continue_statement(p):
    '''continue_statement : CONTINUE'''
    p[0] = Node('Continue', [])


def p_if_statement(p):
    '''if_statement : IF expression DO statements END
                   | IF expression DO statements elif_clauses END
                   | IF expression DO statements ELSE statements END
                   | IF expression DO statements elif_clauses ELSE statements END'''  # noqa: E501
    if len(p) == 6:
        # if condition do statements end
        p[0] = Node('IfStatement', [p[2], p[4]], None)
    elif len(p) == 7:
        # if condition do statements elif_clauses end
        p[0] = Node('IfStatement', [p[2], p[4]] + p[5], None)
    elif len(p) == 8:
        # if condition do statements else statements end
        p[0] = Node('IfStatement', [p[2], p[4], p[6]], None)
    else:
        # if condition do statements elif_clauses else statements end
        p[0] = Node('IfStatement', [p[2], p[4]] + p[5] + [p[7]], None)


def p_elif_clauses(p):
    '''elif_clauses : elif_clause
                    | elif_clause elif_clauses'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_elif_clause(p):
    '''elif_clause : ELIF expression DO statements'''
    p[0] = Node('ElifClause', [p[2], p[4]], None)


def p_comparison_expr(p):
    '''comparison_expr : expr_atom GT expr_atom
                      | expr_atom LT expr_atom
                      | expr_atom GE expr_atom
                      | expr_atom LE expr_atom
                      | expr_atom EQ expr_atom
                      | expr_atom NE expr_atom'''

    # 根据规则索引判断使用的是哪个操作符
    if p.slice[2].type == 'GT':
        operator = '>'
    elif p.slice[2].type == 'LT':
        operator = '<'
    elif p.slice[2].type == 'GE':
        operator = '>='
    elif p.slice[2].type == 'LE':
        operator = '<='
    elif p.slice[2].type == 'EQ':
        operator = '=='
    elif p.slice[2].type == 'NE':
        operator = '!='
    else:
        print(f"警告: 无法识别的操作符类型 {p.slice[2].type}")
        operator = None

    p[0] = Node('ComparisonExpr', [p[1], p[3]], operator)


def p_arithmetic_expr(p):
    '''arithmetic_expr : expression PLUS expression
                       | expression MINUS expression
                       | expression TIMES expression
                       | expression DIVIDE expression
                       | expression MODULO expression'''

    # 根据规则索引判断使用的是哪个操作符
    if p.slice[2].type == 'PLUS':
        operator = '+'
    elif p.slice[2].type == 'MINUS':
        operator = '-'
    elif p.slice[2].type == 'TIMES':
        operator = '*'
    elif p.slice[2].type == 'DIVIDE':
        operator = '/'
    elif p.slice[2].type == 'MODULO':
        operator = '%'
    else:
        print(f"警告: 无法识别的操作符类型 {p.slice[2].type}")
        operator = None

    p[0] = Node('ArithmeticExpr', [p[1], p[3]], operator)


# 全局变量用于存储解析错误
_parse_errors = []


def p_error(p):
    global _parse_errors
    if p:
        error_msg = (f"语法错误: 在第 {p.lineno} 行, 位置 {p.lexpos}, "
                     f"Token {p.type}, 值: {p.value}")
        _parse_errors.append({
            'message': error_msg,
            'line': p.lineno,
            'position': p.lexpos,
            'token_type': p.type,
            'token_value': p.value
        })
        # 不再直接打印，而是存储错误信息
    else:
        error_msg = "语法错误: 在文件末尾"
        _parse_errors.append({
            'message': error_msg,
            'line': None,
            'position': None,
            'token_type': None,
            'token_value': None
        })


def get_parser(debug=False):
    return yacc.yacc(debug=debug)


def parse_with_error_handling(content, lexer=None):
    """带错误处理的解析函数

    Args:
        content: DSL内容
        lexer: 词法分析器实例

    Returns:
        tuple: (AST节点, 错误列表)
    """
    global _parse_errors
    _parse_errors = []  # 清空之前的错误

    if lexer is None:
        from pytest_dsl.core.lexer import get_lexer
        lexer = get_lexer()

    parser = get_parser()
    ast = parser.parse(content, lexer=lexer)

    # 返回AST和错误列表
    return ast, _parse_errors.copy()

# 定义远程关键字调用的语法规则


def p_remote_keyword_call(p):
    '''remote_keyword_call : ID PIPE LBRACKET ID RBRACKET COMMA parameter_list
                          | ID PIPE LBRACKET ID RBRACKET'''
    if len(p) == 8:
        p[0] = Node('RemoteKeywordCall', [p[7]], {
                    'alias': p[1], 'keyword': p[4]})
    else:
        p[0] = Node('RemoteKeywordCall', [[]], {
                    'alias': p[1], 'keyword': p[4]})
