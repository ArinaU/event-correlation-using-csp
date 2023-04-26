from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):

    # def check_conditions(self, event, case, event_type):
    #     event_type2 = 'e2' if event_type == 'e' else 'e'
    #     events = self.find_events_in_list(event, case, event_type)
    #     events2 = self.find_events_in_list(event, case, event_type2)
    #     return (events2 and events) or (events and not events2)

    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]
        other_event_type = 'e2' if event_type == 'e' else 'e'

        available_cases = []

        for case, events in self.case_status.items():
            if case in event_domains:
                events = self.find_events_in_list(curr_event, case, event_type)  # B
                other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C

                if event_type == 'e':
                    # if B, select cases where C exist
                    if other_events:
                        available_cases.append(case)
                else:
                    # # if C, select cases where B exist and not C yet
                    if other_events and not events:
                        available_cases.append(case)

        return available_cases



    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}


        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # 1 1 1 2 3 2 2 1 3

        # B
        if self.data[curr_event][self.attr] == self.val:
            if not self.case_status[curr_case]['e2']:
                if self.check_rejection(domains, assignments, 'e'):
                    return False

            self.case_status[curr_case]['e'].append(curr_event)
            if not self.check_case_status(events, domains, assignments, 'e'):
                return False
        # C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.check_rejection(domains, assignments, 'e2'):
                return False
        # if self.data[curr_event][self.attr] == self.val:
        #     if self.check_conditions(curr_event, curr_case, 'e'):
        #         if self.check_rejection(domains, assignments, 'e'):
        #             return False
        #     self.case_status[curr_case]['e'].append(curr_event)
        #
        # # if C
        # elif self.data[curr_event][self.attr2] == self.val2:
        #     if self.check_conditions(curr_event, curr_case, 'e2'):
        #         if self.check_rejection(domains, assignments, 'e2'):
        #             return False
        #
        #     self.case_status[curr_case]['e2'].append(curr_event)
            self.case_status[curr_case]['e2'].append(curr_event)
            if not self.check_case_status(events, domains, assignments, 'e2'):
                return False

        self.prev_assignments[curr_event] = None
        return True


# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):

    def check_conditions(self, event, case, event_type):
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

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])
        self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        # A,C,A,B,C
        # 1 1 2 2 2

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.find_events_in_list(curr_event, curr_case, 'e2', True):
                return False
            else:
                if self.check_conditions(curr_event, curr_case, 'e'):
                    if self.check_rejection(domains, assignments, 'e'):
                        return False
            self.case_status[curr_case]['e'].append(curr_event)
            if not self.check_case_status(events, domains, assignments, 'e'):
                return False
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.check_conditions(curr_event, curr_case, 'e2'):
                if self.check_rejection(domains, assignments, 'e2'):
                    return False

            self.case_status[curr_case]['e2'].append(curr_event)
            if not self.check_case_status(events, domains, assignments, 'e2'):
                return False

        self.prev_assignments[curr_event] = None
        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

    def check_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        events = self.find_events_in_list(event, case, event_type, True)
        events2 = self.find_events_in_list(event, case, event_type2, True)
        if event_type == 'e':
            return events

        return not events2

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])
        self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,B
        # 1 2 1 2 1 2 3 1

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.check_conditions(curr_event, curr_case, 'e'):
                if self.check_rejection(domains, assignments, 'e'):
                    return False
            self.case_status[curr_case]['e'].append(curr_event)
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.check_conditions(curr_event, curr_case, 'e2'):
                return False

            self.case_status[curr_case]['e2'].append(curr_event)

        self.prev_assignments[curr_event] = None

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):

    def check_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'

        single_events = self.find_events_in_pairs(event, case, event_type, True, False)
        pairs = self.find_events_in_pairs(event, case, event_type, True, True)
        single_events2 = self.find_events_in_pairs(event, case, event_type2, True, False)

        if event_type == 'e2':
            return pairs or len(self.case_status[case]) == 0
        else:
            return single_events

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]

        # self.case_status[curr_case].setdefault('e', [])
        # self.case_status[curr_case].setdefault('e2', [])

        # 1 2 3 4 5 6
        # A,B,A,B,C,C
        # 1 1 2 2 1 2

        # ChainResp(B, C) Absence(D, B)
        # 1 2 3 4 5 6 7 8 9 10
        # A,B,A,D,C,B,A,D,C,C
        # 1 1 2 2 1 2 3 1 1 2
        # 1 1 2 2 1 2 3 1 2 1

        # Absence(G)
        # 1 2 3 4 5 6 7 8
        # A,A,G,A,F,E,G,G
        # 1 2 1 3 2 3 3 2
        # 1 2 1 3 1 2 2 3

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.check_conditions(curr_event, curr_case, 'e'):
                return False
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            event = self.find_events_in_pairs(curr_event, curr_case, 'e', True)
            if event and event[0]['e'] == case_events[-1]:
                event[0]['e2'] = curr_event
            else:
                if self.check_rejection(domains, assignments, 'e2'):
                    return False
        else:
            # case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]
            if case_events:
                prev_event = case_events[-1]
                # if prev event was B
                if self.data[prev_event][self.attr] == self.val:
                    return False

        return True



class ChainPrecedence(BaseEventConstraint):

    def check_conditions(self, event, case, event_type):
        single_events = self.find_events_in_pairs(event, case, event_type, True, False)
        if event_type == 'e':
            return single_events


    # each time B occurs, A immediately beforehand
    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # Absence(D, B)
        # 1 2 3 4 5 6 7 8
        # A,B,A,D,B,C,D,C
        # 1 1 2 2 2 1 1 2

        # A,A,B,B,C,C
        # 1 2 1 2 1 2

        # A no(B) B

        if self.data[curr_event][self.attr] == self.val:
            if self.check_rejection(domains, assignments, 'e'):
                return False

            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            single_events = self.find_events_in_pairs(curr_event, curr_case, 'e', True, False)
            if not single_events:
                return False
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]
            if not case_events[-1] == single_events[-1]['e']:
                return False
            single_events[-1]['e2'] = curr_event

        return True


# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):
    def check_conditions(self, event, case, event_type):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        events = self.find_events_in_pairs(event, case, event_type2, True, False)
        return not events

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,B,D,C,A,B,C
        # 1 2 1  1 1 3 3 2
        # 1 2 1 2 1 1 3 3 2

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,D,C,A,B,C,B
        # 1 2 1 1 1 3 2 2 3

        # A,A,B,B,C,C
        # 1 2 1 2 1 2

        # B noB C

        # if B
        if self.data[curr_event][self.attr] == self.val:
            another_event = self.find_events_in_pairs(curr_event, curr_case, 'e', True, False)
            if another_event:
                return False
            else:
                self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            target_event = self.find_events_in_pairs(curr_event, curr_case, 'e', True, False)
            if target_event:
                target_event[0]['e2'] = curr_event
            else:
                if self.check_rejection(domains, assignments, 'e2'):
                    return False
                self.case_status[curr_case].append({'e2': curr_event})

        self.prev_assignments[curr_event] = None
        return True


# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
# A no(B) B J no(I) I
class AlternatePrecedence(BaseEventConstraint):

    def check_conditions(self, event, case, event_type):
        single_events = self.find_events_in_pairs(event, case, event_type, True, False)
        return single_events

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # if C, preceded by B and no B in between
        # (B, C) B no(C) C
        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2

        # 1 2 3 4 5 6 7
        # A,A,B,D,B,C,C
        # 1 2 1 1 2 1 2

        # B no(C) C

        # if B
        if self.data[curr_event][self.attr] == self.val:
            # here add rejection checking or not
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if not self.case_status[curr_case]:
                return False
            last_pair = self.case_status[curr_case][-1]
            if 'e2' in last_pair:
                return False
            else:
                last_pair['e2'] = curr_event

        # self.prev_assignments[curr_event] = None

        return True
