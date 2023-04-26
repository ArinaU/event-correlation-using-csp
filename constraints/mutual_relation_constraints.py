
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    def has_available_cases(self, domains, assignments, event_type):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        event_domains = domains[curr_event]
        other_event_type = 'e2' if event_type == 'e' else 'e'

        available_cases = []

        # if both B and C
        if self.case_status[curr_case][event_type] and self.case_status[curr_case][other_event_type]:
            for case, events in self.case_status.items():
                if case in event_domains:
                    events = self.find_events_in_list(curr_event, case, event_type)  # B
                    other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C

                    # if empty B and any C
                    if not events and other_events:
                        return [case]
        else: # no B and no C | only B and no C
            for case, events in self.case_status.items():
                if case in event_domains:
                    events = self.find_events_in_list(curr_event, case, event_type)  # B
                    other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C

                    # if empty B and any C
                    if not events and other_events:
                        return [case]
                    else:
                        # if both B and C
                        if events and other_events:
                            available_cases.append(case)


        return available_cases


    def check_case_status(self, events, domains, assignments, event_type):
        other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        if event_type == 'e':
            attr, val = self.attr2, self.val2
        else:
            attr, val = self.attr, self.val

        empty_cases = {}
        possible_cases = {}
        for case, status in self.case_status.items():
            if case in domains[curr_event]:
                if not status['e'] and not status['e2']:
                    continue
                if not status[other_event_type]:
                    empty_cases.setdefault(event_type, []).append(case)
                elif len(status[other_event_type]) > len(status[event_type]):
                    possible_cases.setdefault(event_type, []).append(case)

        # ????
        if not empty_cases:
            return True

        # Cases with no 'e': ['Case2']
        # Cases with superfluous 'e2': ['Case1']

        # if B, check there are any C in future with this case in domain
        all_cases_occur = True
        found_cases = set()
        for case in empty_cases[event_type]:
            case_occurs = False
            for future_event in events:
                if future_event not in assignments:
                    if self.data[future_event][attr] == val:
                        if case in domains[future_event] and case not in found_cases:
                            found_cases.add(case)
                            case_occurs = True
                            break
            if not case_occurs:
                all_cases_occur = False
                break

        if all_cases_occur:
            return True

        remaining_cases_occur = True
        for event_type, cases in possible_cases.items():
            remaining_cases = set(empty_cases[event_type]) - found_cases
            remaining_cases_occur = True
            for case in remaining_cases:
                if case not in possible_cases.get(event_type, []):
                    remaining_cases_occur = False
                    break

        if remaining_cases_occur:
            return False


    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8 9
        # A,A,A,B,C,B,C,C,C
        # 1 2 3 1 1 2 2 1 1

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,C,C,A,B,C,B
        # 1 2 1 1 2 3 2 3 3

        # if B
        if self.data[curr_event][self.attr] == self.val:
            if not (self.case_status[curr_case]['e2'] and not self.case_status[curr_case]['e']):
                if self.check_rejection(domains, assignments, 'e'):
                    return False

            self.case_status[curr_case].setdefault('e', []).append(curr_event)

            if not self.check_case_status(events, domains, assignments, 'e'):
                return False
        elif self.data[curr_event][self.attr2] == self.val2:
            if not (self.case_status[curr_case]['e'] and not self.case_status[curr_case]['e2']):
                if self.check_rejection(domains, assignments, 'e2'):
                    return False

            self.case_status[curr_case].setdefault('e2', []).append(curr_event)

            if not self.check_case_status(events, domains, assignments, 'e2'):
                return False

            # if B
            # if no B and no C
            #   check_rejection
            #   check there if other cases with C and empty B
            #       if no such cases, check other cases with C and B
            #
            # if only B and no C
            #   check_rejection
            #   check there if other cases with C and empty B
            #       if no such cases, check other cases with C and B
            # if only C and no B - ideal
            #   return True in call() and append
            # if B and C
            #   check_rejection
            #   check there if other cases with C and empty B, i.e. B required elsewhere
            #   if no such cases, that's it, return True and append


            # # if B
            # if self.data[curr_event][self.attr] == self.val:
            #     # if C exists
            #     if self.case_status[curr_case]['e2'] and self.case_status[curr_case]['e']:
            #         if self.check_rejection(domains, assignments, 'e'):
            #             return False
            #
            #     self.case_status[curr_case].setdefault('e', []).append(curr_event)
            #
            # elif self.data[curr_event][self.attr2] == self.val2:
            #     if self.case_status[curr_case]['e2'] and self.case_status[curr_case]['e']:
            #         # if B exists
            #         if self.check_rejection(domains, assignments, 'e2'):
            #             return False
            #
            #     self.case_status[curr_case].setdefault('e2', []).append(curr_event)


        self.prev_assignments[curr_event] = None
        return True


