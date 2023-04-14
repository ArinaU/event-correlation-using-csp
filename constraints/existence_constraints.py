
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint



# A occurs at most once
class Absence(BaseEventConstraint):

    def __init__(self, data, required_event, start_event = None):
        self._data = data
        self._required_event = required_event
        self._start_event = start_event
        self._case_status = {}

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

    def __init__(self, data, required_event, start_event = None):
        self._data = data
        self._required_event = required_event
        self._start_event = start_event
        self._case_status = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, self._case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # if required element
        if data[curr_id][required_attr] == required_value:
            # if was before
            if not case_status[curr_case]:

                count = 0
                # how many cases in total
                max_cases = [k for k, v in data.items() if v[self._start_event['attr']] == self._start_event['value']]
                unassigned_cases = len(max_cases) - len(case_status)
                for event in events:
                    if event not in assignments and data[event][required_attr] == required_value:
                        if count < unassigned_cases:
                            domain = domains[event]
                            for value in domain[:]:
                                if value in case_status:
                                    domain.hideValue(value)
                                    domain.resetState()
                            count += 1

            case_status[curr_case].append(curr_id)

        # check at the last event
        if curr_id == len(events):
            for case in set(assignments.values()):
                if not case_status.get(case):
                    return False

        return True