
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    def __init__(self, data, required_event, required_event2):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
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

        self.clean_case_status(assignments)
        self.clean_buf(assignments)

        if not self._case_status.get(curr_case, None):
            self._case_status[curr_case] = {}

        # if B
        if data[curr_id][required_attr] == required_value:
            # if B already exists
            if self._case_status[curr_case].get('e'):
                if self.find_solutions(domains, self._case_status, [curr_id], 'e'):
                    return False
                else:
                    buf.setdefault('e', []).append(curr_id)
            else:
                # case_status.setdefault(curr_case, {})['e'] = curr_id
                self._case_status[curr_case].setdefault('e', []).append(curr_id)
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            if self._case_status[curr_case].get('e2'):
                # if C already exists
                if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
                    return False
                else:
                    buf.setdefault('e2', []).append(curr_id)
            else:
                # case_status.setdefault(curr_case, {})['e2'] = curr_id
                self._case_status[curr_case].setdefault('e2', []).append(curr_id)

        if buf.get('e', None):
            if self.find_solutions(domains, self._case_status, buf['e'], 'e'):
                return False
        elif buf.get('e2', None):
            if self.find_solutions(domains, self._case_status, buf['e2'], 'e2'):
                return False

        return True


