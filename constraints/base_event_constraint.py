from constraint import *
from copy import deepcopy

class BaseEventConstraint(Constraint):

    def __init__(self):
        pass

    # def remove_old_assignments(self, assignments):
    #     # -1 because current assignment would be the last one in list
    #     assigned_events = list(assignments.keys())[:-1]
    #     case_status = self._case_status.copy()
    #     for key, events in case_status.items():
    #         self._case_status[key] = [x for x in events if x in assigned_events]
    #         if not self._case_status[key]:
    #             del self._case_status[key]

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