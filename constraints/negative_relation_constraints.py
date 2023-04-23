
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint


# A and B never occur together: <C, C, A, C>, NOT: <B, C, A, C>
class NotCoexistence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # if B
        if self.data[curr_event][self.attr] == self.val:
            not_target_event = self.find_events_in_pairs(curr_event, curr_case, 'e2')
            if not_target_event:
                return False

            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            not_target_event = self.find_events_in_pairs(curr_event, curr_case, 'e')
            if not_target_event:
                return False

            self.case_status[curr_case].append({'e2': curr_event})

        return True


# B cannot occur after A: [^A]*(A[^B]*)* <B, B, C, A, A>, <B, B, C>, <A, A, C>
class NotSuccession(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

        # if B
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            not_target_event = self.find_events_in_pairs(curr_event, curr_case, 'e')
            if not_target_event:
                return False
            self.case_status[curr_case].append({'e2': curr_event})

        return True


# A and B cannot occur contiguously: <B, B, A, A>, <A, C, B, A, C, B>
# A and B occur if and only if no B occurs immediately after A
class NotChainSuccession(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []


        # if A
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_event]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was A
                if self.data[prev_id][self.attr] == self.val:
                    return False

        return True
