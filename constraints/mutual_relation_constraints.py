
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    def reject_conditions(self, event, case, event_type, with_pair=False):
        event_type2 = 'e2' if event_type == 'e' else 'e'
        events = self.find_events_in_pairs(event, case, event_type, True, with_pair)
        events2 = self.find_events_in_pairs(event, case, event_type2, True, with_pair)
        # if with_pair:
        #     return not ((events2 and events) or (events2 and not events))
        return not events2

    def has_available_cases(self, domains, assignments, event_type, with_pair=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]

        available_cases = []
        for case, events in self.case_status.items():
            # if case in event_domains[event_domains.index(curr_case)+1:]:
            if case in event_domains:
                if not self.reject_conditions(curr_event, case, event_type, with_pair):
                    available_cases.append(case)

        return available_cases

    def check_rejection(self, domains, assignments, event_type, with_pair=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]
        cases = self.has_available_cases(domains, assignments, event_type, with_pair)

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

        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = []

            # A,A,C,C
            # 1 2 1 1

            # 1 2 3 4 5 6 7 8 9
            # A,A,A,B,C,B,C,C,C
            # 1 2 3 1 1 2 2 1 1
            # 1 2 3 1 1 2 2 3 3

            # 1 2 3 4 5 6 7 8 9
            # A,A,B,C,C,A,B,C,B
            # 1 2 1 1 2 3 2 3 3

      # now   1 2 1 2 2 3 3 1 2

        # if B
        if self.data[curr_event][self.attr] == self.val:
            pairs = self.find_events_in_pairs(events, curr_case, 'e2', False, True)
            if pairs:
                target_event = self.find_events_in_pairs(curr_event, curr_case, 'e2', False, False, pairs)
                if target_event:
                    target_event[0]['e'] = curr_event
                    self.prev_assignments[curr_event] = None
                    return True
                else:
                    if self.check_rejection(domains, assignments, 'e'):
                        return False
            else:
                if self.check_rejection(domains, assignments, 'e', True):
                    return False

            self.case_status[curr_case].append({'e': curr_event})
        # if C
        elif self.data[curr_event][self.attr2] == self.val2:
            pairs = self.find_events_in_pairs(events, curr_case, 'e', False, True)
            if pairs:
                target_event = self.find_events_in_pairs(curr_event, curr_case, 'e', False, False, pairs)
                if target_event:
                    target_event[0]['e2'] = curr_event
                    self.prev_assignments[curr_event] = None
                    return True
                else:
                    if self.check_rejection(domains, assignments, 'e2'):
                        return False
            else:
                if self.check_rejection(domains, assignments, 'e2', True):
                    return False

            self.case_status[curr_case].append({'e2': curr_event})

        # self.case_status[curr_case].setdefault('e', [])
        # self.case_status[curr_case].setdefault('e2', [])
        #
        # if self.data[curr_event][self.attr] == self.val:
        #     events = self.find_events_in_list(curr_event, curr_case, 'e')
        #     events2 = self.find_events_in_list(curr_event, curr_case, 'e2')
        #     # if e2 exists
        #     if events2:
        #         # if e doesn't exist yet
        #         if not events:
        #             self.case_status[curr_case]['e'].append(curr_event)
        #             self.prev_assignments[curr_event] = None
        #             return True
        #         # if both exist
        #         else:
        #             if self.check_rejection(domains, assignments, 'e'):
        #                 return False
        #
        #     self.case_status[curr_case]['e'].append(curr_event)
        # # if C
        # elif self.data[curr_event][self.attr2] == self.val2:
        #     events = self.find_events_in_list(curr_event, curr_case, 'e2')
        #     events2 = self.find_events_in_list(curr_event, curr_case, 'e')
        #     # if e2 exists
        #     if events2:
        #         # if e doesn't exist yet
        #         if not events:
        #             self.case_status[curr_case]['e2'].append(curr_event)
        #             self.prev_assignments[curr_event] = None
        #             return True
        #         # if both exist
        #         else:
        #             if self.check_rejection(domains, assignments, 'e2'):
        #                 return False
        #
        #     self.case_status[curr_case]['e2'].append(curr_event)

        self.prev_assignments[curr_event] = None

        return True


