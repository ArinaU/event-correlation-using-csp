


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

        # check at the last event
        if curr_event_id == len(events):
            for case in sorted(set(assignments.values())):
                events_with_case = [data[event][required_attr] for event, assigned_case in assignments.items()
                                    if case == assigned_case]
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

        # check at the last event
        if curr_event_id == len(events):
            # iterate over the set of cases
            for case in sorted(set(assignments.values())):
                flag = False
                # check the events of each case
                for event, assigned_case in assignments.items():
                    if case == assigned_case:
                        if data[event][required_attr] == required_value:
                            flag = True
                # if for this case we didn't find an event with the required attr
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
                events_with_case = [data[event] for event, assigned_case in assignments.items() if
                                    case == assigned_case]
                # if A happens, but B is absent, then return False
                if sum(x.get(required_attr) == required_value for x in events_with_case) >= 1 \
                        and sum(x.get(required_attr2) == required_value2 for x in events_with_case) == 0:
                    return False
        return True



class Coexistence(Constraint):

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
                events_with_case = [data[event] for event, assigned_case in assignments.items() if
                                    case == assigned_case]
                # if A occurs then B occurs and vice versa
                if (sum(x.get(required_attr) == required_value for x in events_with_case) >= 1
                    and sum(x.get(required_attr2) == required_value2 for x in events_with_case) == 0) \
                        or (sum(x.get(required_attr) == required_value for x in events_with_case) == 0
                            and sum(x.get(required_attr2) == required_value2 for x in events_with_case) >= 1):
                    return False

        return True


# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
# class Response(Constraint):
#     def __init__(self, data, required_event, required_event2):
#         self._data = data
#         self._required_event = required_event
#         self._required_event2 = required_event2
#
#     def __call__(self, data, events, assignments, domains):
#         data = self._data
#         required_attr = self._required_event['attr']
#         required_value = self._required_event['value']
#         required_attr2 = self._required_event2['attr']
#         required_value2 = self._required_event2['value']
#
#         curr_event_id = max(assignments.keys())
#
#         if curr_event_id == len(events):
#             for case in sorted(set(assignments.values())):
#                 events_with_case = [data[event] for event, assigned_case in assignments.items() if
#                                     case == assigned_case]
#
#                 flag = True
#                 for x, y in itertools.permutations(events_with_case, 2):
#                     # if A occurs
#                     if x[required_attr] == required_value:
#                         flag = False # if only A for now
#                         # if B occurs
#                         if y[required_attr2] == required_value2:
#                             # if A occurs after B
#                             flag = True
#                             if x['Timestamp'] > y['Timestamp']:
#                                 return False
#                 if not flag:
#                     return False
#
#         return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
class Precedence(Constraint):
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
                events_with_case = [data[event] for event, assigned_case in assignments.items() if
                                    case == assigned_case]

                for x, y in itertools.permutations(events_with_case, 2):
                    # if B occurs
                    if x[required_attr2] == required_value2:
                        # if A occurs
                        if y[required_attr] == required_value:
                            # if B occurs after A
                            if x['Timestamp'] < y['Timestamp']:
                                return False
        return True




def declare_domains(problem, data, start):
    attr = start['attr']
    value = start['value']
    iter = 1
    for id, val in data.items():
        # if equal to start event
        if val[attr] == value:
            problem.addVariable(id, [f"Case{iter}"])
            iter += 1
        # if n-th events
        else:
            problem.addVariable(id, [f"Case{i}" for i in range(1, iter)])



def assign_cases(data, start_data):

    data.set_index('EventID', inplace=True)
    data = data.to_dict(orient="index")


    # start_event = data[[key for key, val in data.items() if val[start_data['attr']] == start_data['value']][0]]

    solver = RecursiveBacktrackingSolver();
    problem = Problem(solver)


    declare_domains(problem, data, start_data)

    # problem.addConstraint(Absence(data, {'attr': 'Activity', 'value': 'B'}))

    # problem.addConstraint(Existence(data, {'attr': 'Activity', 'value': 'B'}))

    # problem.addConstraint(RespondedExistence(data,
    #                                          {'attr': 'Activity', 'value': 'A'},
    #                                          {'attr': 'Activity', 'value': 'B'}))

    problem.addConstraint(Response(data,
                                      {'attr': 'Activity', 'value': 'A'},
                                      {'attr': 'Activity', 'value': 'B'}))

    # problem.addConstraint(Precedence(data,
    #                                   {'attr': 'Activity', 'value': 'B'},
    #                                   {'attr': 'Activity', 'value': 'C'}))

    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = {'attr': 'Activity', 'value': 'A'}

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


