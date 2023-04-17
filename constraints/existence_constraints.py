
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, self._case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = {}

        if data[curr_id][required_attr] == required_value:
            if case_status[curr_case]:
                return False
            else:
                case_status[curr_case] = curr_id

        return True


# A occurs at least once
class Existence(BaseEventConstraint):

    def preProcess(self, events, domains, constraints, vconstraints):
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        data = self._data
        all_cases = self.find_cases(events, domains)

        for event in events:
            if all_cases:
                if data[event][required_attr] == required_value:
                    domain = domains[event]
                    for case in domain[:]:
                        if case == all_cases[0]:
                            target_case = domain.pop(domain.index(case))
                            domain.insert(0, target_case)
                            all_cases.pop(0)
                            break
            else:
                break

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if required element
        if data[curr_id][required_attr] == required_value:
            # if assigned to the existing case, check that enough req events left
            if case_status[curr_case]:
                left_cases = self.find_cases(events[curr_id:], domains)
                for event in events[curr_id:]:
                    if left_cases:
                        # if required event
                        if data[event][required_attr] == required_value:
                            domain = domains[event]
                            intersect = list(set(left_cases) & set(domain))
                            left_cases = [c for c in left_cases if c not in intersect]
                    else:
                        break

                if left_cases:
                    return False

        case_status[curr_case].append(curr_id)

        # check at the last event
        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not case_status.get(case):
                    return False

        return True