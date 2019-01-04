import ir
import platypus.cfg.cfg as cfg


def get_ir(cfg_func):
    """
    Converts the given CFG function into IR entities
    """
    ir_func = ir.Function()
    ir_var_list = []
    cfg_var_list = []
    ir_bb_label_list = []
    for cfg_var in cfg_func.variable_list:
        ir_var = ir.Variable(cfg_var.name)
        ir_var_list.append(ir_var)
        cfg_var_list.append(cfg_var)
    label = 0
    for cfg_bb in cfg_func.basic_block_list:
        ir_bb_label_list.append(label)
        for cfg_instr in cfg_bb.instruction_list:
            if isinstance(cfg_instr, cfg.ArithInstruction):
                ir_instr = ir.ArithInstruction(ir_func)
                ir_lhs = get_ir_numeric(cfg_instr.lhs, cfg_var_list, ir_var_list)
                ir_rhs_1 = get_ir_numeric(cfg_instr.rhs_1, cfg_var_list, ir_var_list)
                ir_rhs_2 = get_ir_numeric(cfg_instr.rhs_2, cfg_var_list, ir_var_list)
                ir_op = ir.Operation(cfg_instr.op.name)
                ir_instr.update(ir_lhs, ir_rhs_1, ir_rhs_2, ir_op)
            elif isinstance(cfg_instr, cfg.CmpInstruction):
                ir_instr = ir.CmpInstruction(ir_func)
                ir_lhs = get_ir_numeric(cfg_instr.lhs, cfg_var_list, ir_var_list)
                ir_rhs_1 = get_ir_numeric(cfg_instr.rhs_1, cfg_var_list, ir_var_list)
                ir_rhs_2 = get_ir_numeric(cfg_instr.rhs_2, cfg_var_list, ir_var_list)
                ir_op = ir.Operation(cfg_instr.op.name)
                ir_instr.update(ir_lhs, ir_rhs_1, ir_rhs_2, ir_op)
            elif isinstance(cfg_instr, cfg.EqInstruction):
                ir_instr = ir.EqInstruction(ir_func)
                ir_lhs = get_ir_numeric(cfg_instr.lhs, cfg_var_list, ir_var_list)
                ir_rhs = get_ir_numeric(cfg_instr.rhs, cfg_var_list, ir_var_list)
                ir_instr.update(ir_lhs, ir_rhs)
            ir_func.add_instruction_by_label(label, ir_instr)
            label += 1
        #at end of BB, add branch statements
        if cfg_bb.number_of_children is 1:
            ir_instr = ir.UncondnJumpInstruction(ir_func)
            ir_func.add_instruction_by_label(label, ir_instr)
        elif cfg_bb.number_of_children is 2:
            if isinstance(cfg_bb.condition_instr, cfg.CmpInstruction):
                ir_instr = ir.CmpInstruction(ir_func)
                ir_lhs = get_ir_numeric(cfg_bb.condition_instr.lhs, cfg_var_list, ir_var_list)
                ir_rhs_1 = get_ir_numeric(cfg_bb.condition_instr.rhs_1, cfg_var_list, ir_var_list)
                ir_rhs_2 = get_ir_numeric(cfg_bb.condition_instr.rhs_2, cfg_var_list, ir_var_list)
                ir_op = ir.Operation(cfg_bb.condition_instr.op.name)
                ir_instr.update(ir_lhs, ir_rhs_1, ir_rhs_2, ir_op)
                ir_func.add_instruction_by_label(label, ir_instr)
                label += 1
            ir_instr = ir.CondnJumpInstruction(ir_func)
            ir_condn_var = get_ir_numeric(cfg_bb.condition, cfg_var_list, ir_var_list)
            ir_instr.update(ir_condn_var, 0, 0)
            ir_func.add_instruction_by_label(label, ir_instr)
        else:
            ir_instr = ir.ReturnInstruction(ir_func)
            ir_func.add_instruction_by_label(label, ir_instr)
        label += 1

    k = 0
    for cfg_bb in cfg_func.basic_block_list:
        if cfg_bb.number_of_children is 1:
            this_label = ir_bb_label_list[k] + len(cfg_bb.instruction_list)
            assert(isinstance(ir_func.instr_list[this_label], ir.UncondnJumpInstruction))
            next_label = ir_bb_label_list[cfg_bb.child.identity]
            ir_func.instr_list[this_label].next_instr_label = next_label
        elif cfg_bb.number_of_children is 2:
            this_label = ir_bb_label_list[k] + len(cfg_bb.instruction_list) 
            if isinstance(cfg_bb.condition_instr, cfg.CmpInstruction):
                this_label += 1
            assert(isinstance(ir_func.instr_list[this_label], ir.CondnJumpInstruction))
            next_true_label = ir_bb_label_list[cfg_bb.child_true.identity]
            next_false_label = ir_bb_label_list[cfg_bb.child_false.identity]
            ir_func.instr_list[this_label].instr_true_label = next_true_label
            ir_func.instr_list[this_label].instr_false_label = next_false_label
        k += 1
    ir_input_variables = []
    for cfg_var in cfg_func.input_variable_list:
        ir_var = get_ir_numeric(cfg_var, cfg_var_list, ir_var_list)
        ir_input_variables.append(ir_var)

    ir_output_variables = []
    for cfg_var in cfg_func.output_variable_list:
        ir_var = get_ir_numeric(cfg_var, cfg_var_list, ir_var_list)
        ir_output_variables.append(ir_var)
    ir_func.set_input_variables(ir_input_variables)
    ir_func.set_output_variables(ir_output_variables)
    ir_func.add_summary(cfg_func.summary)
    return ir_func

def get_ir_numeric(cfg_num, cfg_var_list, ir_var_list):
    assert(isinstance(cfg_num, cfg.Numeric))
    if isinstance(cfg_num, cfg.Variable):
        k = 0
        for cv in cfg_var_list:
            if cv == cfg_num:
                return ir_var_list[k]
            k = k+1
        return None
    else:
        return ir.Constant(cfg_num.value)
