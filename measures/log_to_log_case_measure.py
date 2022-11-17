
import textdistance
from measures.log_to_log_measure import *


class LogToLogCaseMeasure(LogToLogMeasure):

    def trace_to_trace_similarity(self):
        init_traces = self.init_traces()
        suggested_traces = self.renamed_suggested_traces()
        levenshtein = textdistance.Levenshtein(external=False)

        # get pairs from calculating distances
        pairs = {}
        for case1, trace1 in init_traces.items():
            for case2, trace2 in suggested_traces.items():
                pairs[(case1, case2)] = levenshtein(trace1, trace2)

        min_value = min(pairs.values())
        min_distances = [k for k in pairs if pairs[k] == min_value]

        numerator = sum([pairs[pair] for pair in min_distances])

        denumerator = 0
        for pair in min_distances:
            trace1 = init_traces.get(pair[0]) or suggested_traces.get(pair[0])
            trace2 = init_traces.get(pair[1]) or suggested_traces.get(pair[1])
            denumerator += len(trace1) + len(trace2)

        L2L_trace = 1 - numerator/float(denumerator)

        return L2L_trace


    def case_similarity(self):
        init_traces = self.init_traces()
        suggested_traces = self.get_traces(self._assigned_cases)

        intersection = [k for k, v in init_traces.items() if suggested_traces.get(k) == v]
        L2L_case = len(intersection) / len(init_traces) * 1.0

        return L2L_case