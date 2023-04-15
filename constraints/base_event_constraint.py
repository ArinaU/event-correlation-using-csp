from constraint import *
from copy import deepcopy


class BaseEventConstraint(Constraint):

    def has_available_solutions(self, domains, case_status, events, target_event_type):
        if not isinstance(events, list):
            events = [events]
        # cases yet without 'e2' or 'e'
        free_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if target_event_type not in pair:
                    free_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        for event in events:
            event_domains = domains[event]
            if set(free_cases) & set(domains):
                return True

        return False

    def find_pairs_with_target_event(self, curr_case, target_event):
        pairs = []
        for pair in self._case_status[curr_case]:
            if target_event in pair:
                pairs.append(pair)
        return pairs

    def find_single_target_event(self, curr_case, target_event, pairs=None):  # e
        if not pairs:
            pairs = self._case_status[curr_case]
        # get first available pair
        other_event = 'e2' if target_event == 'e' else 'e'
        for pair in pairs:
            if other_event not in pair:
                return pair
        return None

    def clean_struct(self, assignments, struct):
        # Remove values u'', None, {}, []
        for key, value in list(struct.items()):
            if value in (u'', None, {}, []):
                del struct[key]

        # Remove prev events
        last_key = list(assignments.keys())[-1]
        for key, value in list(struct.items()):
            if isinstance(value, dict):
                struct[key] = self.clean_struct(assignments, value)
                if not struct[key]:
                    del struct[key]
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
                if not struct[key]:
                    del struct[key]
            elif isinstance(value, int) and value >= last_key:
                del struct[key]

        return struct
