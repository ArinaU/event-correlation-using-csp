


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
        unary_constraints = constraints[1]
        binary_constraints = constraints[2]
        data = self._data
        #for event in events:
        # print(event)
        curr_event = max(assignments, key=assignments.get)
        suggested_case = assignments[curr_event]

        # get all events with this case
        last_events_ids = [key for key, value in assignments.items() if value == suggested_case]

        last_events = [event for event in data if event['EventID'] in last_events_ids]

        result = True
        if binary_constraints and len(last_events) > 1:
            for constraint in binary_constraints:
                for x, y in itertools.permutations(last_events, 2):
                    result = eval(constraint)
                    if not result:
                        break
        elif unary_constraints:
            for x in last_events:
                result = eval(x)
                if not result:
                    break
        return result






        # for variable in variables:
        #     if variable in assignments:
        #         case = assignments[variable]
        #         column = data[case]
        #         flag = True
        #         if len(column) < 2:
        #             cond = generate_condition(column[0], constraints=constraints[case])
        #             flag = cond()
        #         else:
        #             for x, y in itertools.permutations(column, 2):
        #                 cond = generate_condition(x, y, constraints = constraints[case])
        #                 flag = cond()
        #                 if not flag:
        #                     break
        #         return flag



def assign_cases():
    data = pd.read_csv('data.csv', sep=';')
    n_of_events = len(data)

    # add empty column with cases
    data = data.assign(CaseID=None)
    data = data.to_dict(orient="records")
    # data = list(data.to_records(index=False)) # to tuple

    problem = Problem()

    # result_df = pd.DataFrame(columns=[i for i in range(n_of_events)])

    # raw_df.loc[raw_df['Activity'] == 'B']

    constraints = {1: [], 2: ["x['Timestamp'] < y['Timestamp'] if x['Activity'] == 'B' and y['Activity'] == 'A' else True"]}

    case = 1
    # for nrow in range(n_of_events):
    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(1, n_of_events+1)])

    problem.addConstraint(MyConstraint(data, constraints))
    solutions = problem.getSolution()

    return solutions




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    result = assign_cases()

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


