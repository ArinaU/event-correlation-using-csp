
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
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, self._case_status)

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

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

    def forwardCheckEvents(self, events, domains, assignments, attr, val):
        data = self._data
        # curr_id = list(assignments)[-1]
        # curr_case = assignments[curr_id]
        # required_attr2 = self._required_event['attr']
        # required_value2 = self._required_event['value']

        # if left_cases:
        for event in events:
            if event not in assignments:
                if data[event][attr] == val:
                    domain = domains[event]
                    for case in domain:
                        if case in self._case_status and len(domain) > 1:
                            domain.hideValue(case)
                    return True
        return True


            # # if required event
            # if data[event][required_attr] == required_value:
            #     domain = domains[event]
            #     intersect = list(set(left_cases) & set(domain))
            #     left_cases = [c for c in left_cases if c not in intersect]

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        attr = self._required_event['attr']
        val = self._required_event['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]
        all_cases = self.find_cases(events, domains)

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # A,B,A,B,B,C
        # 1 1 2 2 1 1

        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 1 1 3

        # 1 2 3 4 5 6 7 8 9
        # A,B,B,C,B,C,A,B,C
        # 1 1 1 1 1 1 2 2 1

        if data[curr_id][attr] == val:
            if forwardcheck and len(all_cases) != len(case_status):
                self.forwardCheckEvents(events[curr_id:], domains, assignments, attr, val)

            case_status[curr_case].append(curr_id)


        if len(assignments) == len(events):
            for case in set(assignments.values()):
                if not case_status.get(case):
                    return False

        return True