import sys
import os
from optparse import OptionParser

from _version import __version__
from platypus.frontend import get_ast
from platypus.cfg import get_cfg
from platypus.simulator import get_ir

class Shell:

    def __init__(self, source_filename):
        try:
            source_file = open(source_filename, 'r') 
        except IOError:
            print 'error in opening file ', source_filename
            quit()
        source = ""
        for line in source_file:
            source += line

        func_ast = get_ast(source)
        func_cfg = get_cfg(func_ast)
        try:
            os.remove("parser.out")
            os.remove("parsetab.py")
            os.remove("parsetab.pyc")
        except:
            pass
        self.func_sim = get_ir(func_cfg)


    def run(self):
        self.running = True
        while self.running is True:
            cmd = raw_input('platypus $ ')
            self.handle_cmd(cmd)

    def handle_cmd(self, cmd):
        if (cmd == 'exit'):
            self.running = False
        elif (cmd == ''):
            self.running = True
        elif (cmd == 'summary'):
            print ''
            print self.func_sim.summary
            print ''
        elif (cmd == 'help'):
            print ''
            print 'summary  : show summary of function as written in platypus program'
            print 'exit     : exit simulator'
            print 'asm      : display intermediate code that is being simulated'
            print 'clear    : clear screen'
            print ''
        elif (cmd == 'clear'):
            os.system('clear')
        elif (cmd == 'asm'):
            print ''
            self.func_sim.show()
            print ''
        else:
            input_values_string = cmd.split(' ')
            input_values = []
            valid_input = True
            for value_string in input_values_string:
                try:
                    input_values.append(int(value_string))
                except:
                    valid_input = False
            if valid_input:
                if len(input_values) == len(self.func_sim.input_variables):
                    print self.func_sim.execute(input_values)
                else:
                    print 'expected ', len(self.func_sim.input_variables), ' arguments'
            else:
                print 'please enter only integers as arguments'


def run():
    parser = OptionParser("usage: %platypus [options] filename",
                version=__version__)
    parser.add_option("-i", "--input_file", action="store", dest="source_filename",
            default="source.platypus", help="enter path of the source code ")
    (args, options) = parser.parse_args()
    if args.source_filename == "source.platypus":
        print 'please mention source path'
    shell = Shell(args.source_filename)
    shell.run()



if __name__ == "__main__":
    run()
