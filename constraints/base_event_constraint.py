from constraint import *
from copy import deepcopy


class BaseEventConstraint(Constraint):
    def __init__(self, data, start_event, required_event, required_event2=None):
        self._data = data
        self._start_event = start_event
        self._case_status = {}
        self._attr = required_event['attr']
        self._val = required_event['value']
        self._prev_assignments = []
        self._reserved_events = {key: [] for key in data.keys()}
        if required_event2:
            self._attr2 = required_event2['attr']
            self._val2 = required_event2['value']
    @property
    def prev_assignments(self):
        return self._prev_assignments

    @prev_assignments.setter
    def prev_assignments(self, value):
        self._prev_assignments = value

    @property
    def reserved_events(self):
        return self._reserved_events

    @reserved_events.setter
    def reserved_events(self, value):
        self._reserved_events = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

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

    def __call__(self, events, domains, assignments, forwardcheck=False):
        self.curr_event = list(assignments)[-1]
        self.curr_case = assignments[self.curr_event]
        self.case_status = self.clean_case_status(assignments, self.case_status)
        self.clean_reserved_events(assignments, events)
        if len(self.prev_assignments) == 0 or self.prev_assignments[-1] != list(assignments)[-1]:
            self.prev_assignments.append(list(assignments)[-1])

        return True

    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr, val = self.attr, self.val
        else:
            attr, val = self.attr2, self.val2

        if target_type == 'e2':
            target_attr, target_val = self.attr2, self.val2
        else:
            target_attr, target_val = self.attr, self.val

        # empty_cases = {}
        possible_cases = {}
        for case, status in self.case_status.items():
            if case in domains[curr_event]:
                if not status[event_type] and not status[target_type]:
                    continue
                # if not status[other_event_type]:
                #     empty_cases.setdefault(event_type, []).append(case)
                elif len(status[target_type]) > len(status[event_type]):
                    possible_cases.setdefault(event_type, []).append(case)

        # return empty_cases, possible_cases
        return possible_cases

    def forward_check_events(self, events, domains, assignments, event_type):
        curr_event = self.curr_event
        curr_case = self.curr_case
        if event_type == 'e':
            attr, val = self.attr, self.val
        else:
            attr, val = self.attr2, self.val2

        for event in events[curr_event:]:
            # if event not in assignments:
            if self.data[event][attr] == val:
                if not self.reserved_events[curr_event] or \
                        (curr_case >= self.reserved_events[curr_event][0] and
                         (self.reserved_events[curr_event][1] == event or self.prev_assignments[-1] == curr_event)) \
                        or (curr_case <= self.reserved_events[curr_event][0] and self.reserved_events[curr_event][
                    1] < event):
                    domain = domains[event]
                    if curr_case in domain:
                        if len(domain) > 1:
                            for case in domain[:]:
                                if case != curr_case:
                                    domain.hideValue(case)

                        self.reserved_events[curr_event] = [curr_case, event]
                        return True
        return False

    def forward_prune_events(self, events, domains, assignments, event_type, all_events=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr, val = self.attr, self.val
        else:
            attr, val = self.attr2, self.val2

        for event in events:
            if event not in assignments:
                if self.data[event][attr] == val:
                    domain = domains[event]
                    if curr_case in domain:
                        # if len(domain) > 1:
                        for case in domain[:]:
                            if case == curr_case:
                                domain.hideValue(case)
                        if not all_events:
                            return True
        return False


    def check_case_status(self, events, domains, assignments, event_type, target_type=None):
        other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e' and target_type:
            attr, val = self.attr2, self.val2
        else:
            attr, val = self.attr, self.val

        # empty_cases, possible_cases = self.check_possible_cases(events, domains, assignments, event_type)
        possible_cases = self.check_possible_cases(events, domains, assignments, event_type, target_type)

        # Cases with no 'e': ['Case2']
        # Cases with superfluous 'e2': ['Case1']

        # found_case = self.check_future_case_assignment(events, domains, assignments, curr_case,
        #                                                             event_type, target_type)
        # if found_case:
        #     return True

        if possible_cases:
            return False

        return True


    def find_events_in_list(self, event, case, target_type, check_order=False):
        events = []
        for e in self.case_status[case][target_type]:
            if check_order:
                if e <= event:
                    events.append(e)
            else:
                events.append(e)

        return events

    def find_events_in_pairs(self, event, case, target_type, check_order=False, with_pairs=False, case_events=None):
        other_type = 'e2' if target_type == 'e' else 'e'

        if case_events is None:
            case_events = self.case_status[case]

        events = []

        for event_pair in case_events:
            target_value = event_pair.get(target_type)

            if target_value is not None:
                if check_order:
                    if target_value <= event:
                        events.append(event_pair)
                else:
                    events.append(event_pair)

        if with_pairs:  # If with_pairs is True, return both pairs and single elements together
            return events
        else:  # If with_pairs is False, return only single elements
            return [event_pair for event_pair in events if other_type not in event_pair]

    # def find_events_in_pairs(self, event, case, target_type, check_order=False, pairs=False):
    #     other_type = 'e2' if target_type == 'e' else 'e'
    #     case_events = self.case_status[case]
    #     events = []
    #
    #     for event_pair in case_events:
    #         is_pair = other_type in event_pair
    #
    #         if is_pair == pairs:
    #             target_value = event_pair.get(target_type)
    #
    #             if target_value is not None:
    #                 if check_order:
    #                     if target_value < event:
    #                         events.append(event_pair)
    #                 else:
    #                     events.append(event_pair)
    #     return events


    def clean_reserved_events(self, assignments, events):
        curr_event = list(assignments.keys())[-1]
        # self._reserved_events = {key: [] for key in data.keys()}

        for event in events[curr_event+1:]:
            self.reserved_events[event] = []


    def clean_case_status(self, assignments, case_status):
        # Remove values u'', None, {}, []
        # for key, value in list(struct.items()):
        #     if value in (u'', None, {}, []):
        #         del struct[key]

        # Remove prev events
        last_key = list(assignments.keys())[-1]
        for key, value in list(case_status.items()):
            if isinstance(value, dict):
                case_status[key] = self.clean_case_status(assignments, value)
                # if not struct[key]:
                #     del struct[key]
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_dict = self.clean_case_status(assignments, item)
                        if new_dict:
                            new_list.append(new_dict)
                    elif isinstance(item, int) and item in assignments and item != last_key:
                        new_list.append(item)
                case_status[key] = new_list
                # if not struct[key]:
                #     del struct[key]
            elif isinstance(value, int) and (value not in assignments or value == last_key):
                del case_status[key]

        return case_status

    def get_all_cases(self, events, domains):
        cases = []
        for event in events:
            if self.data[event][self.attr] == self.start_event['value']:
                cases.append(domains[event][0])
        return cases
