

class LogToLogMeasure:
    def __init__(self, data, assigned_cases, case_name = 'Case', start_event = None):
        self._data = data
        self._assigned_cases = assigned_cases
        self._start_event = start_event
        self._case_name = case_name

    def get_traces(self, assignments):
        result_traces = {}
        for e, case in assignments.items():
            result_traces[case] = [e] if case not in result_traces.keys() else result_traces[case] + [e]
        return result_traces

    def init_traces(self):
        # get initial cases
        init_cases = {}
        for id, event in self._data.items():
            init_cases[id] = event[self._case_name]
        return self.get_traces(init_cases)

    def renamed_suggested_traces(self):
        traces = {}
        for case, event in self.get_traces(self._assigned_cases).items():
            traces[f"{case}_2"] = event
        return traces