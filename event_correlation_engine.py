
from constraint import *
import pandas as pd
import os

from measures.log_to_log_case_measure import *
from measures.log_to_log_time_measure import *

class EventCorrelationEngine:
    def __init__(self, start_event, data_file, constraints):
        self._start_event = start_event
        self._data_file = data_file
        self._constraints = constraints

    def declare_domains(self, problem, data, start):
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

    def prepare_data(self, str, timestamp='Timestamp'):
        data = pd.read_csv(str, sep=',')
        data = data.sort_values(by=timestamp, ascending=True)
        data['EventID'] = range(1, len(data) + 1)
        data.set_index('EventID', inplace=True)
        return data


    def assign_cases(self, data, start_event, constraints):
        solver = RecursiveBacktrackingSolver(False)
        problem = Problem(solver)
        self.declare_domains(problem, data, start_event)

        for const in constraints:
            method = const['constraint']
            ev = const['e']
            ev2 = const.get('e2')
            if ev2:
                problem.addConstraint(method(data, ev, ev2, start_event))
            else:
                problem.addConstraint(method(data, ev, start_event))

        solutions = problem.getSolution()
        return solutions

    def generate_logs(self, data, assignments):
        data['SuggestedCaseID'] = list(assignments.values())

        outdir = './new_event_logs'
        filename = f"data{len(data)}"
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        fullname = os.path.join(outdir, filename)
        data.to_csv(fullname, sep=',')


    def generate(self):
        case_name = "CaseID" #TODO
        timestamp_name = "Start Timestamp"

        data = self.prepare_data(self._data_file, timestamp_name)
        datadict = data.to_dict(orient="index")

        result = self.assign_cases(datadict, self._start_event, self._constraints)

        self.generate_logs(data, result)

        measure = LogToLogCaseMeasure(datadict, result, case_name).trace_to_trace_similarity()
        measure2 = LogToLogCaseMeasure(datadict, result, case_name).case_similarity()
        measure3 = LogToLogCaseMeasure(datadict, result, case_name).trace_to_trace_frequency_similarity()
        measure4 = LogToLogCaseMeasure(datadict, result, case_name).partial_case_similarity()
        measure5 = LogToLogCaseMeasure(datadict, result, case_name).bigram_similarity()
        measure6 = LogToLogCaseMeasure(datadict, result, case_name).trigram_similarity()
        measure7 = LogToLogTimeMeasure(timestamp_name, datadict, result, case_name).event_time_deviation()
        measure8 = LogToLogTimeMeasure(timestamp_name, datadict, result, case_name).case_cycle_time_deviation()

        print(f"Result: {result}")
        print(f"Trace-to-trace similarity: {measure}")
        print(f"Case similarity: {measure2}")
        print(f"Trace-to-trace frequency similarity: {measure3}")
        print(f"Partial case similarity: {measure4}")
        print(f"Bigram similarity: {measure5}")
        print(f"Trigram similarity: {measure6}")
        print(f"Event time deviation: {measure7}")
        print(f"Case cycle time deviation: {measure8}")
