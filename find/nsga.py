from platypus import NSGAII, DTLZ2, Problem, Real


# define the problem definition
class Belegundu(Problem):
    def __init__(self):
        super(Belegundu, self).__init__(2, 2, 2)
        self.types[:] = [Real(0, 5), Real(0, 3)]
        self.constraints[:] = "<=0"

    def evaluate(self, solution):
        x = solution.variables[0]
        y = solution.variables[1]
        solution.objectives[:] = [-2 * x + y, 2 * x + y]
        solution.constraints[:] = [-x + y - 1, x + y - 7]


problem = Belegundu()

problem.directions[:] = Problem.MINIMIZE
algorithm = NSGAII(problem)

algorithm.run(10000)
# plot the results using matplotlib
import matplotlib.pyplot as plt

plt.scatter([s.objectives[0] for s in algorithm.result],
            [s.objectives[1] for s in algorithm.result])
plt.xlim([-100, 100])
plt.ylim([-100, 100])
plt.xlabel("$f_1(x)$")
plt.ylabel("$f_2(x)$")
plt.show()
