
from constraint import *

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
class Existence(Constraint):

    def __init__(self, data, required_event):
        self._data = data
        self._required_event = required_event


    def __call__(self, events, domains, assignments, forwardcheck=False):
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