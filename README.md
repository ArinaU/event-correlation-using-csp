## Documentation for the prototype developed for the Master thesis: Event Correlation Based On Constraint Satisfaction Problem


### Current State

The program starts from executing the function:
`def get_matrix()`

The result returned by this function is a matrix where columns are cases, rows are events assigned to one case.

First, it reads the event log in data.csv in `raw_df`:

`raw_df = pd.read_csv('data.csv', sep=';')`

`n_of_events` is the number of events in the event log.

`n_of_cases` is the number of cases defined by a user (hardcoded for now)


Different constraints for each case: 
```
constraints = {0: {'attrs': ['Activity', 'Activity'], 'vals': ['A', 'B'], 'operator': "<"},
               1: {'attrs': ['Activity', 'UserID'], 'vals': ['B', 2], 'operator': "<"},
               2: {'attrs': ['Activity'], 'vals': 'C', 'operator': "!="}}
```
(Hardcoded and this part schould be changed, if for the master thesis the number of cases should be undefined and determined as a result of the program, then this decision is invalid, everything needs to be redone.)

`temp_df` is a temporary dataframe into which the current event for each case is added at each iteration.
This is done in order to check for each column (for each case) whether its constraint conditions are still met with this new event.

In the current prototype, _the variables_ are the events, and _the domain_ for each variable is the cases. (Should also be changed later)

Initializes variables:

`problem.addVariable('Cases', [i for i in range(n_of_cases)])`

Initializes constraints:

`problem.addConstraint(MyConstraint(temp_df, constraints), ['Cases'])`

`MyConstraint` is a subclass of the `Constraint` class from the `python-constraint` library.

In `MyConstraint`:
* `data` - is `temp_df`, a temporary dataframe
* `constraints` - are individual constraints for each case

`column = data[case]` - is a column of the current case (all previous events assigned to this case)

`flag = True` - if flag is False at any time of execution, then the constraint for the case is not satisfied

This is the condition for when the very 1st event in the event log is added:

```
if len(column) < 2:
    cond = generate_condition(column[0], constraints=constraints[case])
    flag = cond()
```

From `itertools` library: for `permutations('AB', 2)` returns r-length tuples, all possible orderings, no repeated elements (e.g. for 'AB' returns 'AB' and 'BA'): 
```
for x, y in itertools.permutations(column, 2):
```

`generate_condition(*args, **kwargs)` - generates a condition with `eval()` and executes it returning a boolean value, whether this condition is satisfied.


On line 17 `if len(args) == 2:` - checks whether it is a binary constraint.


When:
* `constraints` is equal to `{'attrs': ['Activity', 'Activity'], 'vals': ['A', 'B'], 'operator': '<'}`;
* `x` is equal to `{'EventID': 1, 'Activity': 'B', 'Timestamp': '2022-01-01 11:01:58', 'UserID': 1}`;
* `y` is equal `{'EventID': 2, 'Activity': 'A', 'Timestamp': '2022-01-01 11:10:58', 'UserID': 1}`

This expression 
```
if (x[attr] == constraints['vals'][0] and y[attr2] == constraints['vals'][1]) or (
                        y[attr] == constraints['vals'][0] and x[attr2] == constraints['vals'][1]):
```

evaluates to:
```
if ('B' == 'A' and 'A' == 'B') or ('A' == 'A' and 'B' == 'B'):
```



















