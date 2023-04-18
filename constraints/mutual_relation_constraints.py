
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint

# If B occurs, then A occurs and vice versa: <C, A, C, B, B>, <B, C, C, A>
class Coexistence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if B
        if data[curr_id][required_attr] == required_value:
            pairs = self.find_occurrences_of_target_event(curr_case, 'e2')
            if pairs:
                target_event = self.find_single_target_event(curr_case, 'e2', pairs)
                if target_event:
                    target_event.setdefault('e', []).append(curr_id)
                    return True

            if self.has_available_solutions(domains, assignments, case_status, 'e'):
                return False
            case_status[curr_case].append({'e': [curr_id]})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            pairs = self.find_occurrences_of_target_event(curr_case, 'e')
            if pairs:
                target_event = self.find_single_target_event(curr_case, 'e', pairs)
                if target_event:
                    target_event.setdefault('e2', []).append(curr_id)
                    return True
            if self.has_available_solutions(domains, assignments, case_status, 'e2'):
                return False
            case_status[curr_case].append({'e2': [curr_id]})

        return True


