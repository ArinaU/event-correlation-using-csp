
import textdistance
from measures.log_to_log_measure import *


class LogToLogCaseMeasure(LogToLogMeasure):

    def levenshtein_distance(self, list1, list2):
        distance = 0
        # Find the length of the longer list
        max_length = max(len(list1), len(list2))
        for i in range(max_length):
            if i < len(list1) and i < len(list2):
                # If the items are the same, continue
                if list1[i] == list2[i]:
                    continue
                # If the items are different, increment the distance
                else:
                    distance += 1
            else:
                # If one list is shorter than the other, increment the distance
                distance += 1
        return distance

    def get_tcc_pairs(self):
        # get pairs from calculating distances
        pairs = {}
        for case1, trace1 in self.init_traces().items():
            for case2, trace2 in self.suggested_traces().items():
                pairs[(case1, case2)] = self.levenshtein_distance(trace1, trace2)

        return pairs


    def trace_to_trace_similarity(self):
        init_traces = self.init_traces()
        suggested_traces = self.suggested_traces()

        pairs = self.get_tcc_pairs()

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

    def trace_to_trace_frequency_similarity(self):
        init_traces = self.init_traces()
        pairs = self.get_tcc_pairs()
        delta_total = sum([dist for case, dist in pairs.items() if case[1] == f"{case[0]}_2"])
        L2L_freq = 1 - delta_total / ( 2.0 * len(init_traces))

        return L2L_freq

    def case_similarity(self):
        init_traces = self.init_traces()
        suggested_traces = self.get_traces(self._assigned_cases)

        intersection = [k for k, v in init_traces.items() if suggested_traces.get(k) == v]
        L2L_case = len(intersection) / len(init_traces) * 1.0

        return L2L_case