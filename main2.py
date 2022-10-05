


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




class Absence(Constraint):

    def __init__(self, required_event):
        self._required_attr = required_event['attribute']
        self._required_value = required_event['value']


    def __call__(self, data, events, domains, assignments, exceptions, curr_event_id):
        required_attr = self._required_attr
        required_value = self._required_value

        curr_event = data[curr_event_id]
        suggested_case = assignments[curr_event_id]
        past_events = { key:data[key] for key, val in assignments.items() if val == suggested_case }

        # if event with this activity exists already within case
        if required_value not in [val[required_attr] for id, val in past_events.items()]:
            exceptions[curr_event_id] = True

            for event_id, status in exceptions.items():
                if event_id in past_events.keys():
                    # update all old exceptions
                    exceptions[event_id] = True
        else:
            exceptions[curr_event_id] = False

        if curr_event_id == events[-1]:
            if [key for key, value in exceptions.items() if value == False]:
                return False

        return True



class Existence(Constraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_attr = required_event['attribute']
        self._required_value = required_event['value']


    def __call__(self, data, events, assignments, domains):
        data = self._data
        required_attr = self._required_attr
        required_value = self._required_value

        curr_event_id = max(assignments.keys())
        suggested_case = assignments[curr_event_id]

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


def declare_domains(problem, data, start):
    attr = start['attribute']
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

    # start_event = data[start_event_id]
    start_event = data[[key for key, val in data.items() if val[start_data['attribute']] == start_data['value']][0]]

    solver = RecursiveBacktrackingSolver();
    problem = Problem(solver)

    # constraints = { 'C1': "x['UserID'] == y['UserID']" }

    declare_domains(problem, data, start_data)


    problem.addConstraint(Existence(data, {'attribute': 'Activity', 'value': 'B'}))
    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = {'attribute': 'Activity', 'value': 'A'}

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


