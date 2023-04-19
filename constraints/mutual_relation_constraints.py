
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    def forwardCheckEvents(self, events, domains, assignments, attr, val):
        data = self._data
        curr_case = assignments[self._curr_event]
        # required_attr2 = self._required_event2['attr']
        # required_value2 = self._required_event2['value']

        for event in events:
            if event not in assignments:
                if data[event][attr] == val:
                    domain = domains[event]
                    if curr_case in domain and len(domain) > 1:
                        for value in domain[:]:
                            if value != curr_case:
                                domain.hideValue(value)
                    return True
        else:
            return False

    def __call__(self, events, domains, assignments, forwardcheck=False):
        case_status = self._case_status
        attr = self._required_event['attr']
        val = self._required_event['value']
        attr2 = self._required_event2['attr']
        val2 = self._required_event2['value']

        self.curr_event = list(assignments)[-1]
        self.curr_case = assignments[self.curr_event]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(self.curr_case, None):
            self.case_status[curr_case] = []

        # # if B
        # if data[curr_event][required_attr] == required_value:
        #     pairs = self.find_occurrences_of_event(events, curr_case, 'e2')
        #     if pairs:
        #         target_event = self.find_single_event(curr_case, 'e2', pairs)
        #         if target_event:
        #             target_event.setdefault('e', []).append(curr_event)
        #             return True
        #
        #     if self.has_available_solutions(domains, assignments, case_status, 'e'):
        #         return False
        #     case_status[curr_case].append({'e': [curr_event]})
        # # if C
        # elif data[curr_event][required_attr2] == required_value2:
        #     pairs = self.find_occurrences_of_event(events, curr_case, 'e')
        #     if pairs:
        #         target_event = self.find_single_event(curr_case, 'e', pairs)
        #         if target_event:
        #             target_event.setdefault('e2', []).append(curr_event)
        #             return True
        #     if self.has_available_solutions(domains, assignments, case_status, 'e2'):
        #         return False
        #     case_status[curr_case].append({'e2': [curr_event]})

        # 1 2 3 4 5 6 7 8 9
        # A,A,B,C,C,A,B,C,B
        # 1 2 1 1 2 3 2 3 3

        # if B
        if self._data[curr_event][attr] == val:
            # if no Cs yet
            if not self.find_event_type(events, curr_case):
                # if solutions among existing cases and no future ones
                if self.has_available_solutions(domains, assignments, case_status, 'e') \
                        and prev_assignments[self._curr_event] != curr_case:
                    prev_assignments[self._curr_event] = curr_case
                    return False

                if forwardcheck:
                    self.forwardCheckEvents(events[self._curr_event:], domains, assignments, attr2, val2)


        return True


