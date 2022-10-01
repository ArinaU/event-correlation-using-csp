


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


class Existence(Constraint):

    def __init__(self, required_event):
        self._required_attr = required_event['attribute']
        self._required_value = required_event['value']


    def __call__(self, data, events, domains, assignments, forwardcheck=False, _unassigned=Unassigned):
        required_attr = self._required_attr
        required_value = self._required_value

        curr_event_id = max(assignments.keys())
        curr_event = data[curr_event_id]
        suggested_case = assignments[curr_event_id]

        past_events = [data[key] for key, val in assignments.items() if val == suggested_case]

        flag = True
        if curr_event_id == events[-1]:
            if required_value not in [event[required_attr] for event in past_events]:
            # for event in past_events:
            #     if event[required_attr] == required_value:
            #         flag = True
                flag = False

        # if curr_event_id == events[-1]: # if last event
        #     if curr_event[attr['attribute']] != attr['value']:
        #         flag = False
        return flag





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
        assignments[variable] = None
        # Case1
        for ind, value in enumerate(domains[variable]):

            if self._data[variable]['Activity'] == self._start_event['Activity']: # if A
                # assignment_values = list(assignments.values())

                assignment_values = sorted([x for x in list(assignments.values()) if x is not None])
                last_assignment = assignment_values[-1] if len(assignment_values) > 0 else None

                if last_assignment: # if not the 1st event
                    index = domains[variable].index(last_assignment)
                    # assignments[variable] = domains[variable][index + 1] # take next Case
                    assignments[variable] = domains[variable][(index + 1) % len(domains[variable])]

                    # self.recursiveBacktracking(
                    #     solutions, domains, vconstraints, assignments, single
                    # )
                else:
                    assignments[variable] = value  # TODO
            else: # if B
                past_events = [key for key, val in assignments.items() if val == value]
                if past_events:
                    assignments[variable] = value

            for constraint, variables in vconstraints[variable]:
                if not constraint(self._data, variables, domains, assignments):
                    # Value is not good.
                    assignments[variable] = None
                    break
            else:
                # Value is good. Recurse and get next variable.
                self.recursiveBacktracking(
                    solutions, domains, vconstraints, assignments, single
                )
                if solutions and single:
                    return solutions

        del assignments[variable]
        # assignments[variable] = None

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
    start_event = data[[key for key, val in data.items() if val[start_event['attribute']] == start_event['value']][0]]

    solver = MyRecursiveBacktrackingSolver(data, start_event)
    problem = Problem(solver)

    # constraints = { 'C1': "x['UserID'] == y['UserID']" }

    case = 1

    problem.addVariables(range(1, n_of_events+1), [f"Case{i}" for i in range(1, n_of_events+1)])


    # problem.addConstraint(Existence({'attribute': 'Activity', 'value': 'B'}))
    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = {'attribute': 'Activity', 'value': 'A'}

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


