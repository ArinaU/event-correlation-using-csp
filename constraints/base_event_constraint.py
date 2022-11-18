from constraint import *
from copy import deepcopy

class BaseEventConstraint(Constraint):

    def __init__(self):
        pass

    def find_solutions(self, all_domains, case_status, events, other_event):
        left_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        arr = []
        for event in events:
            domains = all_domains[event]
            if set(left_cases) & set(domains):
                arr.append(event)
        return arr


    def strip(self, data):
        new_data = {}
        for k, v in data.items():
            if isinstance(v, dict):
                v = self.strip(v)
            if not v in (u'', None, {}, []):
                new_data[k] = v
        return new_data


    def clean_case_status(self, assignments):
        assigned_events = list(assignments.keys())[:-1]

        for k, v in deepcopy(self._case_status).items():
            for a, b in v.items():
                self._case_status[k][a] = [x for x in b if x in assigned_events]

        self._case_status = self.strip(self._case_status)


    def clean_buf(self, assignments):
        buf = self._buf.copy()
        curr_id = list(assignments)[-1]
        # {'e2': [8]}
        for key, values in buf.items():
            self._buf[key] = [x for x in values if x < curr_id]
            # if it's empty after reassignment, only elmts >= curr_event were there
            if not self._buf[key]:
                del self._buf[key]