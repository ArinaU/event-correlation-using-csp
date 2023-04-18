from constraint import *
from copy import deepcopy


class BaseEventConstraint(Constraint):
    def __init__(self, data, start_event, required_event, required_event2=None):
        self._data = data
        self._required_event = required_event
        self._required_event2 = required_event2
        self._start_event = start_event
        self._case_status = {}
        self._prev_assignments = {}
        self._curr_event = None


    def find_cases(self, events, domains):
        attr = self._required_event['attr']
        cases = []
        for event in events:
            if self._data[event][attr] == self._start_event['value']:
                cases.append(domains[event][0])

        return cases

    def has_future_solutions(self, domains, assignments, events, attr, val):
        curr_case = assignments[list(assignments)[-1]]
        for event in events:
            if event not in assignments:
                if self._data[event][attr] == val:
                    domain = domains[event]
                    if curr_case in domain:
                        return True


    def has_available_solutions(self, domains, assignments, case_status, target_event_type):
        # if not isinstance(events, list):
        #     events = [events]
        # existing cases yet without 'e2' or 'e'

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        other_event_type = 'e2' if target_event_type == 'e' else 'e'
        available_cases = []
        for case, pairs in case_status.items():
            for pair in pairs:
                if target_event_type not in pair and len(domains[pair[other_event_type]]) > 1:
                    available_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        event_domains = domains[curr_id]
        # event_domains[event_domains.index(curr_case):]
        if set(available_cases) & set(event_domains):
            return True

        return False


    def find_occurrences_of_target_event(self, events, assignments, target_type):
        curr_case = assignments[self._curr_event]
        pairs = []
        for pair in self._case_status[curr_case]:
            if target_type in pair and pair[target_type] < self._curr_event:
                pairs.append(pair)
        return pairs

    def find_single_target_event(self, curr_case, target_type, pairs=None):  # e
        if not pairs:
            pairs = self._case_status[curr_case]
        # get first available pair
        other_type = 'e2' if target_type == 'e' else 'e'
        for pair in pairs:
            if other_type not in pair and pair[target_type] < self._curr_event:
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
                    elif isinstance(item, int) and item in assignments and item != last_key:
                        new_list.append(item)
                struct[key] = new_list
                if not struct[key]:
                    del struct[key]
            elif isinstance(value, int) and (value not in assignments or value == last_key):
                del struct[key]

        return struct
