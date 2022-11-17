## Documentation and Testing for the prototype: Event Correlation Based On Constraint Satisfaction Problem


# Testing

The test model as a BPMN:

![result](Activities.png)

The model contains 2 parallel events, 1 XOR, 1 at most event, 2 loops, one of which contains another loop.


10 correlated event logs from 10 to 105 events (with the step ~10 events) using the BPMN model were generated using [BIMP simulator](https://bimp.cs.ut.ee/simulator):

*  [event log with 10 events](./event_logs/data10.csv)

*  [event log with 21 events](./event_logs/data21.csv)

*  [event log with 32 events](./event_logs/data32.csv)

*  [event log with 39 events](./event_logs/data39.csv)

*  [event log with 48 events](./event_logs/data48.csv)

*  [event log with 64 events](./event_logs/data64.csv)

*  [event log with 71 events](./event_logs/data71.csv)

*  [event log with 80 events](./event_logs/data80.csv)

*  [event log with 90 events](./event_logs/data90.csv)

*  [event log with 105 events](./event_logs/data105.csv)

The following constraints are used for the test:

```
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
        {'constraint': NotCoexistence,
         'e': {'attr': 'Activity', 'value': 'F'},
         'e2': {'attr': 'Activity', 'value': 'E'}},
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
         'e2': {'attr': 'Activity', 'value': 'I'}},
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
```

(for the last 2 logs without NotCoexistence(F, E), as these logs contain several loops, where both events are likely to happen)


The measures obtained as a result of the program:

* [event log with 10 events](./event_logs/data10.csv): 
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1', 5: 'Case1', 6: 'Case1', 7: 'Case1', 8: 'Case1', 9: 'Case1', 10: 'Case1'}```
    * Trace-to-trace similarity: `1.0`
    * Case similarity: `1.0`
    * Event time deviation: `0.0`
    * Case cycle time deviation: `0.0`

* [event log with 21 events](./event_logs/data21.csv): 
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case1', 5: 'Case2', 6: 'Case2', 7: 'Case1', 8: 'Case2', 9: 'Case1', 10: 'Case2', 11: 'Case1', 12: 'Case2', 13: 'Case1', 14: 'Case2', 15: 'Case1', 16: 'Case2', 17: 'Case1', 18: 'Case2', 19: 'Case1', 20: 'Case2', 21: 'Case2'}```
    * Trace-to-trace similarity: `0.9047619047619048`
    * Case similarity: `0.0`
    * Event time deviation: `0.03508771929824561`
    * Case cycle time deviation: `0.027189106060500783`
    
*  [event log with 32 events](./event_logs/data32.csv):
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case1', 5: 'Case2', 6: 'Case2', 7: 'Case1', 8: 'Case2', 9: 'Case1', 10: 'Case2', 11: 'Case1', 12: 'Case2', 13: 'Case2', 14: 'Case2', 15: 'Case1', 16: 'Case2', 17: 'Case1', 18: 'Case2', 19: 'Case1', 20: 'Case2', 21: 'Case1', 22: 'Case1', 23: 'Case1', 24: 'Case1', 25: 'Case1', 26: 'Case2', 27: 'Case2', 28: 'Case2', 29: 'Case2', 30: 'Case2', 31: 'Case2', 32: 'Case2'}```
    * Trace-to-trace similarity: `0.71875`
    * Case similarity: `0.0`
    * Event time deviation: `0.07142857142857142`
    * Case cycle time deviation: `0.1592035817811492`
    
*  [event log with 39 events](./event_logs/data39.csv):
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case2', 6: 'Case3', 4: 'Case1', 5: 'Case2', 7: 'Case2', 8: 'Case1', 9: 'Case3', 10: 'Case3', 11: 'Case3', 12: 'Case1', 13: 'Case2', 14: 'Case3', 15: 'Case1', 16: 'Case2', 17: 'Case3', 18: 'Case1', 19: 'Case2', 20: 'Case2', 21: 'Case1', 22: 'Case3', 23: 'Case2', 24: 'Case1', 25: 'Case3', 26: 'Case1', 27: 'Case3', 28: 'Case1', 29: 'Case1', 30: 'Case3', 31: 'Case1', 32: 'Case2', 33: 'Case2', 34: 'Case2', 35: 'Case2', 36: 'Case2', 37: 'Case2', 38: 'Case2', 39: 'Case3'}```
    * Trace-to-trace similarity: `0.8695652173913043`
    * Case similarity: `0.0`
    * Event time deviation: `0.10308641975308643`
    * Case cycle time deviation: `0.06468253010194332`
    
*  [event log with 48 events](./event_logs/data48.csv):
    * Assigned cases: ```{1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case1', 6: 'Case2', 7: 'Case1', 8: 'Case2', 9: 'Case1', 10: 'Case2', 11: 'Case1', 12: 'Case2', 13: 'Case1', 14: 'Case1', 15: 'Case1', 16: 'Case1', 17: 'Case1', 18: 'Case1', 19: 'Case1', 20: 'Case2', 21: 'Case1', 22: 'Case2', 23: 'Case1', 24: 'Case2', 25: 'Case1', 26: 'Case2', 27: 'Case1', 28: 'Case1', 29: 'Case2', 30: 'Case1', 31: 'Case1', 32: 'Case1', 33: 'Case1', 34: 'Case1', 35: 'Case1', 36: 'Case1', 37: 'Case1', 38: 'Case1', 39: 'Case1', 40: 'Case1', 41: 'Case1', 42: 'Case1', 43: 'Case1', 44: 'Case1', 45: 'Case1', 46: 'Case1', 47: 'Case1', 48: 'Case2'}```
    * Trace-to-trace similarity: `0.8518518518518519`
    * Case similarity: `0.0`
    * Event time deviation: `0.09092642673878372`
    * Case cycle time deviation: `0.12893553223388307`
    
*  [event log with 64 events](./event_logs/data64.csv):
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1', 5: 'Case2', 8: 'Case3', 6: 'Case1', 7: 'Case1', 9: 'Case1', 10: 'Case3', 11: 'Case3', 12: 'Case3', 13: 'Case1', 14: 'Case1', 15: 'Case2', 16: 'Case1', 17: 'Case1', 18: 'Case3', 19: 'Case3', 20: 'Case1', 21: 'Case2', 22: 'Case2', 23: 'Case1', 24: 'Case3', 25: 'Case2', 26: 'Case2', 27: 'Case1', 28: 'Case3', 29: 'Case2', 30: 'Case1', 31: 'Case1', 32: 'Case2', 33: 'Case2', 34: 'Case1', 35: 'Case3', 36: 'Case2', 37: 'Case2', 38: 'Case1', 39: 'Case3', 40: 'Case3', 41: 'Case1', 42: 'Case2', 43: 'Case3', 44: 'Case1', 45: 'Case1', 46: 'Case2', 47: 'Case1', 48: 'Case2', 49: 'Case2', 50: 'Case1', 51: 'Case3', 52: 'Case2', 53: 'Case1', 54: 'Case3', 55: 'Case2', 56: 'Case1', 57: 'Case1', 58: 'Case3', 59: 'Case1', 60: 'Case3', 61: 'Case1', 62: 'Case3', 63: 'Case2', 64: 'Case3'}```
    * Trace-to-trace similarity: `0.6923076923076923`
    * Case similarity: `0.0`
    * Event time deviation: `0.21509918960127553`
    * Case cycle time deviation: `0.02470644398273159`
    
*  [event log with 71 events](./event_logs/data71.csv)
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case2', 6: 'Case3', 5: 'Case2', 7: 'Case2', 8: 'Case1', 9: 'Case1', 10: 'Case1', 11: 'Case1', 12: 'Case1', 13: 'Case2', 14: 'Case3', 15: 'Case3', 16: 'Case2', 17: 'Case1', 18: 'Case1', 19: 'Case1', 20: 'Case2', 21: 'Case2', 22: 'Case1', 23: 'Case3', 24: 'Case2', 25: 'Case1', 26: 'Case3', 27: 'Case2', 28: 'Case2', 29: 'Case1', 30: 'Case2', 31: 'Case2', 32: 'Case3', 33: 'Case1', 34: 'Case1', 35: 'Case3', 36: 'Case1', 37: 'Case3', 38: 'Case3', 39: 'Case1', 40: 'Case2', 41: 'Case2', 42: 'Case1', 43: 'Case1', 44: 'Case3', 45: 'Case2', 46: 'Case3', 47: 'Case1', 48: 'Case1', 49: 'Case2', 50: 'Case3', 51: 'Case3', 52: 'Case3', 53: 'Case3', 54: 'Case2', 55: 'Case3', 56: 'Case2', 57: 'Case2', 58: 'Case3', 59: 'Case2', 60: 'Case3', 61: 'Case3', 62: 'Case1', 63: 'Case2', 64: 'Case3', 65: 'Case2', 66: 'Case3', 67: 'Case3', 68: 'Case3', 69: 'Case3', 70: 'Case3', 71: 'Case3'}```
    * Trace-to-trace similarity: `0.7948717948717949`
    * Case similarity: `0.0`
    * Event time deviation: `0.18371690475326868`
    * Case cycle time deviation: `0.06021334416744504`
    
*  [event log with 80 events](./event_logs/data80.csv)
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case1', 5: 'Case2', 6: 'Case2', 7: 'Case1', 8: 'Case2', 9: 'Case1', 10: 'Case2', 11: 'Case1', 12: 'Case2', 13: 'Case1', 14: 'Case1', 15: 'Case2', 16: 'Case1', 17: 'Case2', 18: 'Case1', 19: 'Case2', 20: 'Case2', 21: 'Case1', 22: 'Case2', 23: 'Case1', 24: 'Case1', 25: 'Case1', 26: 'Case2', 27: 'Case1', 28: 'Case1', 29: 'Case2', 30: 'Case2', 31: 'Case1', 32: 'Case2', 33: 'Case1', 34: 'Case2', 35: 'Case1', 36: 'Case2', 37: 'Case1', 38: 'Case1', 39: 'Case2', 40: 'Case1', 41: 'Case2', 42: 'Case1', 43: 'Case2', 44: 'Case2', 45: 'Case1', 46: 'Case2', 47: 'Case1', 48: 'Case2', 49: 'Case1', 50: 'Case2', 51: 'Case1', 52: 'Case1', 53: 'Case1', 54: 'Case1', 55: 'Case1', 56: 'Case1', 57: 'Case1', 58: 'Case2', 59: 'Case2', 60: 'Case1', 61: 'Case1', 62: 'Case1', 63: 'Case1', 64: 'Case1', 65: 'Case1', 66: 'Case1', 67: 'Case1', 68: 'Case2', 69: 'Case2', 70: 'Case2', 71: 'Case2', 72: 'Case1', 73: 'Case1', 74: 'Case1', 75: 'Case2', 76: 'Case2', 77: 'Case2', 78: 'Case2', 79: 'Case2', 80: 'Case2'}```
    * Trace-to-trace similarity: `0.775`
    * Case similarity: `0.0`
    * Event time deviation: `0.07286324786324785`
    * Case cycle time deviation: `0.08139534883720931`
    
*  [event log with 90 events](./event_logs/data90.csv)
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1', 5: 'Case2', 8: 'Case3', 6: 'Case1', 7: 'Case1', 9: 'Case1', 10: 'Case3', 11: 'Case2', 12: 'Case3', 13: 'Case1', 14: 'Case2', 15: 'Case2', 16: 'Case1', 17: 'Case3', 18: 'Case3', 19: 'Case1', 20: 'Case2', 21: 'Case2', 22: 'Case3', 23: 'Case1', 24: 'Case1', 25: 'Case1', 26: 'Case1', 27: 'Case2', 28: 'Case1', 29: 'Case2', 30: 'Case2', 31: 'Case2', 32: 'Case3', 33: 'Case2', 34: 'Case3', 35: 'Case2', 36: 'Case3', 37: 'Case1', 38: 'Case1', 39: 'Case2', 40: 'Case1', 41: 'Case2', 42: 'Case1', 43: 'Case2', 44: 'Case1', 45: 'Case1', 46: 'Case1', 47: 'Case1', 48: 'Case1', 49: 'Case1', 50: 'Case1', 51: 'Case1', 52: 'Case1', 53: 'Case1', 54: 'Case1', 55: 'Case1', 56: 'Case1', 57: 'Case1', 58: 'Case1', 59: 'Case1', 60: 'Case1', 61: 'Case1', 62: 'Case1', 63: 'Case1', 64: 'Case1', 65: 'Case1', 66: 'Case1', 67: 'Case1', 68: 'Case1', 69: 'Case1', 70: 'Case1', 71: 'Case1', 72: 'Case1', 73: 'Case1', 74: 'Case1', 75: 'Case1', 76: 'Case1', 77: 'Case1', 78: 'Case3', 79: 'Case3', 80: 'Case3', 81: 'Case3', 82: 'Case1', 83: 'Case1', 84: 'Case1', 85: 'Case3', 86: 'Case3', 87: 'Case3', 88: 'Case3', 89: 'Case3', 90: 'Case3'}```
    * Trace-to-trace similarity: `0.7096774193548387`
    * Case similarity: `0.0`
    * Event time deviation: `0.1094573711319604`
    * Case cycle time deviation: `0.19718264457636167`
    
*  [event log with 105 events](./event_logs/data105.csv)
    * Assigned cases: ```{1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1', 5: 'Case2', 7: 'Case3', 6: 'Case1', 8: 'Case3', 9: 'Case1', 10: 'Case3', 11: 'Case3', 12: 'Case3', 13: 'Case1', 14: 'Case1', 15: 'Case2', 16: 'Case1', 17: 'Case1', 18: 'Case3', 19: 'Case2', 20: 'Case1', 21: 'Case3', 22: 'Case1', 23: 'Case1', 24: 'Case1', 25: 'Case2', 26: 'Case2', 27: 'Case1', 28: 'Case2', 29: 'Case1', 30: 'Case3', 31: 'Case2', 32: 'Case1', 33: 'Case3', 34: 'Case2', 35: 'Case1', 36: 'Case1', 37: 'Case1', 38: 'Case3', 39: 'Case2', 40: 'Case1', 41: 'Case3', 42: 'Case1', 43: 'Case2', 44: 'Case2', 45: 'Case1', 46: 'Case1', 47: 'Case2', 48: 'Case1', 49: 'Case1', 50: 'Case2', 51: 'Case1', 52: 'Case1', 53: 'Case1', 54: 'Case2', 55: 'Case1', 56: 'Case1', 57: 'Case2', 58: 'Case2', 59: 'Case1', 60: 'Case2', 61: 'Case1', 62: 'Case1', 63: 'Case1', 64: 'Case2', 65: 'Case1', 66: 'Case1', 67: 'Case2', 68: 'Case2', 69: 'Case1', 70: 'Case2', 71: 'Case1', 72: 'Case1', 73: 'Case1', 74: 'Case2', 75: 'Case1', 76: 'Case1', 77: 'Case2', 78: 'Case2', 79: 'Case1', 80: 'Case2', 81: 'Case1', 82: 'Case1', 83: 'Case1', 84: 'Case2', 85: 'Case1', 86: 'Case1', 87: 'Case2', 88: 'Case2', 89: 'Case1', 90: 'Case2', 91: 'Case1', 92: 'Case2', 93: 'Case1', 94: 'Case2', 95: 'Case1', 96: 'Case2', 97: 'Case1', 98: 'Case1', 99: 'Case1', 100: 'Case3', 101: 'Case3', 102: 'Case3', 103: 'Case3', 104: 'Case3', 105: 'Case3'}```
    * Trace-to-trace similarity: `0.5714285714285714`
    * Case similarity: `0.0`
    * Event time deviation: `0.16122940310777795`
    * Case cycle time deviation: `0.19754554102490826`