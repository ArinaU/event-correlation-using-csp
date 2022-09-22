


from constraint import *
import pandas as pd
import numpy as np
import itertools
import math

class MyConstraint(Constraint):

    def __init__(self, data, constraints):
        self._data = data
        self._constraints = constraints

    def __call__(self, events, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        constraints = self._constraints
        unary_constraints = constraints['unary']
        binary_constraints = constraints['binary']
        data = self._data

        curr_event = max(assignments.keys())
        suggested_case = assignments[curr_event]

        # get all events ids with this case
        last_events_ids = [key for key, value in assignments.items() if value == suggested_case]
        # get events themselves
        last_events = [event for event in data if event['EventID'] in last_events_ids]

        if binary_constraints and len(last_events) > 1:
            for constraint in binary_constraints:
                for x, y in itertools.permutations(last_events, 2):
                    if not eval(constraint):
                        return False
        if unary_constraints:
            for constraint in unary_constraints:
                for x in last_events:
                    if not eval(constraint):
                        break #???
        return True



class MyRecursiveBacktrackingSolver(Solver):

    def __init__(self, forwardcheck=True):
        """
        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck


    def recursiveBacktracking(
        self, solutions, domains, vconstraints, assignments, single
    ):

        # Mix the Degree and Minimum Remaing Values (MRV) heuristics
        lst = [
            (-len(vconstraints[variable]), len(domains[variable]), variable)
            for variable in domains
        ]
        lst.sort()
        for item in lst: #(-1, 4, 1)
            if item[-1] not in assignments: # {}
                # Found an unassigned variable. Let's go.
                break
        else:
            # No unassigned variables. We've got a solution.
            solutions.append(assignments.copy())
            return solutions

        variable = item[-1] # 1
        assignments[variable] = None # add to
        # queue

        # Case1
        for value in domains[variable]:
            assignments[variable] = value # {1: 'Case1'}

            for constraint, variables in vconstraints[variable]:
                if not constraint(variables, domains, assignments):
                    # Value is not good.

                    break
            else:
                # Value is good. Recurse and get next variable.
                self.recursiveBacktracking(
                    solutions, domains, vconstraints, assignments, single
                )
                if solutions and single:
                    return solutions

        del assignments[variable]
        return solutions


    def getSolution(self, domains, constraints, vconstraints):
        solutions = self.recursiveBacktracking([], domains, vconstraints, {}, True)
        return solutions and solutions[0] or None

    def getSolutions(self, domains, constraints, vconstraints):
        return self.recursiveBacktracking([], domains, vconstraints, {}, False)



def assign_cases():
    data = pd.read_csv('data.csv', sep=';')
    n_of_events = len(data)

    # add empty column with cases
    data = data.assign(CaseID=None)
    data = data.to_dict(orient="records")

    solver = MyRecursiveBacktrackingSolver()
    problem = Problem(solver)

    # constraints = {'unary': ["x['Timestamp'] < '2022-01-01 11:20:59'"],
    #                'binary': ["x['UserID'] == y['UserID']",
    #                           "x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'B' and y['Activity'] == 'A' else True" ]}

    constraints = {'unary': [],
                   'binary': ["x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'A' and y['Activity'] == 'B' else True" ]}

    case = 1

    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(1, n_of_events+1)])

    problem.addConstraint(MyConstraint(data, constraints))
    solutions = problem.getSolution()

    return solutions




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    result = assign_cases()
    print(result)


