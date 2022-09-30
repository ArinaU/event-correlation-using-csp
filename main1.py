


from constraint import *
import pandas as pd
import numpy as np
import itertools
import math
import json

class MyConstraint(Constraint):

    def __init__(self, constraints):
        self._constraints = constraints

    def __call__(self, data, events, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        constraints = self._constraints

        curr_event = max(assignments.keys())
        suggested_case = assignments[curr_event]

        # get all events ids with this case
        last_events_ids = [key for key, value in assignments.items() if value == suggested_case]
        # get events themselves
        last_events = [value for key, value in data.items() if key in last_events_ids]

        if constraints and len(last_events) > 1:
            for cname, constraint in constraints.items():
                for x, y in itertools.permutations(last_events, 2):
                    if not eval(constraint):
                        return False
        return True



class MyRecursiveBacktrackingSolver(Solver):

    def __init__(self, data, start_event = 1, forwardcheck=True):
        """
        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._data = data
        self._start_event = start_event
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

        # Case1
        for value in domains[variable]:

            if self._data[variable]['Activity'] == self._start_event['Activity']: # if A
                # assignment_values = list(assignments.values())

                assignment_values = sorted([x for x in list(assignments.values()) if x is not None])
                last_assignment = assignment_values[-1] if len(assignment_values) > 0 else None

                if last_assignment:
                    index = domains[variable].index(last_assignment)
                    assignments[variable] = domains[variable][index + 1]

                    self.recursiveBacktracking(
                        solutions, domains, vconstraints, assignments, single
                    )
            else: # if B
                past_events = [key for key, val in assignments.items() if val == value]
                if not past_events:
                    assignments[variable] = None
                    self.recursiveBacktracking(
                        solutions, domains, vconstraints, assignments, single
                    )

            assignments[variable] = value  # {1: 'Case1'}

            for constraint, variables in vconstraints[variable]:
                if not constraint(self._data, variables, domains, assignments):
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



def assign_cases(data, start_event):

    n_of_events = len(data)

    data.set_index('EventID', inplace=True)
    data = data.to_dict(orient="index")

    # start_event = data[start_event_id]
    start_event = data[[key for key, val in data.items() if val[start_event[0]] == start_event[1]][0]]

    solver = MyRecursiveBacktrackingSolver(data, start_event)
    problem = Problem(solver)

    # constraints = {'C1': "x['UserID'] == y['UserID']",
    #                'C2': "x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'A' and y['Activity'] == 'B' else True" }

    constraints = { 'C1': "x['UserID'] == y['UserID']" }

    case = 1

    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(1, n_of_events+1)])


    problem.addConstraint(MyConstraint(constraints))
    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = ['Activity', 'A']

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


