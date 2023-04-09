from constraint import *
from copy import deepcopy

class BaseEventConstraint(Constraint):

    def __init__(self, data, start_event = None):
        self._data = data
        self._start_event = start_event

    def find_solutions(self, all_domains, case_status, events, other_event):
        left_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]
        arr = []
        for event in events:
            domains = all_domains[event]
            if set(left_cases) & set(domains):
                arr.append(event)
        return arr

    #
    # def strip(self, data):
    #     new_data = {}
    #     for k, v in data.items():
    #         if isinstance(v, dict):
    #             v = self.strip(v)
    #         if not v in (u'', None, {}, []):
    #             new_data[k] = v
    #     return new_data
    #
    #
    # def clean_case_status(self, assignments):
    #     assigned_events = list(assignments.keys())[:-1]
    #
    #     for k, v in deepcopy(self._case_status).items():
    #         if isinstance(v, dict):
    #             for a, b in v.items():
    #                 self._case_status[k][a] = [x for x in b if x in assigned_events]
    #         elif isinstance(v, list):
    #             self._case_status[k] = [x for x in v if x in assigned_events]
    #
    #     self._case_status = self.strip(self._case_status)

    def clean_struct(self, assignments, case_status):
        # Remove keys where values are '', None, {}, []
        for key, value in list(case_status.items()):
            if value in ('', None, {}, []):
                del case_status[key]

            # Recursively remove unused numbers
        last_key = list(assignments.keys())[-1]
        for key, value in list(case_status.items()):
            if isinstance(value, dict):
                case_status[key] = self.clean_struct(assignments, value)
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_dict = self.clean_struct(assignments, item)
                        if new_dict:
                            new_list.append(new_dict)
                    elif isinstance(item, int) and item < last_key:
                        new_list.append(item)
                case_status[key] = new_list
            elif isinstance(value, int) and value >= last_key:
                del case_status[key]

        return case_status

    def clean_buf2(self, assignments):
        buf = self._buf.copy()
        curr_id = list(assignments)[-1]
        # {'e2': [8]}
        for key, values in buf.items():
            self._buf[key] = [x for x in values if x < curr_id]
            # if it's empty after reassignment, only elmts >= curr_event were there
            if not self._buf[key]:
                del self._buf[key]