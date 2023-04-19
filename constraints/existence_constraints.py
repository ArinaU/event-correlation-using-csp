
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):

    # def preProcess(self, events, domains, constraints, vconstraints):
    #     required_attr = self._required_event['attr']
    #     required_value = self._required_event['value']
    #     data = self._data
    #     all_cases = self.find_cases(events, domains)
    #
    #     for event in events:
    #         if all_cases:
    #             if data[event][required_attr] == required_value:
    #                 domain = domains[event]
    #                 #iterate over domain of curr event
    #                 for case in domain[:]:
    #                     if case != all_cases[0]:
    #                         domain.hideValue(case)
    #                 all_cases.pop(0)
    #         else:
    #             break

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_struct(assignments, self.case_status)

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

    def forwardCheckEvents(self, events, domains, assignments):
        # if left_cases:
        for event in events:
            if event not in assignments:
                if self.data[event][self.attr] == self.val:
                    domain = domains[event]
                    for case in domain:
                        if case in self.case_status and len(domain) > 1:
                            domain.hideValue(case)
                    return True
        return True


    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        all_cases = self.get_all_cases(events, domains)

        self.case_status = self.clean_struct(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # A,B,A,B,B,C
        # 1 1 2 2 1 1

        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 1

        if self.data[curr_event][self.attr] == self.val:
            if forwardcheck and len(all_cases) != len(self.case_status):
                self.forwardCheckEvents(events[curr_event:], domains, assignments)

            self.case_status[curr_case].append(curr_event)

        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not self.case_status.get(case):
                    return False

        return True
