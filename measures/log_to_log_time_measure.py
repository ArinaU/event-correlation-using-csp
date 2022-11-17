
from measures.log_to_log_measure import *
from datetime import datetime
from math import fabs


class LogToLogTimeMeasure(LogToLogMeasure):

    def __init__(self, timestamp, *args):
        super(LogToLogTimeMeasure, self).__init__(*args)
        self._timestamp = timestamp

    def get_event_times(self, traces):
        timestamp = self._timestamp
        event_times = {}

        for case, trace in traces.items():
            for ind, event in enumerate(trace):
                if ind > 0:
                    prev_event = trace[ind-1]
                    t_start = datetime.strptime(self._data[prev_event][timestamp], '%Y-%m-%d %H:%M:%S.%f')
                    t_end = datetime.strptime(self._data[event][timestamp], '%Y-%m-%d %H:%M:%S.%f')
                    event_times[event] = (t_end - t_start).total_seconds() / 60.0

        return event_times

    def event_time_deviation(self):
        init_traces = self.init_traces()
        suggested_traces = self.renamed_suggested_traces()
        init_ets = self.get_event_times(init_traces)
        suggested_ets = self.get_event_times(suggested_traces)
        numerator = 0

        for event, et in init_ets.items():
            numerator += fabs(init_ets[event] - suggested_ets[event]) / (fabs(init_ets[event]) + fabs(suggested_ets[event])) * 1.0

        denumerator = len(self._data) - len(init_traces)

        return (numerator / denumerator * 1.0)


    def get_cycle_times(self, traces):
        timestamp = self._timestamp
        cycle_times = {}

        for case, trace in traces.items():
            t_start = datetime.strptime(self._data[trace[0]][timestamp], '%Y-%m-%d %H:%M:%S.%f')
            t_end = datetime.strptime(self._data[trace[-1]][timestamp], '%Y-%m-%d %H:%M:%S.%f')
            cycle_times[case] = (t_end - t_start).total_seconds() / 60.0

        return cycle_times


    def case_cycle_time_deviation(self):
        init_traces = self.init_traces()

        suggested_traces = {}
        i = 1
        for case, event in self.get_traces(self._assigned_cases).items():
            suggested_traces[f"{case}"] = event
            i += 1

        init_cts = self.get_cycle_times(init_traces)
        suggested_cts = self.get_cycle_times(suggested_traces)

        summ = 0
        for case, et in init_cts.items():
            summ+= fabs(init_cts[case] - suggested_cts[case]) / (fabs(init_cts[case]) + fabs(suggested_cts[case])) * 1.0

        return summ / len(init_cts) * 1.0
