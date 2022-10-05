


from constraint import *
import pandas as pd
import numpy as np
import itertools
import math
import json




class Absence(Constraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_event = required_event


    def __call__(self, data, events, assignments, domains):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']

        curr_event_id = max(assignments.keys())

        if curr_event_id == len(events):
            for case in sorted(set(assignments.values())):
                events_with_case = [data[event][required_attr] for event, assigned_case in assignments.items() if case == assigned_case]

                if events_with_case.count(required_value) > 1:
                    return False

        return True




class Existence(Constraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_event = required_event


    def __call__(self, data, events, assignments, domains):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']

        curr_event_id = max(assignments.keys())

        if curr_event_id == len(events):
            for case in sorted(set(assignments.values())):
                flag = False
                for event, assigned_case in assignments.items():
                    if case == assigned_case:
                        if data[event][required_attr] == required_value:
                            flag = True
                if not flag:
                    return False

        return True



class RespondedExistence(Constraint):

    def __init__(self, data, required_event, required_event2):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2


    def __call__(self, data, events, assignments, domains):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_event_id = max(assignments.keys())

        if curr_event_id == len(events):
            for case in sorted(set(assignments.values())):
                events_with_case = [data[event][required_attr] for event, assigned_case in assignments.items() if
                                    case == assigned_case]

                if events_with_case.count(required_value) >= 1 and events_with_case.count(required_value2) < 1:
                    return False

        return True



def declare_domains(problem, data, start):
    attr = start['attr']
    value = start['value']
    iter = 1
    for id, val in data.items():
        if val[attr] == value:
            problem.addVariable(id, [f"Case{iter}"])
            iter += 1
        else:
            problem.addVariable(id, [f"Case{i}" for i in range(1, iter)])



def assign_cases(data, start_data):

    data.set_index('EventID', inplace=True)
    data = data.to_dict(orient="index")


    # start_event = data[[key for key, val in data.items() if val[start_data['attr']] == start_data['value']][0]]

    solver = RecursiveBacktrackingSolver();
    problem = Problem(solver)


    declare_domains(problem, data, start_data)


    problem.addConstraint(RespondedExistence(data,
                                             {'attr': 'Activity', 'value': 'A'},
                                             {'attr': 'Activity', 'value': 'B'}))
    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = {'attr': 'Activity', 'value': 'A'}

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


