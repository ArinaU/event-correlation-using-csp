
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    # def has_available_cases(self, domains, assignments, event_type):
    #     curr_event = list(assignments)[-1]
    #     curr_case = assignments[curr_event]
    #     event_domains = domains[curr_event]
    #     other_event_type = 'e2' if event_type == 'e' else 'e'
    #
    #     available_cases = []
    #
    #     # if both B and C
    #     if self.case_status[curr_case][event_type] and self.case_status[curr_case][other_event_type]:
    #         for case, events in self.case_status.items():
    #             if case in event_domains:
    #                 events = self.find_events_in_list(curr_event, case, event_type)  # B
    #                 other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C
    #
    #                 # if empty B and any C
    #                 if not events and other_events:
    #                     return [case]
    #     else: # no B and no C | only B and no C
    #         for case, events in self.case_status.items():
    #             if case in event_domains:
    #                 events = self.find_events_in_list(curr_event, case, event_type)  # B
    #                 other_events = self.find_events_in_list(curr_event, case, other_event_type)  # C
    #
    #                 # if empty B and any C
    #                 if not events and other_events:
    #                     return [case]
    #                 # else:
    #                 #     # if both B and C
    #                 #     if events and other_events:
    #                 #         available_cases.append(case)
    #     return available_cases


    def check_possible_cases(self, events, domains, assignments, event_type, target_type=None):
        # other_event_type = 'e2' if event_type == 'e' else 'e'
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]

        # empty_cases = {}
        possible_cases = {}
        for case, status in self.case_status.items():
            if case != curr_case and case in domains[curr_event]:
                if not status[event_type] and not status[target_type]:
                    continue
                # if not status[other_event_type]:
                #     empty_cases.setdefault(event_type, []).append(case)
                elif len(status[target_type]) > len(status[event_type]) \
                        or (status[target_type] and not status[event_type]):
                    possible_cases.setdefault(event_type, []).append(case)

        # return empty_cases, possible_cases
        return possible_cases

    def __call__(self, events, domains, assignments, forwardcheck=False):
        curr_event = list(assignments)[-1]
        curr_case = assignments[curr_event]
        self.case_status = self.clean_case_status(assignments, self.case_status)

        if not self.case_status.get(curr_case, None):
            self.case_status[curr_case] = {'e': [], 'e2': []}

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,C,C,A,B,C,B
        # 1 2 1 1 2 3 2 3 3

        # 1 2 3 4 5 6 7 8 9
        # A,A,A,B,C,B,C,C,C
        # 1 2 3 1 1 2 2 1 1

        # if B
        if self.data[curr_event][self.attr] == self.val:
            self.case_status[curr_case].setdefault('e', []).append(curr_event)

            if not self.case_status[curr_case]['e2']:
                # if not self.forward_check_events(events, domains, assignments, 'e2'):
                #     if self.check_possible_cases(events, domains, assignments, 'e', 'e2'):
                #         return False

                self.forward_check_events(events, domains, assignments, 'e2')

        elif self.data[curr_event][self.attr2] == self.val2:
            self.case_status[curr_case].setdefault('e2', []).append(curr_event)

            if not self.case_status[curr_case]['e']:
                # if not self.forward_check_events(events, domains, assignments, 'e'):
                #     if self.check_possible_cases(events, domains, assignments, 'e2', 'e'):
                #         return False
                self.forward_check_events(events, domains, assignments, 'e')

        return True


