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

    # def has_available_cases(self, domains, assignments, event_type):
    #     curr_event = list(assignments)[-1]
    #     curr_case = assignments[curr_event]
    #     event_domains = domains[curr_event]
    #     other_event_type = 'e2' if event_type == 'e' else 'e'
    #
    #     available_cases = []
    #
    #     for case, events in self.case_status.items():
    #         if case in event_domains:
    #             events = self.find_events_in_list(curr_event, case, event_type)  # B
    #             other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C
    #
    #             if event_type == 'e':
    #                 # if B, select cases where C exist
    #                 if other_events:
    #                     available_cases.append(case)
    #             else:
    #                 # # if C, select cases where B exist and not C yet
    #                 if other_events and not events:
    #                     available_cases.append(case)
    #
    #     return available_cases

    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case and case in domains[curr_event]:
                # if status[event_type] and not status[other_event_type]:
                #     empty_cases.setdefault(event_type, []).append(case)
                if event_type == 'e':
                    if (status[event_type] and len(status[target_type]) > 1) \
                            or (not status[event_type] and status[target_type]):
                        possible_cases.setdefault(event_type, []).append(case)
                if event_type == 'e2':
                    if status[target_type] and not status[event_type]:
                        possible_cases.setdefault(event_type, []).append(case)

        return possible_cases

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}

        # 2
        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        # 1 2 3 4 5 6
        # A,B,A,C,C,B
        # 1 1 2 1 2 2

        #                   1                   2                   3
        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
        # A,C,A,B,C,A,B,D,C,B,D,F,D,F,G,E,G,H,G,H,I,H,I,J,I,L,J,C,B,K,D,L,E,G,H,I,J,K,L

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # B
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case]['e'].append(curr_event)

            if not self.case_status[curr_case]['e2']:
                if not self.forward_check_events(events, domains, assignments, 'e2'):
                    if self.check_possible_cases(events, domains, assignments, 'e', 'e2'):
                        return False
                # if not self.forward_check_events(events, domains, assignments):
                #     if not self.check_case_status(events, domains, assignments, 'e', 'e2'):
                #         return False
        # C
        elif self.data[curr_event][self.attr2] == self.val2:
            self.case_status[curr_case]['e2'].append(curr_event)

        return True


# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):

    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case and case in domains[curr_event]:

                events = self.find_events_in_list(curr_event, case, 'e2', True)
                target_events = self.find_events_in_list(curr_event, case, 'e', True)

                if event_type == 'e2':
                    if target_events and not events:
                        possible_cases.setdefault(event_type, []).append(case)

        return possible_cases

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,C
        # 1 2 1 1 1 2 3 3

        # 1 2 3 4 5
        # A,C,A,B,C
        # 1 1 2 2 2

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if self.find_events_in_list(curr_event, curr_case, 'e2', True):
                return False

            self.case_status[curr_case]['e'].append(curr_event)

            # if not self.forward_check_events(events, domains, assignments):
            #     if not self.check_case_status(events, domains, assignments, 'e', 'e2'):
            #         return False
            # if not self.forward_check_events(events, domains, assignments):
            #     if not self.case_status[curr_case]['e2']:
            #         return False
            self.forward_check_events(events, domains, assignments, 'e2')

        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.case_status[curr_case]['e'] and not self.case_status[curr_case]['e2']:
                self.case_status[curr_case]['e2'].append(curr_event)
                return True
            # else:
            #     missing_cases = [case for case, events in self.case_status.items() if events['e'] and not events['e2']]
            #     if missing_cases and not self.check_case_status(events, domains, assignments, 'e2', 'e'):
            #         return False

            self.case_status[curr_case]['e2'].append(curr_event)

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,B
        # 1 2 1 2 1 2 3 1


        # if B
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case]['e'].append(curr_event)

        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.find_events_in_list(curr_event, curr_case, 'e', True):
                self.case_status[curr_case]['e2'].append(curr_event)
            else:
                return False

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):

    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case:
                if case in domains[curr_event]:

                    # events = self.find_events_in_pairs(curr_event, case, 'e2', True)
                    target_events = self.find_events_in_pairs(curr_event, case, 'e', True)

                    if event_type == 'e2':
                        if target_events: # and not events:
                            # if self.check_order(assignments, target_events[-1]['e'], 'e', True):
                            possible_cases.setdefault(event_type, []).append(case)

        return possible_cases

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e < curr_event])

        # 1 2 3 4 5 6
        # A,B,A,B,C,C
        # 1 1 2 2 1 2

        # 1 2 3 4 5 6 7 8
        # A,H,A,D,E,D,G,H
        # 1 1 2 2 2 1 2 2

        # Absence(G)
        # 1 2 3 4 5 6 7 8
        # A,A,G,A,F,E,G,G
        # 1 2 1 3 2 3 3 2
        # 1 2 1 3 1 2 2 3

        # ChainResp(B, C) Absence(D, B)
        # 1 2 3 4 5 6 7 8 9 10
        # A,B,A,D,C,B,A,D,C,C
        # 1 1 2 2 1 2 3 1 1 2

        # if B
        if self.data[curr_event][self.attr] == self.val:
            event = self.find_events_in_pairs(curr_event, curr_case, 'e', True)
            # if event and event[-1]['e'] == case_events[-1]:
            if event:
                return False

            self.case_status[curr_case].append({'e': curr_event})
            self.forward_check_events(events, domains, assignments, 'e2')
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            event = self.find_events_in_pairs(curr_event, curr_case, 'e', True)
            if event:
                prev_event = event[-1]
                if self.check_order(assignments, prev_event['e'], 'e2', True):
                    prev_event['e2'] = curr_event
                    return True

                return False
            else:
                self.case_status[curr_case].append({'e2': curr_event})

                # if not self.check_case_status(events, domains, assignments, 'e2', 'e'):
                #     return False
        else:
            if case_events:
                prev_event = case_events[-1]
                # if prev event was B
                if self.data[prev_event][self.attr] == self.val:
                    return False

        return True


# each time B occurs, A immediately beforehand
class ChainPrecedence(BaseEventConstraint):
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
        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e < curr_event])

        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            events = self.find_events_in_pairs(curr_event, curr_case, 'e', True, False)
            if events and case_events[-1] == events[-1]['e']:
                events[-1]['e2'] = curr_event
                return True

            return False

        return True


# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):

    # def check_future_case_assignment(self, events, domains, assignments, curr_case, event_type, target_type=None):
    #     target_attr, target_val = self.attr2, self.val2
    #
    #     # for case in empty_cases[event_type]:
    #     case_occurs = False
    #     for future_event in events:
    #         if future_event not in assignments:
    #             if self.data[future_event][target_attr] == target_val:
    #                 if curr_case in domains[future_event]:
    #                     case_occurs = True
    #                     break
    #
    #     return case_occurs
    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case and case in domains[curr_event]:

                events = self.find_events_in_pairs(curr_event, case, 'e2', True)
                target_events = self.find_events_in_pairs(curr_event, case, 'e', True)

                if event_type == 'e2':
                    if target_events and not events:
                        possible_cases.setdefault(event_type, []).append(case)

        return possible_cases




    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,D,C,A,B,C,B
        # 1 2 1 1 1 3 2 2 3

        # A,A,B,B,C,C
        # 1 2 1 2 1 2

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,B,D,C,A,B,C
        # 1 2 1 2 1 1 3 3 2

        # B noB C

        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
        # A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I

            # 1 2 3 4 5 6 7 8 9
            # A,A,C,C,B,B,D,D,C
            # 1 2 1 2 1 1 1 2 1

            # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
            # A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I,D,C,B,E,D,G,F,H,G,I,C,B,J,L

        # if B
        if self.data[curr_event][self.attr] == self.val:
            another_event = self.find_events_in_pairs(curr_event, curr_case, 'e', True)
            if another_event:
                return False
            else:
                self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            event = self.find_events_in_pairs(curr_event, curr_case, 'e', True)
            if event and self.check_order(assignments, event[-1]['e'], 'e'):
                event[-1]['e2'] = curr_event
            else:
                self.case_status[curr_case].append({'e2': curr_event})

                # possible check last event in check_possible_cases
                if not self.check_case_status(events, domains, assignments, 'e2', 'e'):
                    return False

        return True


# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
# A no(B) B J no(I) I
class AlternatePrecedence(BaseEventConstraint):

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
        # G no(H) H

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2
        # 31
        # if B
        if self.data[curr_event][self.attr] == self.val:
            # here add rejection checking or not
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            pairs = self.find_events_in_pairs(curr_event, curr_case, 'e', True, True)

            if pairs:
                last_pair = pairs[-1]
                if not last_pair.get('e2'):
                    if self.check_order(assignments, last_pair['e'], 'e2'):
                        last_pair['e2'] = curr_event
                        return True

            return False

        return True
