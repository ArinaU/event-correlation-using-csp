


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


    def __call__(self, data, events, domains, assignments, exceptions, curr_event_id):
        required_attr = self._required_attr
        required_value = self._required_value

        curr_event = data[curr_event_id]
        suggested_case = assignments[curr_event_id]

        # past_events = [data[key] for key, val in assignments.items() if val == suggested_case]
        past_events = { key:data[key] for key, val in assignments.items() if val == suggested_case }

        # if event with this activity exists already within case
        if required_value in [val[required_attr] for id, val in past_events.items()]:
            exceptions[curr_event_id] = [True, suggested_case]

            for event_id, status in exceptions.items():
                if event_id in past_events.keys():
                    # update all old exceptions
                    exceptions[event_id] = [True, suggested_case]
        else:
            exceptions[curr_event_id] = [False, suggested_case]

        if curr_event_id == events[-1]:
            if [key for key, value in exceptions.items() if value[0] == False]:
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


    # def recursiveBacktracking2(
    #     self, solutions, domains, vconstraints, assignments, single, curr_index
    # ):
    #
    #     # Mix the Degree and Minimum Remaing Values (MRV) heuristics
    #     lst = [
    #         (-len(vconstraints[variable]), len(domains[variable]), variable)
    #         for variable in domains
    #     ]
    #     lst.sort()
    #     for item in lst: #(-1, 4, 1)
    #         if item[-1] not in assignments: # {}
    #             # Found an unassigned variable. Let's go.
    #             break
    #     else:
    #         # No unassigned variables. We've got a solution.
    #         solutions.append(assignments.copy())
    #         return solutions
    #
    #     variable = item[-1] # 1
    #
    #     value = domains[variable][curr_index]
    #     # assignments[variable] = None
    #
    #     # for ind, value in enumerate(domains[variable]): #REMOVE
    #     last_assignments = sorted([x for x in list(set(assignments.values())) if x is not None])
    #     if self._data[variable]['Activity'] == self._start_event['Activity']: # if A
    #
    #             # assignment_values = sorted([x for x in list(assignments.values()) if x is not None])
    #         last_assignment = last_assignments[-1] if len(last_assignments) > 0 else None
    #         if curr_index < len(domains[variable]):
    #             if last_assignment: # if not the 1st event
    #                 index = domains[variable].index(last_assignment)
    #                 assignments[variable] = domains[variable][index + 1]
    #             else:
    #                 assignments[variable] = value  # TODO
    #     else: # if B
    #         if value in last_assignments:
    #             assignments[variable] = value
    #
    #     flag = True
    #
    #     for constraint, variables in vconstraints[variable]:
    #         if not constraint(self._data, variables, domains, assignments):
    #             # Value is not good.
    #             assignments[variable] = None
    #             # break
    #             self.recursiveBacktracking(
    #                 solutions, domains, vconstraints, assignments, single, curr_index
    #             )
    #     else:
    #         # Value is good. Recurse and get next variable.
    #         self.recursiveBacktracking(
    #             solutions, domains, vconstraints, assignments, single, curr_index
    #         )
    #         if solutions and single:
    #             return solutions
    #
    #     # del assignments[variable]
    #
    #     return solutions


    def recursiveBacktracking(
        self, solutions, domains, vconstraints, assignments, single, exceptions
    ):

        # Mix the Degree and Minimum Remaing Values (MRV) heuristics
        lst = [
            (-len(vconstraints[variable]), len(domains[variable]), variable)
            for variable in domains
        ]
        lst.sort()
        for item in lst: #(-1, 4, 1)
            if not assignments[item[-1]]:
                # Found an unassigned variable. Let's go.
                break
        else:
            # No unassigned variables. We've got a solution.
            solutions.append(assignments.copy())
            return solutions

        variable = item[-1] # 1

        last_cases = sorted([x for x in list(set(assignments.values())) if x is not None])
        exception = exceptions[variable][1]


        if last_cases:
            if exception:
                idx = last_cases.index(exception) + 1
                if idx < len(last_cases):
                    assignments[variable] = last_cases[idx]  # next
            else:
                # if 'A' then get last max case
                if self._data[variable]['Activity'] == self._start_event['Activity']:
                    max_used_case = last_cases[-1]
                    idx = domains[variable].index(max_used_case) + 1
                    if idx < len(domains[variable]):
                        assignments[variable] = domains[variable][idx]
                else:
                    # get only among already used cases
                    assignments[variable] = last_cases[0]
        else:
            # first initialization
            assignments[variable] =  domains[variable][0]


        for constraint, variables in vconstraints[variable]:
            if not constraint(self._data, variables, domains, assignments, exceptions, variable):
                # Value is not good.
                assignments[variable] = None
                # break
                self.recursiveBacktracking(
                    solutions, domains, vconstraints, assignments, single, exceptions
                )
        else:
            # Value is good. Recurse and get next variable.
            self.recursiveBacktracking(
                solutions, domains, vconstraints, assignments, single, exceptions
            )
            if solutions and single:
                return solutions

        # del assignments[variable]

        return solutions


    def getSolution(self, domains, constraints, vconstraints):
        assignments = dict.fromkeys(domains.keys())
        exceptions = dict.fromkeys(domains.keys(), [None, None])
        solutions = self.recursiveBacktracking([], domains, vconstraints, assignments, True, exceptions)
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


    problem.addConstraint(Existence({'attribute': 'Activity', 'value': 'B'}))
    solutions = problem.getSolution()

    return solutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_event = {'attribute': 'Activity', 'value': 'A'}

    data = pd.read_csv('data.csv', sep=';')

    result = assign_cases(data, start_event)
    print(result)


