
import pandas as pd
from datetime import datetime

class EventLogGenerationMixin(object):
    """ this class adds event log generation
    """

    def generate_log(self, trace):
        list = trace.split(",")
        dict = {}
        timestamps = pd.date_range(datetime.today(), periods=len(list), freq='5T').tolist()

        for ind, val in enumerate(list, 1):
            dict[ind] = {
                'Activity': val,
                'Timestamp': str(timestamps[ind - 1]),
                'UserID': ind
            }
        return dict