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
        if len(args) == 2:
            x = args[0]  # B
            y = args[1]  # A
            if pd.isna(x) or pd.isna(y):
                return True
            else:
                attr = kwargs['attrs'][0]
                attr2 = kwargs['attrs'][1]
                # B == A and A == B
                if (x[attr] == kwargs['vals'][0] and y[attr] == kwargs['vals'][1]) or (
                        y[attr] == kwargs['vals'][0] and x[attr] == kwargs['vals'][1]):
                    flag = eval(f"{x['EventID']} {kwargs['operator']} {y['EventID']}")
        elif len(args) == 1:
            x = args[0]
            attr = kwargs['attr']
            flag = eval(f"x[attr] {kwargs['operator']} {kwargs['val']}")
        return flag

    return f


# Hardcoded Constraints for 1st Case
def binary_constraint(*args):
    flag = True
    for x, y in itertools.combinations(args, 2):
        cond = generate_condition(x, y, attrs=['Activity', 'Activity'], vals=['A', 'B'], operator=">")
        if not cond():
            flag = False
            break
    return flag


def unary_constraint(*args):
    flag = True
    for x in args:
        cond = generate_condition(x, attr='UserID', val="3", operator="!=")
        if not cond():
            flag = False
            break
    return flag

# Main()

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


def get_matrix1():

    df = pd.read_csv('data1.csv', sep=';')

    n_of_cases = len(df)
    n_of_events = len(df['EventID'])

    matr = np.zeros((n_of_cases, n_of_events))

    df2 = pd.DataFrame(columns=["Case1", "Case2", "Case3"])


    for nrow in range(n_of_cases):
        curr = df.loc[nrow].to_dict()
        for col in df2:
            if col == 'Case1':
                new_column = curr

                solutions = get_solutions(df, nrow, curr, column=new_column, constraints=[unary_constraint])
                if solutions:
                    var = list(solutions[0].values())[0]['EventID']
                    df2 = df2.append({'Case1': solutions[0][var], 'Case2': np.NaN, 'Case3': np.NaN}, ignore_index=True)
                    break
    #         elif col == 'Case2':
    #             new_column = curr

    #             solutions = get_solutions(curr, column = new_column, constraints = [unary_constraint2])
    #             if solutions:
    #                 var = list(solutions[0].values())[0]['EventID']
    #                 df2 = df2.append({'Case1': np.NaN, 'Case2': solutions[0][var], 'Case3': np.NaN}, ignore_index=True)
    #                 break
    #         elif col == 'Case3':
    #             new_column = curr

    #             solutions = get_solutions(curr, column = new_column, constraints = [unary_constraint3])
    #             if solutions:
    #                 var = list(solutions[0].values())[0]['EventID']
    #                 df2 = df2.append({'Case1': np.NaN, 'Case2': solutions[0][var], 'Case3': np.NaN}, ignore_index=True)
    #                 break
    return df2


def get_matrix():
    df = pd.read_csv('data1.csv', sep=';')

    # n_of_cases = len(df)

    cases = ['Case1', 'Case2', 'Case3']

    n_of_events = len(df['EventID'])

    # df2 = pd.DataFrame(columns=["Case1", "Case2", "Case3"])



    dict = { 'Case1': [{'EventID': 1, 'Activity': 'A', 'Timestamp': '2022-01-01 11:01:58', 'UserID': 1},
            {'EventID': 2, 'Activity': 'B', 'Timestamp': '2022-01-01 11:10:58', 'UserID': 1}],
             'Case2': np.NaN,
             'Case3': np.NaN }

    # dict = [{'EventID': 1, 'Activity': 'A', 'Timestamp': '2022-01-01 11:01:58', 'UserID': 1},
    #         {'EventID': 2, 'Activity': 'B', 'Timestamp': '2022-01-01 11:10:58', 'UserID': 1}]

    # df2 = pd.DataFrame(dict) #!! in a certain case

    df2 = pd.DataFrame(dict)

    problem = Problem()

    # for row in range(n_of_events):
    #     curr = df.loc[row].to_dict()
    #     # for case in cases:
    #
    #     dict = { 'Case1': curr, 'Case2': curr, 'Case3': curr }
    #     df3 = df2.append(dict, ignore_index=True)
    #
    #     data = df3.to_dict()
    #
    #     problem.addVariable('Data', data)
    #     problem.addVariable('Cases', ['Case1', 'Case2', 'Case3'])
    #
    #     problem.addConstraint(my_constraint, ['Data', 'Cases'])
    #     print(problem.getSolutions())
    #     problem.reset()

    curr = df.loc[2].to_dict()

    dict = {'Case1': curr, 'Case2': curr, 'Case3': curr}
    df3 = df2.append(dict, ignore_index=True)

    data = df3.to_dict()

    # problem.addVariable('Data', data)
    problem.addVariable('Cases', ['Case1', 'Case2', 'Case3'])

    problem.addConstraint(MyConstraint(data), ['Cases'])
    print(problem.getSolutions())


class MyConstraint(Constraint):

    def __init__(self, data):
        self._data = data

    def __call__(self, variables, domains, assignments, forwardcheck=False):
        data = self._data
        for variable in variables:
            if variable in assignments:
                case = assignments[variable]
                column = data[case]
                for x, y in itertools.combinations(column, 2):
                    x = column[x]
                    y = column[y]
                    cond = generate_condition(x, y, attrs=['Activity', 'Activity'], vals=['A', 'C'], operator=">")
                    flag = cond()
                    if not flag:
                        return False
                return True



# def my_constraint(data):
#     column = data[case]
#     flag = True
#     for x, y in itertools.combinations(column, 2):
#         cond = generate_condition(x, y, attrs=['Activity', 'Activity'], vals=['A', 'C'], operator=">")
#         if not cond():
#             flag = False
#             break
#
#     return flag # binary_constraint(column)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # df2 = get_matrix()
    #
    # var1 = 'Case1'
    # var2 = 'Case2'
    # var3 = 'Case3'
    #
    # problem = Problem()
    #
    # problem.addVariable('Event', [var1, var2, var3])
    #
    # problem.addConstraint(my_constraint, ['Event'])
    #
    # print(problem.getSolutions())

    get_matrix()

