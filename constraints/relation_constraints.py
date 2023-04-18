
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):

    def forwardCheckEvents(self, events, domains, assignments, attr, val):
        data = self._data
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
        # required_attr2 = self._required_event2['attr']
        # required_value2 = self._required_event2['value']

        for event in events:
            if event not in assignments:
                if data[event][attr] == val:
                    domain = domains[event]
                    if curr_case in domain and len(domain) > 1:
                        for value in domain[:]:
                            if value != curr_case:
                                domain.hideValue(value)
                    return True
        else:
            return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        prev_assignments = self._prev_assignments
        case_status = self._case_status
        attr = self._required_event['attr']
        val = self._required_event['value']
        attr2 = self._required_event2['attr']
        val2 = self._required_event2['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # if B
        if data[curr_id][attr] == val:
            # if no Cs yet
            if not self.find_occurrences_of_target_event(events, assignments, 'e2'):
                # if solutions among existing cases and no future ones
                if self.has_available_solutions(domains, assignments, case_status, 'e') \
                        and prev_assignments[curr_id] != curr_case:
                    prev_assignments[curr_id] = curr_case
                    return False

                if forwardcheck:
                    self.forwardCheckEvents(events[curr_id:], domains, assignments, attr2, val2)

            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][attr2] == val2:
            # if not self.find_occurrences_of_target_event(events, assignments, 'e'):
            #     if forwardcheck:
            #         self.forwardCheckEvents(events[curr_id:], domains, assignments, attr, val)

            case_status[curr_case].append({'e2': curr_id})

        prev_assignments[curr_id] = None
        return True



# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):

    def forwardCheck(self, events, domains, assignments, _unassigned=Unassigned):
        data = self._data
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        for event in events:
            # if another element
            if event not in assignments:
                if data[event][required_attr2] == required_value2:
                    domain = domains[event]
                    if curr_case in domain:
                        for value in domain[:]:
                            if value != curr_case:
                                domain.hideValue(value)
                        return True
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
        curr_case = assignments[self._curr_event]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        # A C A B C

        # if B
        if data[self._curr_event][required_attr] == required_value:
            # if C was before
            if self.find_occurrences_of_target_event(events, assignments, 'e2'):
                return False
            else:
                if forwardcheck:
                    self.forwardCheck(events[self._curr_event:], domains, assignments)

                case_status[curr_case].append({'e': self._curr_event})

        # if C
        elif data[self._curr_event][required_attr2] == required_value2:
            case_status[curr_case].append({'e2': self._curr_event})

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        self._curr_event = list(assignments)[-1]
        curr_case = assignments[self._curr_event]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if B
        if data[self._curr_event][required_attr] == required_value:
            case_status[curr_case].append({'e': self._curr_event})
        # if C
        elif data[self._curr_event][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = self._curr_event
            else:
                return False

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):

    def forwardCheck(self, events, domains, assignments, _unassigned=Unassigned):
        data = self._data
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
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
            # if not
            else:
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

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8
        # A,A,G,A,F,E,G,G
        # 1 2 1 3 2 3 2 3

        # ChainResp(B, C) Absence(D, B)
        # 1 2 3 4 5 6 7 8 9 10
        # A,B,A,D,C,B,A,D,C,C
        # 1 1 2 2 1 2 3 3 2 1

        # if B
        if data[curr_id][required_attr] == required_value:
            if not self.forwardCheck(events[curr_id:], domains, assignments):
                return True
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
        else:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_id]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was not B
                if data[prev_id][required_attr] == required_value:
                    return False


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

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        if data[curr_id][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_id]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was not B
                if not data[prev_id][required_attr] == required_value:
                    return False

            case_status[curr_case].append({'e2': curr_id})

        return True



# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):

    def forwardCheck(self, events, domains, assignments, _unassigned=Unassigned):
        data = self._data
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
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

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
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
        if data[curr_id][required_attr] == required_value:
            not_target_event = self.find_single_target_event(curr_case, 'e')
            if not_target_event:
                return False
            else:
                if not self.forwardCheck(events[curr_id:], domains, assignments):
                    return True
            case_status[curr_case].append({'e': curr_id})

        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                case_status[curr_case].append({'e2': curr_id})


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

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if C, preceded by B and no B in between
        # (B, C) B no(C) C
        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2

        # if B
        if data[curr_id][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            if case_status[curr_case]:
                last_pair = case_status[curr_case][-1]
                if 'e2' in last_pair:
                    return False
                else:
                    last_pair['e2'] = curr_id
            else:
                return False

        return True

