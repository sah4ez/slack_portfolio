"""
Defines the entities in a Control Flow Graph
"""

class Numeric:
    """Base class for Variables & Constants"""
    pass


class Variable (Numeric):

    def __init__(self, name):
        """
        :param str name: The name of a variable is as same as in the source code
        """
        assert(isinstance(name, str))
        self.name = name


class Constant (Numeric):

    def __init__(self, value):
        """
        :param int value: the numeric value of a constant
        """
        assert(isinstance(value, int))
        self.value = value
        self.name = str(value)


class Operation:
    """
    Represents a binary operation
    """
    def __init__(self, name):
        assert(name == '<' or \
                name == '>' or \
                name == '<=' or \
                name == '>=' or \
                name == '==' or \
                name == '!=' or\
                name == '+' or \
                name == '*' or \
                name == '/' or \
                name == '-' or \
                name == '%')
        self.name = name

    def __eq__(self, other):
        return (self.name == other.name)

class Instruction:
    """Base class for all Instructions"""
    pass


class CmpInstruction (Instruction):
    """
    Represents instructions of the format: 'a = b op c' where\
            op can be <, >, <=, >=, ==, !=
    'a' has to be a Variable, where as 'b' & 'c' can be a variable or a constant
    """

    def __init__(self, lhs, rhs_1, rhs_2, op):
        """
        :type lhs: Variable
        :type rhs_1: Numeric
        :type rhs_2: Numeric
        :type op: Operation
        """
        assert(op == Operation('<') or \
                op == Operation('>') or \
                op == Operation('<=') or \
                op == Operation('>=') or \
                op == Operation('==') or \
                op == Operation('!='))
        assert(isinstance(lhs, Variable) and \
                isinstance(rhs_1, Numeric) and \
                isinstance(rhs_2, Numeric))
        self.lhs = lhs
        self.rhs_1 = rhs_1
        self.rhs_2 = rhs_2
        self.op = op


class ArithInstruction(Instruction):
    """
    Represents instructions of the format: 'a = b op c' where\
            op can be +, *, /, -, %
    'a' has to be a Variable, where as 'b' & 'c' can be a variable or a constant
    """

    def __init__(self, lhs, rhs_1, rhs_2, op):
        """
        :type lhs: Variable
        :type rhs_1: Numeric
        :type rhs_2: Numeric
        :type op: Operation
        """
        assert(op == Operation('+') or \
                op == Operation('*') or \
                op == Operation('/') or \
                op == Operation('-') or \
                op == Operation('%'))
        assert(isinstance(lhs, Variable) and \
                isinstance(rhs_1, Numeric) and \
                isinstance(rhs_2, Numeric))
        self.lhs = lhs
        self.rhs_1 = rhs_1
        self.rhs_2 = rhs_2
        self.op = op



class EqInstruction(Instruction):
    """
    Represents instuctions of the format: 'a = b'
    """

    def __init__(self, lhs, rhs):
        """
        :type lhs: Variable
        :type rhs: Numeric
        """
        assert(isinstance(lhs, Variable) and isinstance(rhs, Numeric))
        self.lhs = lhs
        self.rhs = rhs
        return



class BasicBlock:

    """
    Represents a basic block in the Control Flow Graph

    :param used_variables: A list of all variables which come in the RHS of any\
            instruction in the basic block. Example, if a instruction 'a = 3 + b'\
            is a part of the basic block, then 'b'  would be added in this list
    :type used_variables: list(Variable)

    :param defined_variables: A list of all variables which come in the LHS of any\
            instruction in the basic block. Example, if a instruction 'a = 3 _ b'\
            is a part of the basic blocl, then 'a' would be added to this list
    :type defined_variables: list(Variable)

    :param child_true: The exit basic block in case the condition evaluates to True
    :type child_true: BasicBlock

    :param child_false: The exit basic block in case the condition evaluates to False
    :type child_false: BasicBlock

    :param instruction_list: The list of instructions which form this basic block
    :type instruction_list: list(Instruction)

    :param int identity: Unique identity which identifies this basic block
    """

    def __init__(self):
        self.identity = 0
        self.condition = None
        self.condition_instr = None
        self.child_true = None
        self.child_false = None
        self.used_variables = []
        self.defined_variables = []
        self.instruction_list = []

    def add_instruction (self, instr):
        """
        Adds the argument instruction in the list of instructions of this basic block.

        Also updates the variable lists (used_variables, defined_variables)
        """
        assert(isinstance(instr, Instruction))
        self.instruction_list.append(instr)
        if instr.lhs not in self.defined_variables:
            if isinstance(instr.lhs, Variable):
                self.defined_variables.append(instr.lhs)
        if isinstance(instr, EqInstruction):
            if isinstance(instr.rhs, Variable):
                if instr.rhs not in self.used_variables:
                    self.used_variables.append(instr.rhs)
        else:
            if isinstance(instr.rhs_1, Variable):
                if instr.rhs_1 not in self.used_variables:
                    self.used_variables.append(instr.rhs_1)
            if isinstance(instr.rhs_2, Variable):
                if instr.rhs_2 not in self.used_variables:
                    self.used_variables.append(instr.rhs_2)


    def set_condition(self, condition, condition_instr=None):
        """
        Defines the condition which decides how the basic block exits

        :param condition:
        :type condition:

        :param condition_instr: If the 'condition' argument is a Variable, then\
                condition_instr is None, else, condition_instr should be\
                of type CmpInstruction
        :type condition_instr: CmpInstruction
        """
        assert(isinstance(condition, Numeric))
        if condition_instr is not None:
            assert(isinstance(condition_instr, CmpInstruction))
        self.condition = condition
        self.condition_instr = condition_instr
        if condition_instr is not None:
            if condition_instr.lhs not in self.defined_variables:
                if isinstance(condition_instr.lhs, Variable):
                    self.defined_variables.append(condition_instr.lhs)
            if isinstance(condition_instr.rhs_1, Variable):
                if condition_instr.rhs_1 not in self.used_variables:
                    self.used_variables.append(condition_instr.rhs_1)
            if isinstance(condition_instr.rhs_2, Variable):
                if condition_instr.rhs_2 not in self.used_variables:
                    self.used_variables.append(condition_instr.rhs_2)

    def clean_up(self):
        if self.child_true == self.child_false:
            self.child = self.child_true
            if(self.child == None):
                self.number_of_children = 0
            else:
                self.number_of_children = 1
        else:
            self.number_of_children = 2


class Function:

    """A function in the CFG is a collection of interconnected\
            basic blocks
    :param basic_block_list: A list of basic blocks contained in the function
    :type basic_block_list: list(BasicBlock)

    :param variable_list: A list of variables which are defined or used in the function
    :type variable_list: list(Variable)

    :param input_variable_list: A list of variables whose initial which are passed as argument\
            to the function in the source code. The initial values of these variables is known
    :type input_variable_list: list(Variable)

    :param output_variable_list: A list of variables which are returned by the function
    :type output_variable_list: list(Variable)
    """
    def __init__(self):
        self.basic_block_list = []
        self.variable_list = []
        self.input_variable_list = []
        self.output_variable_list = []
        self.summary = ""

    def add_basic_block(self, basic_block):
        """Adds the given basic block in the function"""
        assert(isinstance(basic_block, BasicBlock))
        self.basic_block_list.append(basic_block)

    def clean_up(self):
        identity = 0
        for basic_block in self.basic_block_list:
            basic_block.clean_up()
            basic_block.identity = identity
            identity += 1

    def get_variable(self, var_name):
        """
        If a variable with the name var_name exists in this function's variable list, \
                then that variable object is returned; else a new variable is created\
                with the given name and added to the variable list of this function\
                and returned back

        :returns: A variable which has the its name as var_name
        :rype: Variable
        """
        assert(isinstance(var_name, str))
        if isinstance(var_name, str):
            for var in self.variable_list:
                if var.name == var_name:
                    return var
            new_var = Variable(var_name)
            self.variable_list.append(new_var)
            return new_var

    def add_input_variable(self, var):
        """Adds the argument variable as one of the input variable"""
        assert(isinstance(var, Variable))
        self.input_variable_list.append(var)

    def add_output_variable(self, var):
        """Adds the argument variable as one of the output variable"""
        assert(isinstance(var, Variable))
        self.output_variable_list.append(var)

    def add_summary(self, summary_string):
        """Adds a summary description to this function"""
        assert(isinstance(summary_string, str))
        self.summary = summary_string
        return
