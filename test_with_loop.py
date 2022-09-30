


from constraint import *
import pandas as pd
import numpy as np
import itertools
import math

class MyConstraint(Constraint):

    def __init__(self, data, constraints):
        self._data = data
        self._constraints = constraints

    def exist_in_exceptions(self, x, y, exceptions):
        for exception in exceptions: # [5, 3]
            if x in exception and y in exception:
                return True
        return False


    def __call__(self, events, domains, assignments, exceptions):
        constraints = self._constraints
        data = self._data

        curr_event = max(assignments.keys())
        suggested_case = assignments[curr_event]

        # get all events ids with this case
        last_events_ids = [key for key, value in assignments.items() if value == suggested_case]
        # get events themselves
        last_events = [event for event in data if event['EventID'] in last_events_ids]

        if constraints and len(last_events) > 1:
            for cname, constraint in constraints.items():
                for x, y in itertools.permutations(last_events, 2):
                    if not eval(constraint):
                        if cname == 'C6':
                            if not self.exist_in_exceptions(x['EventID'], y['EventID'], exceptions):
                                other_event = y['EventID'] if x['EventID'] == curr_event else x['EventID']
                                exceptions.append([curr_event, other_event])
                            return True
                        return False
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
        self, solutions, domains, vconstraints, assignments, single, exceptions=[]
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

        variable = item[-1]
        assignments[variable] = None # add to

        # Case1
        for value in domains[variable]:
            assignments[variable] = value # {1: 'Case1'}

            for constraint, variables in vconstraints[variable]:
                if not constraint(variables, domains, assignments, exceptions):
                    # Value is not good.
                    if variable in [item[0] for item in exceptions]:
                        continue
                    else:
                        break
            else:
                # Value is good. Recurse and get next variable.
                self.recursiveBacktracking(
                    solutions, domains, vconstraints, assignments, single, exceptions
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

    data = data.to_dict(orient="records")

    solver = MyRecursiveBacktrackingSolver()
    # solver = RecursiveBacktrackingSolver()
    problem = Problem(solver)

    # constraints = {'unary': ["x['Timestamp'] < '2022-01-01 11:20:59'"],
    #                'binary': ["x['UserID'] == y['UserID']",
    #                           "x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'B' and y['Activity'] == 'A' else True" ]}

    constraints = {
                   'C6': "x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'A' and y['Activity'] == 'B' else True" }

    case = 1

    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(1, n_of_events+1)])

    problem.addConstraint(MyConstraint(data, constraints))
    solutions = problem.getSolution()

    return solutions




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    result = assign_cases()
    print(result)


