import pandas as pd
import os
from constraints.existence_constraints import *
from constraints.relation_constraints import *
from constraints.mutual_relation_constraints import *
from constraints.negative_relation_constraints import *
from measures.log_to_log_case_measure import *
from measures.log_to_log_time_measure import *


def declare_domains(problem, data, start):
    attr = start['attr']
    value = start['value']
    iter = 1
    for id, val in data.items():
        # if equal to start event
        if val[attr] == value:
            # problem.addVariable(id, [iter])
            problem.addVariable(id, [f"Case{iter}"])
            iter += 1
        # if n-th events
        else:
            # problem.addVariable(id, list(range(1, iter)))
            problem.addVariable(id, [f"Case{i}" for i in range(1, iter)])


def prepare_data(str, timestamp='Timestamp'):
    data = pd.read_csv(str, sep=',')
    data = data.sort_values(by=timestamp, ascending=True)
    data['EventID'] = range(1, len(data) + 1)
    data.set_index('EventID', inplace=True)
    return data


def assign_cases(data, start_event, constraints):
    solver = RecursiveBacktrackingSolver();
    problem = Problem(solver)

    declare_domains(problem, data, start_event)

    # problem.addConstraint(Absence(data, {'attr': 'Activity', 'value': 'B'}))

    for const in constraints:
        method = const['constraint']
        ev = const['e']
        ev2 = const.get('e2')
        if ev2:
            problem.addConstraint(method(data, ev, ev2))
        else:
            problem.addConstraint(method(data, ev))

    solutions = problem.getSolution()

    return solutions


def generate_logs(data, assignments):
    data['SuggestedCaseID'] = list(assignments.values())

    outdir = './new_event_logs'
    filename = f"data{len(data)}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    fullname = os.path.join(outdir, filename)

    data.to_csv(fullname, sep=',')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_event = {'attr': 'Activity', 'value': 'A'}
    case_name = "CaseID"
    timestamp_name = "Start Timestamp"

    data_file = 'event_logs/data105.csv'

    data = prepare_data(data_file, timestamp_name)

    datadict = data.to_dict(orient="index")

    constraints = [
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'A'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'L'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'B'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'C'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'I'}},
        {'constraint': Existence,
         'e': {'attr': 'Activity', 'value': 'D'}},
        {'constraint': Absence,
         'e': {'attr': 'Activity', 'value': 'K'}},
        {'constraint': AlternateResponse,
         'e': {'attr': 'Activity', 'value': 'B'},
         'e2': {'attr': 'Activity', 'value': 'D'}},
        {'constraint': AlternateResponse,
         'e': {'attr': 'Activity', 'value': 'C'},
         'e2': {'attr': 'Activity', 'value': 'D'}},
        {'constraint': Precedence,
         'e': {'attr': 'Activity', 'value': 'A'},
         'e2': {'attr': 'Activity', 'value': 'B'}},
        {'constraint': Precedence,
         'e': {'attr': 'Activity', 'value': 'A'},
         'e2': {'attr': 'Activity', 'value': 'C'}},
        {'constraint': Coexistence,
         'e': {'attr': 'Activity', 'value': 'B'},
         'e2': {'attr': 'Activity', 'value': 'C'}},
        {'constraint': ChainResponse,
         'e': {'attr': 'Activity', 'value': 'F'},
         'e2': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': ChainResponse,
         'e': {'attr': 'Activity', 'value': 'E'},
         'e2': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': ChainPrecedence,
         'e': {'attr': 'Activity', 'value': 'G'},
         'e2': {'attr': 'Activity', 'value': 'H'}},
        {'constraint': ChainPrecedence,
         'e': {'attr': 'Activity', 'value': 'I'},
         'e2': {'attr': 'Activity', 'value': 'J'}},
        {'constraint': NotChainSuccession,
         'e': {'attr': 'Activity', 'value': 'D'},
         'e2': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': NotSuccession,
         'e': {'attr': 'Activity', 'value': 'J'},
         'e2': {'attr': 'Activity', 'value': 'I'}},  # redundant?
        {'constraint': ChainPrecedence,
         'e': {'attr': 'Activity', 'value': 'J'},
         'e2': {'attr': 'Activity', 'value': 'K'}},
        {'constraint': RespondedExistence,
         'e': {'attr': 'Activity', 'value': 'F'},
         'e2': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': RespondedExistence,
         'e': {'attr': 'Activity', 'value': 'E'},
         'e2': {'attr': 'Activity', 'value': 'G'}},
        {'constraint': RespondedExistence,
         'e': {'attr': 'Activity', 'value': 'K'},
         'e2': {'attr': 'Activity', 'value': 'L'}},
        {'constraint': AlternatePrecedence,
         'e': {'attr': 'Activity', 'value': 'H'},
         'e2': {'attr': 'Activity', 'value': 'I'}},
        {'constraint': AlternatePrecedence,
         'e': {'attr': 'Activity', 'value': 'G'},
         'e2': {'attr': 'Activity', 'value': 'H'}}
    ]

    result = assign_cases(datadict, start_event, constraints)

    generate_logs(data, result)

    measure = LogToLogCaseMeasure(datadict, result, case_name).trace_to_trace_similarity()

    measure2 = LogToLogCaseMeasure(datadict, result, case_name).case_similarity()

    measure3 = LogToLogCaseMeasure(datadict, result, case_name).trace_to_trace_frequency_similarity()

    measure4 = LogToLogCaseMeasure(datadict, result, case_name).partial_case_similarity()

    measure5 = LogToLogCaseMeasure(datadict, result, case_name).bigram_similarity()

    measure7 = LogToLogTimeMeasure(timestamp_name, datadict, result, case_name).event_time_deviation()

    measure8 = LogToLogTimeMeasure(timestamp_name, datadict, result, case_name).case_cycle_time_deviation()


    print(result)
    print(measure)
    print(measure2)
    print(measure3)
    print(measure4)
