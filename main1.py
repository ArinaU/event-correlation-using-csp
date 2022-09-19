


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
                        break
        return True



def assign_cases():
    data = pd.read_csv('data.csv', sep=';')
    n_of_events = len(data)

    # add empty column with cases
    data = data.assign(CaseID=None)
    data = data.to_dict(orient="records")

    problem = Problem()

    constraints = {'unary': ["x['Timestamp'] < '2022-01-01 11:20:59'"],
                   'binary': ["x['UserID'] == y['UserID']", "x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'B' and y['Activity'] == 'A' else True"]}

    case = 1
    # for nrow in range(n_of_events):
    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(n_of_events, 0, -1)])

    problem.addConstraint(MyConstraint(data, constraints))
    solutions = problem.getSolution()

    return solutions




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    result = assign_cases()
    print(result)
    # problem = Problem()
    # problem.addVariable("a", [1, 2, 3])
    # problem.addConstraint(AllDifferentConstraint())
    # problem.addVariables("b", [4, 5, 6])
    # print(problem.getSolutions())

    # problem = Problem()
    # numpieces = 4
    # cols = range(numpieces)
    # rows = range(numpieces)
    # problem.addVariables(cols, rows)
    # for col1 in cols:
    #     for col2 in cols:
    #         if col1 < col2:
    #             problem.addConstraint(lambda row1, row2: row1 != row2, (col1, col2))
    # solutions = problem.getSolutions()
    # solutions

    # problem = Problem()
    # problem.addVariables(["a", "b"], [1, 2, 3])
    # problem.addConstraint(AllDifferentConstraint())
    # print(problem.getSolution())


