"""
This module defines all nodes in the AST (Abstract Syntax Tree).
The AST is a very close representation of the source program.
The root of the tree is a Function
"""


class ExprNode(object):
    """Base class for SingleExprNode & BinExprNode"""
    pass



class StmtNode(object):
    """Base class for WhileNode, IfElseNode, IfNode"""
    pass


class SingleExprNode(ExprNode):
    """Base class for VariableNode & NumberNode"""
    pass



class BinExprNode(ExprNode):
    """Represents binary expressions such as 'a + 2'"""

    def __init__(self, operator, operand_1, operand_2):
        assert(isinstance(operator, str))
        assert(isinstance(operand_1, SingleExprNode))
        assert(isinstance(operand_2, SingleExprNode))
        self.operator = operator
        self.operand_1 = operand_1
        self.operand_2 = operand_2

    def __str__(self):
        output = "{operand_1} {operator} {operand_2}".\
                format(operand_1=str(self.operand_1),
                       operator=self.operator,
                       operand_2=str(self.operand_2))
        return output


class VariableNode(SingleExprNode):

    def __init__(self, name):
        assert(isinstance(name, str))
        self.name = name

    def __str__(self):
        return self.name


class NumberNode(SingleExprNode):

    def __init__(self, value):
        assert(isinstance(value, int))
        self.value = value

    def __str__(self):
        return str(self.value)

class ArithExprNode(BinExprNode):

    def __init__(self, operator, operand_1, operand_2):
        super(ArithExprNode, self).__init__(operator, operand_1, operand_2)


class CmpExprNode(BinExprNode):

    def __init__(self, operator, operand_1, operand_2):
        super(CmpExprNode, self).__init__(operator, operand_1, operand_2)


class EqNode(StmtNode):

    def __init__(self, variable, expr):
        assert(isinstance(variable, VariableNode))
        assert(isinstance(expr, ExprNode))
        self.variable = variable
        self.expr = expr
        return

    def __str__(self, indent_level=0):
        output = "{variable} = {expr}"\
                .format(variable=str(self.variable),
                        expr=str(self.expr))
        return output

class WhileNode(StmtNode):

    def __init__(self, condition, body):
        assert(isinstance(condition, SingleExprNode) or \
                isinstance(condition, CmpExprNode))
        self.condition = condition
        self.body = body
        for stmt in body:
            assert(isinstance(stmt, StmtNode))


    def __str__(self, indent_level=0):
        output = "while ({condition}){next_indent}{body}"\
                .format(condition=str(self.condition),
                        body=indent_helper(indent_level+1).\
                                join([stmt.__str__(indent_level+1) 
                                      for stmt in self.body]),
                        next_indent=indent_helper(indent_level+1))
        return output

class IfElseNode(StmtNode):

    def __init__(self, condition, body_yes, body_no):
        assert(isinstance(condition, SingleExprNode) or \
                isinstance(condition, CmpExprNode))
        for stmt in body_yes:
            assert(isinstance(stmt, StmtNode))
        for stmt in body_no:
            assert(isinstance(stmt, StmtNode))
        self.condition = condition
        self.body_yes = body_yes
        self.body_no = body_no

    def __str__(self, indent_level=0):
        output = "if ({condition}){next_indent}{body_yes}"\
                "{cur_indent}else{next_indent}{body_no}"\
                .format(condition=str(self.condition),
                        body_yes=indent_helper(indent_level+1).\
                                join([stmt.__str__(indent_level+1) 
                                      for stmt in self.body_yes]),
                        body_no=indent_helper(indent_level+1).\
                                join([stmt.__str__(indent_level+1) 
                                      for stmt in self.body_no]),
                        next_indent=indent_helper(indent_level+1),
                        cur_indent=indent_helper(indent_level))

        return output


class IfNode(StmtNode):

    def __init__(self, condition, body):
        assert(isinstance(condition, SingleExprNode) or \
                isinstance(condition, CmpExprNode))
        self.condition = condition
        self.body = body
        for stmt in body:
            assert(isinstance(stmt, StmtNode))

    def __str__(self, indent_level=0):
        output = "if ({condition}){next_indent}{body}"\
                .format(condition=str(self.condition),
                        body=indent_helper(indent_level+1).\
                                join([stmt.__str__(indent_level+1) 
                                      for stmt in self.body]),
                        next_indent=indent_helper(indent_level+1))
        return output


class Function(object):

    def __init__(self, input_variable_list, 
                 output_variable_list, body, summary):
        for var in input_variable_list:
            assert(isinstance(var, VariableNode))
        for var in output_variable_list:
            assert(isinstance(var, VariableNode))
        for stmt in body:
            assert(isinstance(stmt, StmtNode))
        self.body = body
        self.input_variable_list = input_variable_list
        self.output_variable_list = output_variable_list
        self.summary = summary

    def __str__(self):
        output = \
                "\n\nfunction ( {input_var_list} )\n\t{summary}"\
                "\n\t{body}\n\treturn {output_var_list}"\
                .format(input_var_list=", ".join([str(var) for var 
                                                  in self.input_variable_list]),
                        summary=self.summary,
                        body=indent_helper(1).\
                                join([stmt.__str__(1) for stmt in self.body]),
                        output_var_list=", ".\
                                join([str(var) for var in \
                                      self.output_variable_list]))
        return output

def indent_helper(indent_level, new_line=True):
    indent_string = "\n"
    indent_string += "\t".join(['' for i in range(indent_level+1)])
    return indent_string

