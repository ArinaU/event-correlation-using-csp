
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):
    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        if self.data[curr_event][self.attr] == self.val:
            if self.case_status[curr_case]:
                return False
            else:
                self.case_status[curr_case] = curr_event
        return True


# A occurs at least once
class Existence(BaseEventConstraint):

    def get_all_cases(self, events, domains):
        cases = []
        for event in events:
            if self.data[event][self.attr] == self.start_event['value']:
                cases.append(domains[event][0])
        return cases

    def forward_check_events(self, events, domains, assignments):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        all_cases = self.get_all_cases(events, domains)

        existing_cases = [c for c, e in self.case_status.items() if e['e']]

        left_cases = [e for e in all_cases if e not in existing_cases]

        if left_cases:
            for event in events:
                if event not in assignments:
                    if self.data[event][self.attr] == self.val:
                        domain = domains[event]
                        if left_cases[0] in domain:
                            for case in domain[:]:
                                if case != left_cases[0]:
                                    domain.hideValue(case)
                            return True
                        else:
                            return True

    def __call__(self, events, domains, assignments, forwardcheck=False):
        BaseEventConstraint.__call__(self, events, domains, assignments, forwardcheck)
        curr_event = self.curr_event
        curr_case = self.curr_case

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])

        # A,B,A,B,B,C
        # 1 1 2 2 1 1

        # 1 2 3 4 5 6
        # A,B,A,B,B,C
        # 1 1 2 2 1 1

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

        # 1 2 3 4 5
        # A,A,B,B,C
        # 1 2 1 2 1

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 1

        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case]['e'].append(curr_event)

            # if [c for c, e in self.case_status.items() if not e['e']]:
            #     self.forward_check_events(events, domains, assignments)

        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not self.case_status[case]['e']:
                    return False

        return True
