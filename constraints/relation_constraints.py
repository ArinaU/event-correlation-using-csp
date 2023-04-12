
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
        # self._buf = {}


    def has_available_solutions(self, all_domains, case_status, events, other_event):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        # free_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        free_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if other_event not in pair:
                    free_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        for event in events:
            domains = all_domains[event]
            if set(free_cases) & set(domains):
                return True

        return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        # buf = self._buf
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']
        curr_id = list(assignments)[-1]

        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)
        # self.clean_buf2(assignments)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = []

        # if B
        if data[curr_id][required_attr] == required_value:
            target_event = self.find_single_event(curr_case, 'e2')
            if target_event:
                target_event['e'] = curr_id
            else:
                if self.has_available_solutions(domains, self._case_status, curr_id, 'e'):
                    return False
                else:
                    self._case_status[curr_case].append({'e': curr_id})
        # if C
        # A,C,B,A,A,B,C,C,B
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, self._case_status, curr_id, 'e2'):
                    return False
                else:
                    self._case_status[curr_case].append({'e2': curr_id})

        return True



# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}


    def has_available_solutions(self, all_domains, case_status, events, other_event):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        # free_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        free_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if other_event not in pair:
                    free_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        for event in events:
            domains = all_domains[event]
            if set(free_cases) & set(domains):
                return True

        return False

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

        if data[curr_id][required_attr] == required_value:
            # pair where there's no 'e2'
            if self.find_pairs_with_event(curr_case, 'e2'):
                return False
            else:
                self._case_status[curr_case].append({'e': curr_id})
        # if C
        # A,C,A,B,C,C,A,B
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, self._case_status, curr_id, 'e2'):
                    return False
                else:
                    self._case_status[curr_case].append({'e2': curr_id})

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
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
            target_event = self.find_single_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
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


    # def clean_struct(self, assignments, case_status):
    #     assigned_events = list(assignments.keys())[:-1]
    #
    #     for k, v in deepcopy(case_status).items():
    #         for a, b in v.items():
    #             if a not in assigned_events:
    #                 self._case_status[k][a] = None
    #             elif b not in assigned_events:
    #                 self._case_status[k][a] = False
    #
    #     return self.strip(case_status)
    #
    #
    # def has_available_solutions(self, all_domains, case_status, events, other_event = None):
    #     if not isinstance(events, list):
    #         events = [events]
    #
    #     left_cases = [c for c, v in case_status.items() if case_status[c] and False in case_status[c].values()]
    #     arr = []
    #     for event in events:
    #         domains = all_domains[event]
    #         if set(left_cases) & set(domains):
    #             arr.append(event)
    #     return arr

    def has_available_solutions(self, all_domains, case_status, events, other_event):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        # free_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        free_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if other_event not in pair:
                    free_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        for event in events:
            domains = all_domains[event]
            if set(free_cases) & set(domains):
                return True

        return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        # if ChainResponse.lock.get(curr_id) == self:
        #     ChainResponse.lock[curr_id] = None

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = []

        # case_events = sorted([e for e, c in assignments.items() if c == curr_case])
        # last_id = case_events[-2] if len(case_events) > 1 else None

        # # if curr element is C
        # if data[curr_id][required_attr2] == required_value2:
        #     # if available B is found
        #     if last_id and data[last_id][required_attr] == required_value:
        #         self._case_status[curr_case][last_id] = curr_id
        #         ChainResponse.lock[curr_id] = self
        #     else:
        #         # check other cases
        #         if not ChainResponse.lock.get(curr_id) and self.has_available_solutions(domains, self._case_status,
        #                                                                                 curr_id, ):
        #             return False
        #
        # else: # if B or any other Activity
        #     if False in self._case_status[curr_case].values():
        #         return False
        #
        #     # if curr element is B
        #     if data[curr_id][required_attr] == required_value:
        #         self._case_status[curr_case][curr_id] = False

        # if curr element is B
        # if B

        # A,B,A,D,C,B,A,D,C,C

        # if B
        if data[curr_id][required_attr] == required_value:
            self._case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, self._case_status, curr_id, 'e2'):
                    return False
        else:
            if self.find_single_event(curr_case, 'e'):
                return False

        return True



class ChainPrecedence(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}


    # each time B occurs, A immediately beforehand
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

        if data[curr_id][required_attr] == required_value:
            self._case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_id]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was not B
                if not data[prev_id][required_attr] == required_value:
                    return False

            self._case_status[curr_case].append({'e2': curr_id})

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

    def has_available_solutions(self, all_domains, case_status, events, other_event):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        # free_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        free_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if other_event not in pair:
                    free_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        for event in events:
            domains = all_domains[event]
            if set(free_cases) & set(domains):
                return True

        return False

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
            not_target_event = self.find_single_event(curr_case, 'e')
            if not_target_event:
                return False
            self._case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, self._case_status, curr_id, 'e2'):
                    return False
                else:
                    self._case_status[curr_case].append({'e2': curr_id})

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
                last_pair = self._case_status[curr_case][-1]
                if 'e2' in last_pair:
                    return False
                else:
                    last_pair['e2'] = curr_id
            else:
                return False

        return True

