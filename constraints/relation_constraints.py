from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):

    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case and case in domains[curr_event]:
                # if status[event_type] and not status[other_event_type]:
                #   empty_cases.setdefault(event_type, []).append(case)
                if event_type == 'e':
                    if (status[event_type] and len(status[target_type]) > 1) \
                            or (not status[event_type] and status[target_type]):
                        possible_cases.setdefault(event_type, []).append(case)
                if event_type == 'e2':
                    if status[target_type] and not status[event_type]:
                        possible_cases.setdefault(event_type, []).append(case)

        return possible_cases

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        if not self.case_status.get(self.curr_case, None):
            self.case_status[self.curr_case] = {'e': [], 'e2': []}
        # 2
        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        #                   1                   2                   3
        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
        # A,C,A,B,C,A,B,D,C,B,D,F,D,F,G,E,G,H,G,H,I,H,I,J,I,L,J,C,B,K,D,L,E,G,H,I,J,K,L

        # 1 2 3 4 5 6
        # A,B,A,C,C,B
        # 1 1 2 1 2 2

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,B,C,C
        # 1 1 1 2 3 2 3 2 3

        # B
        if self.data[curr_event][self.attr] == self.val:
            if not self.case_status[curr_case]['e2']:
                if not self.forward_check_events(events, domains, assignments, 'e2'):
                    if self.check_possible_cases(events, domains, assignments, 'e', 'e2'):
                        return False

            self.case_status[curr_case]['e'].append(curr_event)
            # 5: [Case1, 7]
        # C
        elif self.data[curr_event][self.attr2] == self.val2:
            self.case_status[curr_case]['e2'].append(curr_event)

        return True


# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        if not self.case_status.get(self.curr_case, None):
            self.case_status[self.curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,C
        # 1 2 1 1 1 2 3 3

        # 1 2 3 4 5
        # A,C,A,B,C
        # 1 1 2 2 2

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        # if B
        if self.data[self.curr_event][self.attr] == self.val:
            if self.find_events_in_list(curr_event, curr_case, 'e2', True):
                return False

            self.forward_check_events(events, domains, assignments, 'e2')
            self.case_status[curr_case]['e'].append(curr_event)

        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            self.case_status[curr_case]['e2'].append(curr_event)

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        if not self.case_status.get(self.curr_case, None):
            self.case_status[self.curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8
        # A,A,B,B,C,C,A,B
        # 1 2 1 2 1 2 3 1


        # if B
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case]['e'].append(curr_event)
            # self.forward_check_events(events, domains, assignments, 'e2')

        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if self.find_events_in_list(curr_event, curr_case, 'e', True):
                self.case_status[curr_case]['e2'].append(curr_event)
            else:
                return False

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        if not self.case_status.get(self.curr_case, None):
            self.case_status[self.curr_case] = {'e': [], 'e2': []}

        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e < curr_event])
        last_event = case_events[-1] if case_events else None

        # 1 2 3 4 5 6
        # A,B,A,B,C,C
        # 1 1 2 2 1 2

        # Absence(G)
        # 1 2 3 4 5 6 7 8
        # A,A,G,A,F,E,G,G
        # 1 2 1 3 2 3 3 2
        # 1 2 1 3 1 2 2 3

        # 1 2 3 4 5 6 7 8
        # A,H,A,D,E,D,G,H
        # 1 1 2 2 2 1 2 2
        # 1 1 2 1 2 2 2 2

        # ChainResp(B, C) Absence(D, B)
        # 1 2 3 4 5 6 7 8 9 10
        # A,B,A,D,C,B,A,D,C,C
        # 1 1 2 2 1 2 3 1 1 2

        #                   1                   2
        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
        # A,B,C,A,A,B,A,C,B,A,C,D,B,C,B,C,D,D,E,D,D,E,F,G,F,E,\
        #               3                   4
        #         7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        #         G,G,H,G,G,H,B,C,I,H,H,I,D,J,J

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if last_event and self.data[last_event][self.attr] == self.val:
                return False

            self.case_status[curr_case]['e'].append(curr_event)
            self.forward_check_events(events, domains, assignments, 'e2')
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            if last_event in self.case_status[curr_case]['e'] and self.data[last_event][self.attr] == self.val:
                self.case_status[curr_case]['e'].remove(last_event)
                return True
            else:
                if self.find_events_in_list(curr_event, curr_case, 'e', True):
                    return False
        else:
            if last_event and self.data[last_event][self.attr] == self.val:
                return False

        return True


# each time B occurs, A immediately beforehand
class ChainPrecedence(BaseEventConstraint):
    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        # Absence(D, B)
        # 1 2 3 4 5 6 7 8
        # A,B,A,D,B,C,D,C
        # 1 1 2 2 2 1 1 2

        # A,A,B,B,C,C
        # 1 2 1 2 1 2

        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e < curr_event])
        last_event = case_events[-1] if case_events else None

        if self.data[curr_event][self.attr2] == self.val2:
            if not last_event or self.data[last_event][self.attr] != self.val:
                return False

        return True


# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):

    def forward_check_events(self, events, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        attr, val = self.attr, self.val
        attr2, val2 = self.attr2, self.val2

        flag = False
        flag2 = False
        for event in events[curr_event:]:
            # if event not in assignments:
                # B no(B) C
                # B B C
                # B C B
                # if C found
            if self.data[event][attr2] == val2:
                domain = domains[event]
                if curr_case in domain:
                    flag = True
                    if len(domain) > 1:
                        for case in domain[:]:
                            if case != curr_case:
                                domain.hideValue(case)
                    return True
                # if B found
            elif self.data[event][attr] == val and not flag:
                domain = domains[event]
                if curr_case in domain:
                    for case in domain[:]:
                        if case == curr_case:
                            domain.hideValue(case)
                            break

        return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e <= curr_event])

        # A,A,B,B,C,C
        # 1 2 1 2 1 2

        # 1 2 3 4 5 6 7 8 9
        # A,A,C,C,B,B,D,D,C
        # 1 2 1 2 1 1 1 2 1

        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
        # A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I,D,C,B,E,D,G,F,H,G,I,C,B,J,L

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,B,D,C,A,B,C
        # 1 2 1 2 1 1 3 3 2

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,D,C,A,B,C,B
        # 1 2 1 1 1 3 2 2 3

        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
        # A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I
        # 1 2 1 2 1 2 1 2 1 1 1 1 1 1 1 1

        # B D
        # C D

        # B no(B) C
        # if B
        if self.data[curr_event][self.attr] == self.val:
            flag = False
            for event in case_events:
                if self.data[event][self.attr] == self.val:
                    if flag:
                        return False
                    flag = True
                if self.data[event][self.attr2] == self.val2:
                    if flag:
                        flag = False

            self.forward_check_events(events, domains, assignments, 'e')

        return True


# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
# A no(B) B J no(I) I
class AlternatePrecedence(BaseEventConstraint):

    # def forward_check_events(self, events, domains, assignments, event_type):
    #     curr_event = list(assignments)[-1]
    #     curr_case = assignments[curr_event]
    #     if event_type == 'e':
    #         attr, val = self.attr, self.val
    #         attr2, val2 = self.attr2, self.val2
    #     else:
    #         attr, val = self.attr2, self.val2
    #         attr2, val2 = self.attr, self.val
    #
    #     flag = False
    #     flag2 = False
    #
    #     # B no(C) C
    #     # B C! B C
    #
    #     for event in events[curr_event:]:
    #         # if event not in assignments:
    #         # if B found
    #         if self.data[event][attr2] == val2 and not flag:
    #             flag = True
    #         # if another C found
    #         if self.data[event][attr] == val:
    #             # if B not found before
    #             if flag:
    #                 return True
    #             else:
    #                 domain = domains[event]
    #                 if curr_case in domain:
    #                     # if len(domain) > 1
    #                     for case in domain[:]:
    #                         if case == curr_case:
    #                             domain.hideValue(case)
    #                             return True
    #
    #     return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        case_events = sorted([e for e, c in assignments.items() if c == curr_case and e <= curr_event])

        # if not self.case_status.get(curr_case, None):
        #     self.case_status[curr_case] = []

        # if C, preceded by B and no B in between
        # (B, C) B no(C) C
        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2

        # 1 2 3 4 5 6 7
        # A,A,B,D,B,C,C
        # 1 2 1 1 2 1 2

        # 1 2 3 4 5 6 7 8
        # A,A,B,D,B,C,C,C
        # 1 2 1 1 2 1 2 1

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 2

        # B no(C) C
        # G no(H) H

        # if C
        if self.data[curr_event][self.attr2] == self.val2:
            flag = False
            for event in case_events:
                # B
                if self.data[event][self.attr] == self.val:
                    flag = True
                # C
                if self.data[event][self.attr2] == self.val2:
                    if not flag:
                        return False
                    flag = False

        # # if B
        # if self.data[curr_event][self.attr] == self.val:
        #     self.case_status[curr_case].append({'e': curr_event})
        # # if C
        # elif self.data[curr_event][self.attr2] == self.val2:
        #     pairs = self.find_events_in_pairs(curr_event, curr_case, 'e', True, True)
        #
        #     if pairs:
        #         last_pair = pairs[-1]
        #         if not last_pair.get('e2'):
        #             # if self.check_occurrence(assignments, last_pair['e'], 'e2'):
        #             last_pair['e2'] = curr_event
        #
        #             # self.forward_check_events(events, domains, assignments, 'e2')
        #             return True
        #
        #     return False

        return True
