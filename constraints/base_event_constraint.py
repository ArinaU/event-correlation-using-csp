from constraint import *
from copy import deepcopy

class BaseEventConstraint(Constraint):

    def __init__(self, data, start_event = None):
        self._data = data
        self._start_event = start_event

    @staticmethod
    def set_other_event(event):
        return 'e2' if event == 'e' else 'e'

    def has_available_solutions(self, all_domains, case_status, events, other_event):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        free_cases = [c for c,v in case_status.items() if case_status[c] and other_event not in case_status[c]]

        # check if there are events that can be assigned to free cases
        for event in events:
            domains = all_domains[event]
            if set(free_cases) & set(domains):
                return True

        return False


    def find_pairs_with_event(self, curr_case, target_event):
        pairs = []
        for pair in self._case_status[curr_case]:
            if target_event in pair:
                pairs.append(pair)
        return pairs


    def find_single_event(self, curr_case, target_event): # e
        # get first available pair
        other_event = self.set_other_event(target_event)
        for pair in self._case_status[curr_case]:
            if other_event not in pair:
                return pair
        return None

    #
    # def search_pair(self, curr_case, target_event, with_existing_pairs = False):
    #     other_event = self.set_other_event(target_event)
    #
    #     for pair in self._case_status[curr_case]:
    #         if target_event in pair:
    #             if with_existing_pairs and other_event not in pair:
    #             return pair
    #
    #
    #     return None

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

    def clean_struct(self, assignments, struct):
        # Remove keys where values are '', None, {}, []
        for key, value in list(struct.items()):
            if value in (u'', None, {}, []):
                del struct[key]

        # Recursively remove unused events
        last_key = list(assignments.keys())[-1]
        for key, value in list(struct.items()):
            if isinstance(value, dict):
                struct[key] = self.clean_struct(assignments, value)
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_dict = self.clean_struct(assignments, item)
                        if new_dict:
                            new_list.append(new_dict)
                    elif isinstance(item, int) and item < last_key:
                        new_list.append(item)
                struct[key] = new_list
            elif isinstance(value, int) and value >= last_key:
                del struct[key]

        return struct

    def clean_buf2(self, assignments):
        buf = self._buf.copy()
        curr_id = list(assignments)[-1]
        # {'e2': [8]}
        for key, values in buf.items():
            self._buf[key] = [x for x in values if x < curr_id]
            # if it's empty after reassignment, only elmts >= curr_event were there
            if not self._buf[key]:
                del self._buf[key]
        # self._buf = self.clean_struct(assignments, self._buf)
        # self._buf =