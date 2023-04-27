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


    def check_possible_cases(self, events, domains, assignments, event_type, target_type):
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

    def check_future_case_assignment(self, events, domains, assignments, curr_case, event_type, target_type):
        if event_type == 'e':
            attr, val = self.attr, self.val
        else:
            attr, val = self.attr2, self.val2

        if target_type == 'e2':
            target_attr, target_val = self.attr2, self.val2
        else:
            target_attr, target_val = self.attr, self.val

        # for case in empty_cases[event_type]:
        case_occurs = False
        for future_event in events:
            if future_event not in assignments:
                if self.data[future_event][target_attr] == target_val:
                    if curr_case in domains[future_event]:
                        case_occurs = True
                        break

        return case_occurs


    def check_case_status(self, events, domains, assignments, event_type, target_type):
        other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr, val = self.attr2, self.val2
        else:
            attr, val = self.attr, self.val

        # empty_cases, possible_cases = self.check_possible_cases(events, domains, assignments, event_type)
        possible_cases = self.check_possible_cases(events, domains, assignments, event_type, target_type)

        # Cases with no 'e': ['Case2']
        # Cases with superfluous 'e2': ['Case1']

        found_case = self.check_future_case_assignment(events, domains, assignments, curr_case,
                                                                    event_type, target_type)
        if found_case:
            return True

        if possible_cases:
            return False

        return True


    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            if case in event_domains:
                if not self.reject_conditions(curr_event, case, event_type):
                    available_cases.append(case)

        return available_cases

    def reject_conditions(self, curr_event, case, event_type):
        pass

    def check_rejection(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]
        cases = self.has_available_cases(domains, assignments, event_type)

        if not cases:
            return False

        for case in cases:
            if event_domains.index(case) > event_domains.index(curr_case):
                if self.prev_assignments[curr_event] != curr_case:
                    self.prev_assignments[curr_event] = curr_case
                    return True

        # if self.check_backtracking(domains, assignments, event_type) \
        #         and self.prev_assignments[curr_event] != curr_case:
        #     self.prev_assignments[curr_event] = curr_case
        #     return True

        return False

    def check_backtracking(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr = self.attr2
            val = self.val2
        else:
            attr = self.attr
            val = self.val

        if len(domains) > curr_event:
            for event in domains:
                if event not in assignments:
                    if self.data[event][attr] == val:
                        if curr_case in domains[event]:
                            return False

        #if len(domains[curr_event]) > 1:
        for event in reversed(domains):
            if event < curr_event:
                if domains[event].index(assignments[event]) < len(domains[event])-1:
                    return True
        return False

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
                    if target_value < event:
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
