
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):

    def check_next_events(self, events, domains, assignments):
        curr_event = list(assignments)[-1]

        for event in events[curr_event:]:
            if event not in assignments:
                if self.data[event][self.attr] == self.val:
                    domain = domains[event]
                    for case in domain[:]:
                        if self.case_status.get(case) and len(domain) > 1:
                            domain.hideValue(case)
                    return True
        return True

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
                if len(all_cases) != len(self.case_status):
                    self.check_next_events(events, domains, assignments)

                self.case_status[curr_case] = curr_event
        return True


# A occurs at least once
class Existence(BaseEventConstraint):
    def reject_conditions(self, event, case, event_type):
        events = self.find_events_in_list(event, case, event_type)
        return events

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        all_cases = self.get_all_cases(events, domains)

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {}

        self.case_status[curr_case].setdefault('e', [])

        # A,B,A,B,B,C
        # 1 1 2 2 1 1

        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 1

        if self.data[curr_event][self.attr] == self.val:
            if self.reject_conditions(curr_event, curr_case, 'e'):
                if self.check_rejection(domains, assignments, 'e'):
                    return False

            self.case_status[curr_case]['e'].append(curr_event)

        self.prev_assignments[curr_event] = None

        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not self.case_status[case]['e']:
                    return False

        return True
