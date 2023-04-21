from constraint import *
from copy import deepcopy


class BaseEventConstraint(Constraint):
    def __init__(self, data, start_event, required_event, required_event2=None):
        self._data = data
        self._start_event = start_event
        self._case_status = {}
        self._prev_assignments = {event: None for event in self._data.keys()}
        self._attr = required_event['attr']
        self._val = required_event['value']
        if required_event2:
            self._attr2 = required_event2['attr']
            self._val2 = required_event2['value']


    # @property
    # def curr_case(self):
    #     return self._curr_case
    #
    # @curr_case.setter
    # def curr_case(self, value):
    #     self._curr_case = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    # @property
    # def curr_event(self):
    #     return self._curr_event
    #
    # @curr_event.setter
    # def curr_event(self, value):
    #     self._curr_event = value

    @property
    def case_status(self):
        return self._case_status

    @case_status.setter
    def case_status(self, value):
        self._case_status = value

    @property
    def start_event(self):
        return self._start_event

    @property
    def prev_assignments(self):
        return self._prev_assignments

    @prev_assignments.setter
    def prev_assignments(self, value):
        self._prev_assignments = value

    @property
    def attr(self):
        return self._attr

    @property
    def val(self):
        return self._val

    @property
    def attr2(self):
        return self._attr2

    @property
    def val2(self):
        return self._val2

    def check_backtracking(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr = self.attr
            val = self.val
        else:
            attr = self.attr2
            val = self.val2

        if len(domains) > curr_event:
            for event in domains:
                if event not in assignments and not self.prev_assignments[event]:
                    if self.data[event][attr] == val:
                        if curr_case in domains[event]:
                            return False

        #if len(domains[curr_event]) > 1:
        for event in reversed(domains):
            if event < curr_event:
                if domains[event].index(assignments[event]) < len(domains[event])-1:
                    return True
        return False


    def get_all_cases(self, events, domains):
        cases = []
        for event in events:
            if self.data[event][self.attr] == self.start_event['value']:
                cases.append(domains[event][0])

        return cases


    def has_available_solutions(self, domains, assignments, target_event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        other_event_type = 'e2' if target_event_type == 'e' else 'e'
        available_cases = []
        for case, pairs in self.case_status.items():
            for pair in pairs:
                if target_event_type not in pair and len(domains[pair[other_event_type]]) > 1:
                    available_cases.append(case)
                    break

        # check if there are events that can be assigned to free cases
        event_domains = domains[curr_event]
        # event_domains[event_domains.index(curr_case):]
        if set(available_cases) & set(event_domains):
            return True

        return False

    def find_events_in_list(self, event, case, target_type, check_order=False):
        events = []
        for e in self.case_status[case][target_type]:
            if check_order:
                if e < event:
                    events.append(e)
            else:
                events.append(e)

        return events

    def find_event_in_pairs(self, event, case, target_type, check_order=False, pairs=False):
        other_type = 'e2' if target_type == 'e' else 'e'
        case_events = self.case_status[case]
        events = []

        for event_pair in case_events:
            is_pair = other_type in event_pair

            if is_pair == pairs:
                target_value = event_pair.get(target_type)

                if target_value is not None:
                    if check_order:
                        if target_value < event:
                            events.append(event_pair)
                    else:
                        events.append(event_pair)

        return events

    def find_all_occurrences_of_event(self, assignments, target_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        pairs = []
        for pair in self.case_status[curr_case]:
            if target_type in pair and pair[target_type] < curr_event:
                pairs.append(pair)

        return pairs

    def clean_struct(self, assignments, struct):
        # Remove values u'', None, {}, []
        # for key, value in list(struct.items()):
        #     if value in (u'', None, {}, []):
        #         del struct[key]

        # Remove prev events
        last_key = list(assignments.keys())[-1]
        for key, value in list(struct.items()):
            if isinstance(value, dict):
                struct[key] = self.clean_struct(assignments, value)
                # if not struct[key]:
                #     del struct[key]
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
                # if not struct[key]:
                #     del struct[key]
            elif isinstance(value, int) and (value not in assignments or value == last_key):
                del struct[key]

        return struct
