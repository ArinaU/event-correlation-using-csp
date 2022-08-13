# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from constraint import *
import pandas as pd
import numpy as np
import itertools
import math


def generate_condition(*args, **kwargs):
    def f():
        flag = True
        constraints = kwargs['constraints']
        if len(args) == 2:
            x = args[0]  # B
            y = args[1]  # A
            if pd.isna(x) or pd.isna(y):
                return True
            else:
                attr = constraints['attrs'][0]
                attr2 = constraints['attrs'][1]
                # B == A and A == B
                if (x[attr] == constraints['vals'][0] and y[attr] == constraints['vals'][1]) or (
                        y[attr] == constraints['vals'][0] and x[attr] == constraints['vals'][1]):
                    flag = eval(f"{x['EventID']} {constraints['operator']} {y['EventID']}")
        elif len(args) == 1 and len(constraints['attrs']) == 1:
            x = args[0]
            attr = constraints['attrs']
            flag = eval(f"x{attr} {constraints['operator']} '{constraints['vals']}'") # TODO что-то с кавычками
        return flag

    return f


def get_solutions(df, nrow, curr, **kwargs):
    curr = df.loc[nrow].to_dict()
    problem = Problem()

    # problem.addVariable('2', [var1, var2])

    #     problem.addVariable(curr['EventID'], kwargs['column'])

    problem.addVariable(curr['EventID'], [curr])

    for constraint in kwargs['constraints']:
        problem.addConstraint(constraint, [curr['EventID']])

    solutions = problem.getSolutions()
    print(solutions)
    return solutions


def get_matrix():
    df = pd.read_csv('data1.csv', sep=';')
    cases = ['Case1', 'Case2', 'Case3']

    n_of_cases = len(cases)
    n_of_events = len(df['EventID'])

    # dict = { 'Case1': [{'EventID': 1, 'Activity': 'A', 'Timestamp': '2022-01-01 11:01:58', 'UserID': 1},
    #         {'EventID': 2, 'Activity': 'B', 'Timestamp': '2022-01-01 11:10:58', 'UserID': 1}],
    #          'Case2': np.NaN,
    #          'Case3': np.NaN }

    df2 = pd.DataFrame()
    problem = Problem()

    for nrow in range(n_of_cases):
        curr = df.loc[nrow].to_dict()

    curr = df.loc[2].to_dict()

    dict = {'Case1': curr, 'Case2': curr, 'Case3': curr}
    df3 = df2.append(dict, ignore_index=True)
    data = df3.to_dict()

    # print(data)

    problem.addVariable('Cases', ['Case1', 'Case2', 'Case3'])

    # constraints = {'attrs': ['Activity', 'Activity'], 'vals': ['A', 'C'], 'operator': ">"}

    constraints = {'Case1': {'attrs': ['Activity', 'Activity'], 'vals': ['A', 'C'], 'operator': ">"},
                   'Case2': {'attrs': ['Activity', 'UserID'], 'vals': ['A', '2'], 'operator': "<"},
                   'Case3': {'attrs': ['Activity'], 'vals': 'C', 'operator': "!="}}

    problem.addConstraint(MyConstraint(data, constraints), ['Cases'])
    print(problem.getSolutions())


class MyConstraint(Constraint):

    def __init__(self, data, constraints):
        self._data = data
        self._constraints = constraints

    def __call__(self, variables, domains, assignments, forwardcheck=False):
        data = self._data
        constraints = self._constraints
        for variable in variables:
            if variable in assignments:
                case = assignments[variable]
                column = data[case]
                flag = True
                if len(column) < 2:
                    cond = generate_condition(column[0], constraints=constraints[case])
                    flag = cond()
                else:
                    for x, y in itertools.combinations(column, 2):
                        cond = generate_condition(column[x], column[y], constraints = constraints[case])
                        flag = cond()
                        if not flag:
                            break
                return flag


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # UserID 3 !=
    # dict = {'Case1': { 'attrs': ['Activity', 'Activity'], 'vals': ['A', 'C'], 'operator': ">" },
    #         'Case2': { 'attrs': ['UserID'], 'vals': ['2'], 'operator': "!=" }}
    # print()

    # cond = generate_condition(x, y, attrs=['Activity', 'Activity'], vals=['A', 'C'], operator=">")

    get_matrix()

