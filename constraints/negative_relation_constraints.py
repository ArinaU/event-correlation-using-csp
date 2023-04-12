
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint


# A and B never occur together: <C, C, A, C>, NOT: <B, C, A, C>
class NotCoexistence(BaseEventConstraint):
    def __init__(self, data, required_event, required_event2, start_event = None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']
        data = self._data

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self._case_status = self.clean_struct(assignments, self._case_status)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = []

        # if B
        if data[curr_id][required_attr] == required_value:
            not_target_event = self.find_single_event(curr_case, 'e2')
            if not_target_event:
                return False

            self._case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            not_target_event = self.find_single_event(curr_case, 'e')
            if not_target_event:
                return False

            self._case_status[curr_case].append({'e2': curr_id})

        return True


# B cannot occur after A: [^A]*(A[^B]*)* <B, B, C, A, A>, <B, B, C>, <A, A, C>
class NotSuccession(BaseEventConstraint):

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
            not_target_event = self.find_single_event(curr_case, 'e')
            if not_target_event:
                return False
            self._case_status[curr_case].append({'e2': curr_id})

        return True


# A and B cannot occur contiguously: <B, B, A, A>, <A, C, B, A, C, B>
# A and B occur if and only if no B occurs immediately after A
class NotChainSuccession(BaseEventConstraint):
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

        # if curr event C
        if data[curr_id][required_attr2] == required_value2:
            # if the key with CaseN exists
            if self._case_status.get(curr_case, {}).get('e'):
                # last event in CaseN
                last_id = self._case_status[curr_case]['e'][-1]
                # if last event in CaseN was A
                if data[last_id][required_attr] == required_value:
                    return False

        self._case_status[curr_case].setdefault('e', []).append(curr_id)

        return True
