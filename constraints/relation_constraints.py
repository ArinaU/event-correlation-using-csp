
from constraint import *
from constraints.base_event_constraint import BaseEventConstraint
from copy import deepcopy


# If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
class RespondedExistence(BaseEventConstraint):

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        buf = self._buf
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']
        curr_id = list(assignments)[-1]

        curr_case = assignments[curr_id]

        case_status = self.clean_struct(assignments, case_status)
        buf = self.clean_struct(assignments, buf)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # # if B
        # if data[curr_id][required_attr] == required_value:
        #     self._case_status[curr_case].setdefault('e', []).append(curr_id)
        # # if C
        # elif data[curr_id][required_attr2] == required_value2:
        #     # if case_status[curr_case].get('e2'):
        #     if 'e2' in self._case_status[curr_case]:  # if C already exists
        #         if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
        #             return False
        #         else:
        #             buf.setdefault('e2', []).append(curr_id)
        #     else:
        #         self._case_status[curr_case].setdefault('e2', []).append(curr_id)
        #
        # if buf:
        #     if self.find_solutions(domains, self._case_status, [curr_id], 'e2'):
        #         return False

        # 1 2 3 4 5 6 7 8 9
        # A,C,B,A,A,B,C,C,B
        # 1 1 1 2 3 2 2 3 3
        # 1 1 1 2 3 2 1 1 3

        # if B
        if data[curr_id][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            occurrences = [e['e2'] for e in case_status[curr_case] if 'e2' in e]
            # if already exists
            if occurrences:
                if self.has_available_solutions(domains, case_status, curr_id, 'e2'):
                    return False
                else:
                    buf.setdefault('e2', []).append(curr_id)
            else:
                case_status[curr_case].append({'e2': curr_id})

        if buf:
            if self.has_available_solutions(domains, case_status, curr_id, 'e2'):
                return False

        return True



# If A occurs, then B occurs after A <C, A, A, C, B>, <B, C, C>
class Response(BaseEventConstraint):

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

        # 1 2 3 4 5 6 7 8
        # A,C,A,B,C,C,A,B
        # 1 1 2 2 2 1 3 3

        if data[curr_id][required_attr] == required_value:
            # pair where there's no 'e2'
            if self.find_occurrences_of_target_event(curr_case, 'e2'):
                return False
            else:
                case_status[curr_case].append({'e': curr_id})
        # if C
        # A,C,A,B,C,C,A,B
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, case_status, curr_id, 'e2'):
                    return False
                else:
                    case_status[curr_case].append({'e2': curr_id})

        return True


# B occurs only if preceded by A: <C, A, C, B, B>, <A, C, C>
# C occurs only if preceded by B
class Precedence(BaseEventConstraint):

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
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                return False

        return True


# If A occurs, then B occurs immediately after A <A, B, B>, <A, B, C, A, B>
class ChainResponse(BaseEventConstraint):
    lock = {}

    def __call__(self, events, domains, assignments, forwardcheck=False):
        data = self._data
        case_status = self._case_status
        required_attr = self._required_event['attr']
        required_value = self._required_event['value']
        required_attr2 = self._required_event2['attr']
        required_value2 = self._required_event2['value']

        curr_id = list(assignments)[-1]
        curr_case = assignments[curr_id]

        # if ChainResponse.lock.get(curr_id) == self:
        #     ChainResponse.lock[curr_id] = None

        case_status = self.clean_struct(assignments, case_status)

        if not case_status.get(curr_case, None):
            case_status[curr_case] = []

        # case_events = sorted([e for e, c in assignments.items() if c == curr_case])
        # last_id = case_events[-2] if len(case_events) > 1 else None

        # # if curr element is C
        # if data[curr_id][required_attr2] == required_value2:
        #     # if available B is found
        #     if last_id and data[last_id][required_attr] == required_value:
        #         case_status[curr_case][last_id] = curr_id
        #         ChainResponse.lock[curr_id] = self
        #     else:
        #         # check other cases
        #         if not ChainResponse.lock.get(curr_id) and self.has_available_solutions(domains, case_status,
        #                                                                                 curr_id, ):
        #             return False
        #
        # else: # if B or any other Activity
        #     if False in case_status[curr_case].values():
        #         return False
        #
        #     # if curr element is B
        #     if data[curr_id][required_attr] == required_value:
        #         case_status[curr_case][curr_id] = False

        # if curr element is B
        # if B

        # A,B,A,D,C,B,A,D,C,C

        # if B
        if data[curr_id][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, case_status, curr_id, 'e2'):
                    return False
        else:
            if self.find_single_target_event(curr_case, 'e'):
                return False

        return True



class ChainPrecedence(BaseEventConstraint):

    # each time B occurs, A immediately beforehand
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

        if data[curr_id][required_attr] == required_value:
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            case_events = [e for e, c in assignments.items() if c == curr_case and e < curr_id]
            if case_events:
                prev_id = case_events[-1]
                # if prev event was not B
                if not data[prev_id][required_attr] == required_value:
                    return False

            case_status[curr_case].append({'e2': curr_id})

        return True



# If A occurs, then B occurs afterwards, before A recurs: <A, B, C, A, C, B>, <A, B, B, A, B>
# After each activity A at least one activity B is executed
class AlternateResponse(BaseEventConstraint):

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
            not_target_event = self.find_single_target_event(curr_case, 'e')
            if not_target_event:
                return False
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            target_event = self.find_single_target_event(curr_case, 'e')
            if target_event:
                target_event['e2'] = curr_id
            else:
                if self.has_available_solutions(domains, case_status, curr_id, 'e2'):
                    return False
                else:
                    case_status[curr_case].append({'e2': curr_id})

        return True



# If B occurs, it's preceded by A and no other B in between: <C, A, C, B, A>, <A, B, C, A, A, C, B>
# Cannot be: <A, C, A, B, B>, <A, B, C, B>
# After each activity A at least one activity B is executed
class AlternatePrecedence(BaseEventConstraint):

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
            case_status[curr_case].append({'e': curr_id})
        # if C
        elif data[curr_id][required_attr2] == required_value2:
            if case_status[curr_case]:
                last_pair = case_status[curr_case][-1]
                if 'e2' in last_pair:
                    return False
                else:
                    last_pair['e2'] = curr_id
            else:
                return False

        return True

