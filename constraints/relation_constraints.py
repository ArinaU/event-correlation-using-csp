from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):
    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            if case in event_domains[event_domains.index(curr_case)+1:]:
                if not self.reject_conditions(curr_event, case, event_type):
                    available_cases.append(case)

        return available_cases

    def reject_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        # events = self.case_status[case].setdefault(event_type, [])
        # events2 = self.case_status[case].setdefault(event_type2, [])
        events = self.find_events_in_list(event, case, event_type)
        events2 = self.find_events_in_list(event, case, event_type2)
        return (events2 and events) or (events and not events2)

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_struct(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])
        self.case_status[curr_case].setdefault('e2', [])

        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        if self.data[curr_event][self.attr] == self.val:
            if self.reject_conditions(curr_event, curr_case, 'e'):
                if self.prev_assignments[curr_event] != curr_case \
                        and self.has_available_cases(domains, assignments, 'e'): # and self.backtracking_available(domains, assignments):
                    self.prev_assignments[curr_event] = curr_case
                    return False
            self.case_status[curr_case]['e'].append(curr_event)

        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.reject_conditions(curr_event, curr_case, 'e2'):
                if self.prev_assignments[curr_event] != curr_case \
                        and self.has_available_cases(domains, assignments, 'e2'): # and self.backtracking_available(domains, assignments):
                    self.prev_assignments[curr_event] = curr_case
                    return False

            self.case_status[curr_case]['e2'].append(curr_event)

        self.prev_assignments[curr_event] = None
        return True


# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):
    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            if case in event_domains[event_domains.index(curr_case)+1:]:
                if not self.reject_conditions(curr_event, case, event_type):
                    available_cases.append(case)

        return available_cases

    def reject_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        events = self.find_events_in_list(event, case, event_type, True)
        events2 = self.find_events_in_list(event, case, event_type2, True)
        if event_type == 'e':
            # return (events and not events2) or (events2 and not events)
            return events or events2

        return (events2 and events) or (events and not events2)


    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_struct(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])
        self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        # A,C,A,B,C
        # 1 1 2 2 2

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.find_events_in_list(curr_event, curr_case, 'e2', True):
                return False
            else:
                if self.reject_conditions(curr_event, curr_case, 'e'):
                    if self.prev_assignments[curr_event] != curr_case \
                        and self.has_available_cases(domains, assignments,
                                                     'e'):  # and self.backtracking_available(domains, assignments):
                        self.prev_assignments[curr_event] = curr_case
                        return False
            self.case_status[curr_case]['e'].append(curr_event)
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.reject_conditions(curr_event, curr_case, 'e2'):
                if self.prev_assignments[curr_event] != curr_case \
                        and self.has_available_cases(domains, assignments,
                                                     'e2'):  # and self.backtracking_available(domains, assignments):
                    self.prev_assignments[curr_event] = curr_case
                    return False

            self.case_status[curr_case]['e2'].append(curr_event)

        self.prev_assignments[curr_event] = None
        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            if case in event_domains[event_domains.index(curr_case)+1:]:
                if not self.reject_conditions(curr_event, case, event_type):
                    available_cases.append(case)

        return available_cases

    def reject_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        events = self.find_events_in_list(event, case, event_type, True)
        events2 = self.find_events_in_list(event, case, event_type2, True)
        if event_type == 'e':
            return events

        return not events2


    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_struct(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])
        self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,B
        # 1 2 1 2 1 2 3 1

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.reject_conditions(curr_event, curr_case, 'e'):
                if self.prev_assignments[curr_event] != curr_case \
                        and self.has_available_cases(domains, assignments, 'e'): # and self.backtracking_available(domains, assignments):
                    self.prev_assignments[curr_event] = curr_case
                    return False
            self.case_status[curr_case]['e'].append(curr_event)
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.reject_conditions(curr_event, curr_case, 'e2'):
                return False

            self.case_status[curr_case]['e2'].append(curr_event)

        self.prev_assignments[curr_event] = None

        # # if B
        # if self.data[curr_event][self.attr] == self.val:
        #     self.case_status[curr_case].append({'e': curr_event})
        # # if C
        # elif self.data[curr_event][self.attr2] == self.val2:
        #     target_event = self.find_single_event_type(assignments, 'e')
        #     if target_event:
        #         target_event['e2'] = curr_event
        #     else:
        #         return False
        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):

    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            if case in event_domains[event_domains.index(curr_case)+1:]:
                if not self.reject_conditions(curr_event, case, event_type):
                    available_cases.append(case)

        return available_cases

    def reject_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'

        single_events = self.find_event_in_pairs(event, case, event_type, True, False)
        pairs = self.find_event_in_pairs(event, case, event_type, True, True)
        single_events2 = self.find_event_in_pairs(event, case, event_type2, True, False)

        if event_type == 'e2':
            return pairs or len(self.case_status[case]) == 0
        else:
            return single_events2 and not single_events

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

        if self.check_backtracking(domains, assignments, event_type) \
                and self.prev_assignments[curr_event] != curr_case:
            self.prev_assignments[curr_event] = curr_case
            return True

        return False


    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_struct(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # self.case_status[curr_case].setdefault('e', [])
        # self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6
        # A,B,A,B,C,C
        # 1 1 2 2 1 2

        # Absence(G)
        # 1 2 3 4 5 6 7 8
        # A,A,G,A,F,E,G,G
        # 1 2 1 3 2 3 3 2
        # 1 2 1 3 1 2 2 3

        # ChainResp(B, C) Absence(D, B)
        # 1 2 3 4 5 6 7 8 9 10
        # A,B,A,D,C,B,A,D,C,C
        # 1 1 2 2 1 2 3 1 1 2
        # 1 1 2 2 1 2 3 1 2 1

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.reject_conditions(curr_event, curr_case, 'e'):
                return False

            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            target_event = self.find_event_in_pairs(curr_event, curr_case, 'e', True)
            if target_event:
                target_event[0]['e2'] = curr_event
            else:
                if self.check_rejection(domains, assignments, 'e2'):
                    return False
        else:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]
            if case_events:
                prev_event = case_events[-1]
                # if prev event was B
                if self.data[prev_event][self.attr] == self.val:
                    return False

        self.prev_assignments[curr_event] = None

        return True



class ChainPrecedence(BaseEventConstraint):

    # each time B occurs, A immediately beforehand
    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        self._curr_event = list(assignments)[-1]
        curr_event = self._curr_event
        curr_case = assignments[curr_event]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        if data[curr_event][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_event})
        # if C
        elif data[curr_event][required_attr2] == required_value2:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was not B
                if not data[prev_id][required_attr] == required_value:
                    return False

            case_status[curr_case].append({'e2': curr_event})

        return True



# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):

    def forwardCheck(self, events, domains, assignments, _unassigned=Unassigned):
        data = self._data
        curr_case = assignments[self._curr_event]
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        for event in events:
            # if 2nd element next
            if data[event][required_attr2] == required_value2:
                domain = domains[event]
                if curr_case in domain:
                    for value in domain[:]:
                        if value != curr_case:
                            domain.hideValue(value)
                    return True
            # if 1st before 2nd
            elif data[event][required_attr] == required_value:
                domain = domains[event]
                if curr_case in domain:
                    for value in domain[:]:
                        if value == curr_case:
                            domain.hideValue(value)
        else:
            return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        self._curr_event = list(assignments)[-1]
        curr_event = self._curr_event
        curr_case = assignments[curr_event]
        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,B,D,C,A,B,C
        # 1 2 1 2 1 1 3 3 2
        # 1 2 1 2 1 1 3 3 2

        # 1 2 3 4 5 6 7 8 9 10  11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
        # A,A,C,C,B,B,D,D,F, E, G, G, H, C, B, I, D, C, B, E, D, G, F, H, G, I, C, B, J, L
        # 1,2,1,2,1,2,1,2,1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1
        #     1 2 3 4 1 2

        # (B,D)
        # (C,D)

        # if B
        if data[curr_event][required_attr] == required_value:
            not_target_event = self.find_single_event_type(curr_case, 'e')
            if not_target_event:
                return False
            else:
                if not self.forwardCheck(events[curr_event:], domains, assignments):
                    return True
            case_status[curr_case].append({'e': curr_event})

        # if C
        elif data[curr_event][required_attr2] == required_value2:
            target_event = self.find_single_event_type(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_event
            else:
                case_status[curr_case].append({'e2': curr_event})


        # # if B
        # if data[curr_id][required_attr] == required_value:
        #     not_target_event = self.find_single_target_event(curr_case, 'e')
        #     if not_target_event:
        #         return False
        #     case_status[curr_case].append({'e': curr_id})
        # # if C
        # elif data[curr_id][required_attr2] == required_value2:
        #     target_event = self.find_single_target_event(curr_case, 'e')
        #     if target_event:
        #         target_event['e2'] = curr_id
        #     else:
        #         if self.has_available_solutions(domains, assignments, case_status, 'e2'):
        #             return False
        #         else:
        #             case_status[curr_case].append({'e2': curr_id})

        return True



# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
# A no(B) B
class AlternatePrecedence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        self._curr_event = list(assignments)[-1]
        curr_event = self._curr_event
        curr_case = assignments[curr_event]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if C, preceded by B and no B in between
        # (B, C) B no(C) C
        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2

        # if B
        if data[curr_event][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_event})
        # if C
        elif data[curr_event][required_attr2] == required_value2:
            if case_status[curr_case]:
                last_pair = case_status[curr_case][-1]
                if 'e2' in last_pair:
                    return False
                else:
                    last_pair['e2'] = curr_event
            else:
                return False

        return True

