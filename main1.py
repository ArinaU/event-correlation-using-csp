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


def get_matrix():
    raw_df = pd.read_csv('data1.csv', sep=';')
    n_of_cases = 3

    n_of_events = len(raw_df['EventID'])

    problem = Problem()
    result_df = pd.DataFrame(columns=[i for i in range(n_of_cases)])

    constraints = {0: {'attrs': ['Activity', 'Activity'], 'vals': ['A', 'B'], 'operator': ">"},
                   1: {'attrs': ['Activity', 'UserID'], 'vals': ['A', '2'], 'operator': "<"},
                   2: {'attrs': ['Activity'], 'vals': 'C', 'operator': "!="}}

    for nrow in range(n_of_events):
        curr = raw_df.loc[nrow].to_dict()
        dict = {}

        for i in range(n_of_cases):
            dict[i] = curr

        temp_df = result_df.append(dict, ignore_index=True)

        # Add cases from 0 to n
        problem.addVariable('Cases', [i for i in range(n_of_cases)])
        problem.addConstraint(MyConstraint(temp_df, constraints), ['Cases'])

        case = min([case['Cases'] for case in problem.getSolutions()]) # find 1st convenient case

        temp_df[temp_df.columns.difference([case])] = pd.NA

        result_df = temp_df #TODO delete temp_df ???

        print(result_df)

        problem.reset()















# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    get_matrix()

