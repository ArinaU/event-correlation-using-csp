
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# A occurs at most once
class Absence(Constraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_event = required_event
        self._buf = {}

    def clear_buf(self, curr_event):
        buf = self._buf.copy()
        for key, value in buf.items():
            if value >= curr_event:
                del self._buf[key]


    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        buf = self._buf
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        curr_id = list(assignments)[-1]

        self.clear_buf(curr_id)

        if data[curr_id][required_attr] == required_value:
            if buf.get(assignments[curr_id], None):
                #if buffer[assignments[curr_event_id]]: # if event was before
                return False
            else:
                buf[assignments[curr_id]] = curr_id

        return True


# A occurs at least once
class Existence(BaseEventConstraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_event = required_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        self.clean_case_status(assignments)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if event
        if data[curr_id][required_attr] == required_value:
            if self._case_status[curr_case].get('e'):
                if [case for case in domains[curr_id] if case not in self._case_status.keys()]:
                    return False
            else:
                self._case_status[curr_case].setdefault('e', []).append(curr_id)

        # check at the last event
        if curr_id == len(events):
            for case in set(assignments.values()):
                if not self._case_status.get(case):
                    return False

        return True