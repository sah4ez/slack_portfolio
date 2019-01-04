import platypus.frontend.ast as ast
import cfg

def get_cfg(ast_func):
    """
    Traverses the AST and returns the corresponding CFG

    :param ast_func: The AST representation of function
    :type ast_func: ast.Function

    :returns: The CFG representation of the function
    :rtype: cfg.Function
    """
    cfg_func = cfg.Function()
    for ast_var in ast_func.input_variable_list:
        cfg_var = cfg_func.get_variable(ast_var.name)
        cfg_func.add_input_variable(cfg_var)
    for ast_var in ast_func.output_variable_list:
        cfg_var = cfg_func.get_variable(ast_var.name)
        cfg_func.add_output_variable(cfg_var)
    bb_start  = cfg.BasicBlock()
    cfg_func.add_basic_block(bb_start)
    for stmt in ast_func.body:
        bb_temp = bb_start
        bb_temp = process_cfg(stmt, bb_temp, cfg_func)
    cfg_func.clean_up()
    cfg_func.add_summary(ast_func.summary)
    return cfg_func

def process_cfg(stmt, basic_block, func):
    if isinstance(stmt, ast.IfElseNode):
        return process_if_else_node_cfg(stmt, basic_block, func)
    if isinstance(stmt, ast.IfNode):
        return process_if_node_cfg(stmt, basic_block, func)
    if isinstance(stmt, ast.WhileNode):
        return process_while_node_cfg(stmt, basic_block, func)
    if isinstance(stmt, ast.EqNode):
        return process_eq_node_cfg(stmt, basic_block, func)



def process_eq_node_cfg(eq_node, basic_block, func):
    assert(isinstance(basic_block, cfg.BasicBlock))
    result = func.get_variable(eq_node.variable.name)
    if isinstance(eq_node.expr, ast.SingleExprNode):
        if isinstance(eq_node.expr, ast.NumberNode):
            operand = cfg.Constant(eq_node.expr.value)
        else:
            operand = func.get_variable(eq_node.expr.name)
        instr = cfg.EqInstruction(result, operand)
        basic_block.add_instruction(instr)
    else:
        if isinstance(eq_node.expr.operand_1, ast.NumberNode):
            operand_1 = cfg.Constant(eq_node.expr.operand_1.value)
        else:
            operand_1 = \
                    func.get_variable(eq_node.expr.operand_1.name)
        if isinstance(eq_node.expr.operand_2, ast.NumberNode):
            operand_2 = cfg.Constant(eq_node.expr.operand_2.value)
        else:
            operand_2 = \
                    func.get_variable(eq_node.expr.operand_2.name)
        if (isinstance(eq_node.expr, ast.CmpExprNode)):
            opr = cfg.Operation(eq_node.expr.operator)
            instr = cfg.CmpInstruction(result, operand_1, operand_2, opr)
        else:
            opr = cfg.Operation(eq_node.expr.operator)
            instr = cfg.ArithInstruction(result, operand_1, operand_2, opr)
        basic_block.add_instruction(instr)
    return basic_block


def process_while_node_cfg(while_node, basic_block, func):
    assert(isinstance(basic_block, cfg.BasicBlock))
    if isinstance(while_node.condition, ast.VariableNode):
        condn = func.get_variable(while_node.condition.name)
        condn_instr = None
    elif isinstance(while_node.condition, ast.CmpExprNode):
        condn = func.get_variable('x')
        operand_1 = while_node.condition.operand_1
        operand_2 = while_node.condition.operand_2
        if isinstance(operand_1, ast.VariableNode):
            rhs_1 = func.get_variable(while_node.condition.operand_1.name)
        else:
            rhs_1 = cfg.Constant(operand_1.value)
        if isinstance(operand_2, ast.VariableNode):
            rhs_2 = func.get_variable(while_node.condition.operand_2.name)
        else:
            rhs_2 = cfg.Constant(operand_2.value)
        opr = cfg.Operation(while_node.condition.operator)
        condn_instr = cfg.CmpInstruction(condn, rhs_1, rhs_2, opr)
    basic_block.set_condition(condn, condn_instr)
    bb_new = cfg.BasicBlock()
    func.add_basic_block(bb_new)
    basic_block.child_false = bb_new
    bb_body = cfg.BasicBlock()
    func.add_basic_block(bb_body)
    basic_block.child_true = bb_body
    bb_temp = bb_body
    for stmt in while_node.body:
        bb_temp = process_cfg(stmt, bb_temp, func)
    bb_temp.child_true = bb_body
    bb_temp.child_false = bb_new
    bb_temp.set_condition(condn, condn_instr)
    return bb_new

def process_if_else_node_cfg(if_else_node, basic_block, func):
    assert(isinstance(basic_block, cfg.BasicBlock))
    assert(isinstance(func, cfg.Function))
    if isinstance(if_else_node.condition, ast.VariableNode):
        condn = func.get_variable(if_else_node.condition.name)
        condn_instr = None
    elif isinstance(if_else_node.condition, ast.CmpExprNode):
        condn = func.get_variable('x')
        operand_1 = if_else_node.condition.operand_1
        operand_2 = if_else_node.condition.operand_2
        if isinstance(operand_1, ast.VariableNode):
            rhs_1 = func.get_variable(if_else_node.condition.operand_1.name)
        else:
            rhs_1 = cfg.Constant(operand_1.value)
        if isinstance(operand_2, ast.VariableNode):
            rhs_2 = func.get_variable(if_else_node.condition.operand_2.name)
        else:
            rhs_2 = cfg.Constant(operand_2.value)
        opr = cfg.Operation(if_else_node.condition.operator)
        condn_instr = cfg.CmpInstruction(condn, rhs_1, rhs_2, opr)
    basic_block.set_condition(condn, condn_instr)
    bb_new = cfg.BasicBlock()
    func.add_basic_block(bb_new)
    bb_body_yes = cfg.BasicBlock()
    func.add_basic_block(bb_body_yes)
    bb_body_no = cfg.BasicBlock()
    func.add_basic_block(bb_body_no)
    basic_block.child_true = bb_body_yes
    basic_block.child_false = bb_body_no
    bb_temp_yes = bb_body_yes
    bb_temp_no = bb_body_no
    for stmt in if_else_node.body_yes:
        bb_temp_yes = process_cfg(stmt, bb_temp_yes, func)
    for stmt in if_else_node.body_no:
        bb_temp_no = process_cfg(stmt, bb_temp_no, func)
    bb_temp_yes.child_false = bb_new
    bb_temp_yes.child_true = bb_new
    bb_temp_no.child_false = bb_new
    bb_temp_no.child_true = bb_new
    return bb_new


def process_if_node_cfg(if_node, bb_old, func):
    assert(isinstance(bb_old, cfg.BasicBlock))
    if isinstance(if_node.condition, ast.VariableNode):
        condn = func.get_variable(if_node.condition.name)
        condn_instr = None
    elif isinstance(if_node.condition, ast.CmpExprNode):
        condn = func.get_variable('x')
        operand_1 = if_node.condition.operand_1
        operand_2 = if_node.condition.operand_2
        if isinstance(operand_1, ast.VariableNode):
            rhs_1 = func.get_variable(if_node.condition.operand_1.name)
        else:
            rhs_1 = cfg.Constant(operand_1.value)
        if isinstance(operand_2, ast.VariableNode):
            rhs_2 = func.get_variable(if_node.condition.operand_2.name)
        else:
            rhs_2 = cfg.Constant(operand_2.value)
        opr = cfg.Operation(if_node.condition.operator)
        condn_instr = cfg.CmpInstruction(condn, rhs_1, rhs_2, opr)
    bb_old.set_condition(condn, condn_instr)
    bb_new = cfg.BasicBlock()
    func.add_basic_block(bb_new)
    bb_old.child_false = bb_new
    bb_body = cfg.BasicBlock()
    func.add_basic_block(bb_body)
    bb_old.child_true = bb_body
    bb_temp = bb_body
    for stmt in if_node.body:
        bb_temp = process_cfg(stmt, bb_temp, func)
    bb_temp.child_true = bb_new
    bb_temp.child_false = bb_new
    return bb_new
