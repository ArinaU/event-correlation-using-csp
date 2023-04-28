
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):
    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        all_cases = self.get_all_cases(events, domains)

        self.case_status = self.clean_case_status(assignments, self.case_status)

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
    # def check_future_case_assignment(self, events, domains, assignments, curr_case, event_type, target_type):
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

    # def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
    #     # other_event_type = 'e2' if event_type == 'e' else 'e'
    #     curr_event = list(assignments)[-1]
    #     curr_case = assignments[curr_event]
    #
    #     possible_cases = {}
    #     for case, status in self.case_status.items():
    #         if case in domains[curr_event]:
    #             if not self.case_status[case]['e']:
    #                 possible_cases.setdefault(event_type, []).append(case)
    #
    #     return possible_cases

    def forward_check_events(self, events, domains, assignments):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        for event in events:
            if event not in assignments:
                if self.data[event][self.attr] == self.val:
                    domain = domains[event]
                    if curr_case in domain:
                        for case in domain[:]:
                            if case == curr_case:
                                domain.hideValue(case)
                        return True
                    else:
                        return True

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

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

            if [c for c, e in self.case_status.items() if not e['e']]:
                self.forward_check_events(events, domains, assignments)

        self.prev_assignments[curr_event] = None

        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not self.case_status[case]['e']:
                    return False

        return True
