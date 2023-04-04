
from constraint import *
import pandas as pd
import os
import sys

from measures.log_to_log_case_measure import *
from measures.log_to_log_time_measure import *
from constraints.existence_constraints import *
from constraints.relation_constraints import *
from constraints.mutual_relation_constraints import *
from constraints.negative_relation_constraints import *

class EventCorrelationEngine:
    def __init__(self, start_event, constraints):
        self._start_event = start_event
        self._constraints = constraints
        self._case_name = "CaseID"  # TODO
        self._timestamp_name = "Start Timestamp"
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, input_data = None):
        if isinstance(input_data, pd.DataFrame):
            self._data = input_data
        # elif self._data_file:
        elif isinstance(input_data, str):
            data = pd.read_csv(input_data, sep=',')
            data = data.sort_values(by=self._timestamp_name, ascending=True)
            data['EventID'] = range(1, len(data) + 1)
            data.set_index('EventID', inplace=True)
            self._data = data
        else:
            raise ValueError("Input must be a dataframe or a csv file.")

    # def prepare_data(self, str, timestamp='Timestamp'):
    #     # data = self.prepare_data(self._data_file, timestamp_name)
    #     data = pd.read_csv(str, sep=',')
    #     data = data.sort_values(by=timestamp, ascending=True)
    #     data['EventID'] = range(1, len(data) + 1)
    #     data.set_index('EventID', inplace=True)
    #     return data


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


    def assign_cases(self, datadict):
        solver = RecursiveBacktrackingSolver(False)
        problem = Problem(solver)
        self.declare_domains(problem, datadict, self._start_event)

        for const in self._constraints:
            # method = const['constraint']
            method = getattr(sys.modules[__name__], const['constraint'])
            ev = const['e']
            ev2 = const.get('e2')
            if ev2:
                problem.addConstraint(method(datadict, ev, ev2, self._start_event))
            else:
                problem.addConstraint(method(datadict, ev, self._start_event))

        solutions = problem.getSolution()
        return solutions

    def generate_logs(self, assignments):
        generated_data = self.data.copy()
        generated_data['SuggestedCaseID'] = list(assignments.values())

        outdir = './new_event_logs'
        filename = f"data{len(generated_data)}"
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        fullname = os.path.join(outdir, filename)
        generated_data.to_csv(fullname, sep=',')


    def generate(self, input_data = None):
        self.data = input_data # set data

        # data = self.prepare_data(self._data_file, timestamp_name)
        datadict = self.data.to_dict(orient="index")

        result = self.assign_cases(datadict)

        self.generate_logs(result)

        measures = {}
        measures["Trace-to-trace similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).trace_to_trace_similarity()
        measures["Case similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).case_similarity()
        measures["Trace-to-trace frequency similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).trace_to_trace_frequency_similarity()
        measures["Partial case similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).partial_case_similarity()
        measures["Bigram similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).bigram_similarity()
        measures["Trigram similarity"] = LogToLogCaseMeasure(datadict, result, self._case_name).trigram_similarity()
        measures["Event time deviation"] = LogToLogTimeMeasure(self._timestamp_name, datadict, result, self._case_name).event_time_deviation()
        measures["Case cycle time deviation"] = LogToLogTimeMeasure(self._timestamp_name, datadict, result, self._case_name).case_cycle_time_deviation()

        print(f"Result: {result}")
        print(f"Trace-to-trace similarity: { measures['Trace-to-trace similarity'] }")
        print(f"Case similarity: {measures['Case similarity']}")
        print(f"Trace-to-trace frequency similarity: {measures['Trace-to-trace frequency similarity']}")
        print(f"Partial case similarity: {measures['Partial case similarity']}")
        print(f"Bigram similarity: {measures['Bigram similarity']}")
        print(f"Trigram similarity: {measures['Trigram similarity']}")
        print(f"Event time deviation: {measures['Event time deviation']}")
        print(f"Case cycle time deviation: {measures['Case cycle time deviation']}")

        return result, measures
