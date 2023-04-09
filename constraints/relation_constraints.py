
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):

    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}
        self._buf = {}


    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        buf = self._buf
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']
        curr_id = list(assignments)[-1]

        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)
        self.clean_buf2(assignments)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if B
        if data[curr_id][required_attr] == required_value:
            self._case_status[curr_case].setdefault('e', []).append(curr_id)
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            # if case_status[curr_case].get('e2'):
            if 'e2' in self._case_status[curr_case]: # if C already exists
                if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
                    return False
                else:
                    buf.setdefault('e2', []).append(curr_id)
            else:
                self._case_status[curr_case].setdefault('e2', []).append(curr_id)

        if buf:
            if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
                return False

        return True



# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if B
        if data[curr_id][required_attr] == required_value:
            # if C already exists in curr case
            if self._case_status[curr_case].get('e2'):
                last_e2_id = self._case_status[curr_case]['e2'][-1]
                # if last C happens before current B
                if last_e2_id < curr_id:
                    return False
            self._case_status[curr_case].setdefault('e', []).append(curr_id)
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            # if B was not before in curr case or B and C constr already satisfied
            if not self._case_status[curr_case].get('e') or \
                    (self._case_status[curr_case].get('e') and self._case_status[curr_case].get('e2')):
                # find other cases without C
                if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
                    return False

            self._case_status[curr_case].setdefault('e2', []).append(curr_id)

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
class Precedence(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = []

        # if B
        if data[curr_id][required_attr] == required_value:
            self._case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            # if B was before
            flag = False
            for pair in self._case_status[curr_case]:
                if not (flag or 'e2' in pair):
                    pair['e2'] = curr_id
                    flag = True

            if not flag:
                return False

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):
    lock = {}

    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}


    def clean_struct(self, assignments, case_status):
        assigned_events = list(assignments.keys())[:-1]

        for k, v in deepcopy(case_status).items():
            for a, b in v.items():
                if a not in assigned_events:
                    self._case_status[k][a] = None
                elif b not in assigned_events:
                    self._case_status[k][a] = False

        return self.strip(case_status)


    def find_solutions(self, all_domains, case_status, events, other_event = None):
        left_cases = [c for c, v in case_status.items() if case_status[c] and False in case_status[c].values()]
        arr = []
        for event in events:
            domains = all_domains[event]
            if set(left_cases) & set(domains):
                arr.append(event)
        return arr

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        if ChainResponse.lock.get(curr_id) == self:
            ChainResponse.lock[curr_id] = None

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        case_events = sorted([e for e, c in assignments.items() if c == curr_case])
        last_id = case_events[-2] if len(case_events) > 1 else None

        # if curr element is C
        if data[curr_id][required_attr2] == required_value2:
            # if available B is found
            if last_id and data[last_id][required_attr] == required_value:
                self._case_status[curr_case][last_id] = curr_id
                ChainResponse.lock[curr_id] = self
            else:
                # check other cases
                if not ChainResponse.lock.get(curr_id) and self.find_solutions(domains, self._case_status, [curr_id]):
                    return False

        else: # if B or any other Activity
            if False in self._case_status[curr_case].values():
                return False

            # if curr element is B
            if data[curr_id][required_attr] == required_value:
                self._case_status[curr_case][curr_id] = False

        return True



class ChainPrecedence(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}


    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if C?
        if data[curr_id][required_attr2] == required_value2:
            if self._case_status[curr_case].get('e'):
                # If B isn't immediately beforehand
                last_id = self._case_status[curr_case]['e'][-1]
                if not data[last_id][required_attr] == required_value:
                    return False

        self._case_status[curr_case].setdefault('e', []).append(curr_id)

        return True



# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if B
        if data[curr_id][required_attr] == required_value:
            # if C was before
            if self._case_status[curr_case].get('e2'):
                # pop everything and add new B
                self._case_status[curr_case] = {'e': [curr_id] }
            # only B was before, no C
            elif self._case_status[curr_case].get('e'):
                return False
            # first time B
            else:
                self._case_status[curr_case].setdefault('e', []).append(curr_id)
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            # add C after B
            # if B was before
            if self._case_status[curr_case].get('e'):
                # if it's first C
                if not self._case_status[curr_case].get('e2'):
                    # pop everything
                    del self._case_status[curr_case]
                    return True
            if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
                return False

        return True



# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
class AlternatePrecedence(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = []

        # if B
        if data[curr_id][required_attr] == required_value:
            self._case_status[curr_case].append({'e': curr_id})

        # if C
        elif data[curr_id][required_attr2] == required_value2:
            if self._case_status[curr_case]:
                max_val = 0
                pair_ind = None
                for ind, pair in enumerate(self._case_status[curr_case]):
                    for event, val in pair.items():
                        if val > max_val:
                            max_val = val
                            pair_ind = ind
                if 'e2' in self._case_status[curr_case][pair_ind]:
                    return False
                else:
                    self._case_status[curr_case][pair_ind]['e2'] = curr_id
            else:
                return False

        return True

