import unittest
from testutils import EventLogGenerationMixin

from constraints.existence_constraints import *
from constraints.relation_constraints import *
from constraints.negative_relation_constraints import *
from constraints.mutual_relation_constraints import *
from event_correlation_engine import *


class TestExistenceConstraints(unittest.TestCase, EventLogGenerationMixin):

    def setUp(self):
        self.start_event = {'attr': 'Activity', 'value': 'A'}
        self.required_event = {'attr': 'Activity', 'value': 'B'}

    def test_absence_with_1_req_event(self):
        data = self.generate_log('A,B,A,B,C')
        constraints = [{'constraint': 'Absence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        result = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1'}
        self.assertEqual(result, expected_result, "Incorrect cases")

    def test_absence_with_2_req_events(self):
        data = self.generate_log('A,B,A,B,B')
        constraints = [{'constraint': 'Absence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        self.assertIsNone(cases, "Incorrect cases")

    def test_absence_with_no_req_events_for_1_case(self):
        data = self.generate_log('A,B,A')
        constraints = [{'constraint': 'Absence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_existence_with_1_req_event(self):
        data = self.generate_log('A,B,A,B,C')
        constraints = [{'constraint': 'Existence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_existence_with_2_req_events(self):
        data = self.generate_log('A,B,A,B,B,C')
        constraints = [{'constraint': 'Existence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1', 6: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_existence_with_no_req_events_for_1_case(self):
        data = self.generate_log('A,B,A,C')
        constraints = [{'constraint': 'Existence',
                             'e': {'attr': 'Activity', 'value': 'B'}}]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        self.assertIsNone(cases, "Incorrect cases")



class TestRelationConstraints(unittest.TestCase, EventLogGenerationMixin):

    def setUp(self):
        self.start_event = {'attr': 'Activity', 'value': 'A'}

    # If A occurs, then B occurs: <B, C, A, A, C>, <B, C, C> NOT: <A, C, C>
    # If B occurs, then C occurs
    def test_responded_existence(self):
        data = self.generate_log('A,C,B,A,A,B,C,C,B')

        constraints = [
            {'constraint': 'RespondedExistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case2',
                           5: 'Case3', 6: 'Case2', 7: 'Case2', 8: 'Case3', 9: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_responded_existence2(self):
        data = self.generate_log('A,C,С')

        constraints = [
            {'constraint': 'RespondedExistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1' }
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_responded_existence3(self):
        # abrupted event log
        data = self.generate_log('A,A,B')

        constraints = [
            {'constraint': 'RespondedExistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_responded_existence4(self):
        # abrupted event log
        data = self.generate_log('A,B,A,C,C,B')

        constraints = [
            {'constraint': 'RespondedExistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case1', 5: 'Case2', 6: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # If B occurs, then C occurs after B
    def test_response(self):
        data = self.generate_log('A,C,A,B,C,C,A,B')

        constraints = [
            {'constraint': 'Response',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2',
                           5: 'Case2', 6: 'Case1', 7: 'Case3', 8: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_response2(self):
        data = self.generate_log('A,A,B,B,C,C,A,C')

        constraints = [
            {'constraint': 'Response',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 7: 'Case3', 3: 'Case1',
                           4: 'Case2', 5: 'Case1', 6: 'Case2', 8: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_precedence(self):
        # B at the end is assigned to Case1, coz C,B,C is allowed (C after B preceded)
        data = self.generate_log('A,A,B,B,C,C,A,B')

        constraints = [
            {'constraint': 'Precedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 7: 'Case3', 3: 'Case1',
                           4: 'Case2', 5: 'Case1', 6: 'Case2', 8: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_precedence2(self):
        # B should be reassigned for 'Absence'(C) to work
        data = self.generate_log('A,A,B,B,A,B,C,C,C')

        constraints = [
            {'constraint': 'Precedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 5: 'Case3', 3: 'Case1',
                           4: 'Case2', 6: 'Case3', 7: 'Case1', 8: 'Case2', 9: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_precedence3(self):
        data = self.generate_log('A,C,C')

        constraints = [
            {'constraint': 'Precedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        # expected_result = {1: 'Case1', 2: 'Case2', 5: 'Case3', 3: 'Case1',
        #                    4: 'Case2', 6: 'Case3', 7: 'Case1', 8: 'Case2', 9: 'Case3'}
        self.assertIsNone(cases, "Incorrect cases")

    def test_chain_response(self):
        data = self.generate_log('A,B,A,B,C,C')

        constraints = [
            {'constraint': 'ChainResponse',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1', 6: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_chain_response2(self):
        data = self.generate_log('A,B,A,D,C,B,A,D,C,C')

        constraints = [
            {'constraint': 'ChainResponse',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1',
                           6: 'Case2', 7: 'Case3', 8: 'Case3', 9: 'Case2', 10: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_chain_response3(self):
        data = self.generate_log('A,H,A,D,E,D,G,H')

        constraints = [
            {'constraint': 'ChainResponse',
             'e': {'attr': 'Activity', 'value': 'E'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'H'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': 'NotChainSuccession',
             'e': {'attr': 'Activity', 'value': 'D'},
             'e2': {'attr': 'Activity', 'value': 'H'}},
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2',
                           5: 'Case2', 6: 'Case1', 7: 'Case2', 8: 'Case2' }
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # test deadlock when ChainResponse(F, G) and ChainResponse(E, G)
    # and ...E,F,G,G; assign G to E first
    def test_chain_response4(self):
        data = self.generate_log('A,A,G,A,F,E,G,G')

        constraints = [
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': 'ChainResponse',
             'e': {'attr': 'Activity', 'value': 'F'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': 'ChainResponse',
             'e': {'attr': 'Activity', 'value': 'E'},
             'e2': {'attr': 'Activity', 'value': 'G'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case3',
                           5: 'Case2', 6: 'Case3', 7: 'Case2', 8: 'Case3' }
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_chain_precedence(self):
        data = self.generate_log('A,A,B,B,C,C')

        constraints = [
            {'constraint': 'ChainPrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case1', 6: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_chain_precedence2(self):
        data = self.generate_log('A,B,A,D,B,C,D,C')

        constraints = [
            {'constraint': 'ChainPrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2',
                           5: 'Case2', 6: 'Case1', 7: 'Case1', 8: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_chain_precedence3(self):
        data = self.generate_log('A,H,A,D,B,D,C,H')

        constraints = [
            {'constraint': 'ChainPrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'H'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': 'NotChainSuccession',
             'e': {'attr': 'Activity', 'value': 'D'},
             'e2': {'attr': 'Activity', 'value': 'H'}},
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2',
                           5: 'Case2', 6: 'Case1', 7: 'Case2', 8: 'Case2' }
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # If B occurs, then C occurs afterwards, before B recurs
    def test_alternate_response(self):
        data = self.generate_log('A,A,B,D,C,A,B,C,B')

        constraints = [
            {'constraint': 'AlternateResponse',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 6: 'Case3', 3: 'Case1',
                           4: 'Case1', 5: 'Case1', 7: 'Case2', 8: 'Case2', 9: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_alternate_response(self):
        data = self.generate_log('A,A,B,B,D,C,A,B,C')

        constraints = [
            {'constraint': 'AlternateResponse',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2',
                           5: 'Case1', 6: 'Case1', 7: 'Case3', 8: 'Case3', 9: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_alternate_response2(self):
        data = self.generate_log('A,A,B,B,C')

        constraints = [
            {'constraint': 'AlternateResponse',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_alternate_precedence(self):
        data = self.generate_log('A,A,B,B,C,C')

        constraints = [
            {'constraint': 'AlternatePrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case1', 6: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_alternate_precedence2(self):
        data = self.generate_log('A,B,C,C')

        constraints = [
            {'constraint': 'AlternatePrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = None
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_alternate_precedence3(self):
        data = self.generate_log('A,C,C')

        constraints = [
            {'constraint': 'AlternatePrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        self.assertIsNone(cases, "Incorrect cases")

    def test_alternate_precedence4(self):
        data = self.generate_log('A,B,C,B,C,A')

        constraints = [
            {'constraint': 'AlternatePrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1', 5: 'Case1', 6: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_alternate_precedence5(self):
        data = self.generate_log('A,B,B,C,B,C,A,B,C')

        constraints = [
            {'constraint': 'AlternatePrecedence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Existence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case1',
                           5: 'Case1', 6: 'Case1', 7: 'Case2', 8: 'Case2', 9: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


class TestNegativeRelationConstraints(unittest.TestCase, EventLogGenerationMixin):

    def setUp(self):
        self.start_event = {'attr': 'Activity', 'value': 'A'}


    # A and B never occur together: <C, C, A, C>, NOT: <B, C, A, C>
    def test_not_coexistence(self):
        data = self.generate_log('A,A,A,B,C,B')

        constraints = [
            {'constraint': 'NotCoexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case3', 4: 'Case1', 5: 'Case2', 6: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_not_coexistence2(self):
        data = self.generate_log('A,A,C,B,A,C,B')

        constraints = [
            {'constraint': 'NotCoexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'C'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2',
                           5: 'Case3', 6: 'Case3', 7: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # B cannot occur after A: [^A]*(A[^B]*)* <B, B, C, A, A>, <B, B, C>, <A, A, C>
    def test_not_succession(self):
        data = self.generate_log('A,A,B,B,A,C,C,C')

        constraints = [
            {'constraint': 'NotSuccession',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2',
                           5: 'Case3', 6: 'Case3', 7: 'Case3', 8: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_not_succession2(self):
        data = self.generate_log('A,A,C,B,C,A,B,C')

        constraints = [
            {'constraint': 'NotSuccession',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]
        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case1',
                           5: 'Case2', 6: 'Case3', 7: 'Case2', 8: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # A and B occur if and only if no B occurs immediately after A
    def test_not_chain_succession(self):
        data = self.generate_log('A,A,B,B,A,C,C')

        constraints = [
            {'constraint': 'NotChainSuccession',
             'e': {'attr': 'Activity', 'value': 'A'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2',
                           5: 'Case3', 6: 'Case1', 7: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_not_chain_succession2(self):
        data = self.generate_log('A,A,C,B,C,D,C')

        constraints = [
            {'constraint': 'NotChainSuccession',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case1',
                           5: 'Case2', 6: 'Case1', 7: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


class TestMutualRelationConstraints(unittest.TestCase, EventLogGenerationMixin):

    def setUp(self):
        self.start_event = {'attr': 'Activity', 'value': 'A'}

    def test_coexistence(self):
        data = self.generate_log('A,A,A,B,C,B,C,C,C')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case3', 4: 'Case1',
                           5: 'Case1', 6: 'Case2', 7: 'Case2', 8: 'Case1', 9: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    # plain simple test, 2 B's and 1 C
    def test_coexistence2(self):
        data = self.generate_log('A,A,A,B,C,B')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case3', 4: 'Case1', 5: 'Case1', 6: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_coexistence3(self):
        data = self.generate_log('A,A,C,C')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_coexistence4(self):
        data = self.generate_log('A,C,B,A,C')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case2', 5: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_coexistence5(self):
        data = self.generate_log('A,C,B,A,C')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case1', 4: 'Case2', 5: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_coexistence6(self):
        data = self.generate_log('A,A,B,C,C,A,B,C,B')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case1', 5: 'Case2',
                           6: 'Case3', 7: 'Case2', 8: 'Case3', 9: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


class TestCompoundConstraints(unittest.TestCase, EventLogGenerationMixin):

    def setUp(self):
        self.start_event = {'attr': 'Activity', 'value': 'A'}

    def test_existence_not_coexistence_2_chain_precedences(self):
        data = self.generate_log('A,A,B,C,A,C,A,A,B,D,C,D,E,E,F,F')

        constraints = [{'constraint': 'Existence',
                        'e': {'attr': 'Activity', 'value': 'A'}},
                       {'constraint': 'NotCoexistence',
                        'e': {'attr': 'Activity', 'value': 'B'},
                        'e2': {'attr': 'Activity', 'value': 'C'}},
                       {'constraint': 'ChainPrecedence',
                        'e': {'attr': 'Activity', 'value': 'A'},
                        'e2': {'attr': 'Activity', 'value': 'C'}},
                       {'constraint': 'ChainPrecedence',
                        'e': {'attr': 'Activity', 'value': 'A'},
                        'e2': {'attr': 'Activity', 'value': 'B'}}
                       ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 5: 'Case3', 7: 'Case4', 8: 'Case5', 3: 'Case1',
                           4: 'Case2', 6: 'Case3', 9: 'Case4', 10: 'Case1', 11: 'Case5',
                           12: 'Case1', 13: 'Case1', 14: 'Case1', 15: 'Case1', 16: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_all(self):
        data = self.generate_log('A,B,A,C,B,C,D,D,F,F,G,G,H,H,I,I,J,J,L,K,L')

        constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "K"},
             "e2": {"attr": "Activity", "value": "L"}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case3', 6: 'Case3',
                           7: 'Case4', 8: 'Case5', 9: 'Case4', 10: 'Case1', 11: 'Case5', 12: 'Case1',
                           13: 'Case4', 14: 'Case5', 15: 'Case4', 16: 'Case1', 17: 'Case5', 18: 'Case1',
                           19: 'Case1', 20: 'Case5', 21: 'Case1'
                           }
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_all2(self):
        data = self.generate_log('A,B,A,C,B,C,D,D,F,F,G,G,H,H,I,I,J,J,L,K,L')

        constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "A"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "G"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "I"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "J"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "A"},
             "e2": {"attr": "Activity", "value": "B"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "A"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "NotChainSuccession",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "NotSuccession",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case3', 6: 'Case3',
                           7: 'Case4', 8: 'Case5', 9: 'Case4', 10: 'Case1', 11: 'Case5', 12: 'Case1',
                           13: 'Case4', 14: 'Case5', 15: 'Case4', 16: 'Case1', 17: 'Case5', 18: 'Case1',
                           19: 'Case1', 20: 'Case5', 21: 'Case1'
                           }
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_all3(self):
        data = self.generate_log("A,A,C,C,B,B,D,D,F,E,G,G")

        constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "A"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "G"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case3', 6: 'Case3',
                           7: 'Case4', 8: 'Case5', 9: 'Case4', 10: 'Case1', 11: 'Case5', 12: 'Case1'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_all4(self):
        data = self.generate_log("A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I,D,C,B,E,D,G,F,H,G,I,C,B,J,L")

        constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "A"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "G"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "I"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}}
            # {"constraint": "Precedence",
            #  "e": {"attr": "Activity", "value": "G"},
            #  "e2": {"attr": "Activity", "value": "H"}},
            # {"constraint": "Precedence",
            #  "e": {"attr": "Activity", "value": "J"},
            #  "e2": {"attr": "Activity", "value": "K"}},
            # {"constraint": "Coexistence",
            #  "e": {"attr": "Activity", "value": "B"},
            #  "e2": {"attr": "Activity", "value": "C"}},
            # {"constraint": "ChainResponse",
            #  "e": {"attr": "Activity", "value": "F"},
            #  "e2": {"attr": "Activity", "value": "G"}},
            # {"constraint": "ChainResponse",
            #  "e": {"attr": "Activity", "value": "E"},
            #  "e2": {"attr": "Activity", "value": "G"}}
            # ,
            # {"constraint": "ChainPrecedence",
            #  "e": {"attr": "Activity", "value": "G"},
            #  "e2": {"attr": "Activity", "value": "H"}},
            # {"constraint": "ChainPrecedence",
            #  "e": {"attr": "Activity", "value": "I"},
            #  "e2": {"attr": "Activity", "value": "J"}},
            # {"constraint": "NotChainSuccession",
            #  "e": {"attr": "Activity", "value": "D"},
            #  "e2": {"attr": "Activity", "value": "G"}},
            # {"constraint": "NotSuccession",
            #  "e": {"attr": "Activity", "value": "J"},
            #  "e2": {"attr": "Activity", "value": "I"}},
            # {"constraint": "ChainPrecedence",
            #  "e": {"attr": "Activity", "value": "J"},
            #  "e2": {"attr": "Activity", "value": "K"}},
            # {"constraint": "RespondedExistence",
            #  "e": {"attr": "Activity", "value": "F"},
            #  "e2": {"attr": "Activity", "value": "G"}},
            # {"constraint": "RespondedExistence",
            #  "e": {"attr": "Activity", "value": "E"},
            #  "e2": {"attr": "Activity", "value": "G"}},
            # {"constraint": "RespondedExistence",
            #  "e": {"attr": "Activity", "value": "K"},
            #  "e2": {"attr": "Activity", "value": "L"}},
            # {"constraint": "AlternatePrecedence",
            #  "e": {"attr": "Activity", "value": "H"},
            #  "e2": {"attr": "Activity", "value": "I"}},
            # {"constraint": "AlternatePrecedence",
            #  "e": {"attr": "Activity", "value": "G"},
            #  "e2": {"attr": "Activity", "value": "H"}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case3', 6: 'Case3',
                           7: 'Case4', 8: 'Case5', 9: 'Case4', 10: 'Case1', 11: 'Case5', 12: 'Case1',
                           13: 'Case4', 14: 'Case5', 15: 'Case4', 16: 'Case1', 17: 'Case5', 18: 'Case1',
                           19: 'Case1', 20: 'Case5', 21: 'Case1', 22: 'Case4', 23: 'Case5', 24: 'Case4',
                           25: 'Case1', 26: 'Case5', 27: 'Case1', 28: 'Case1', 29: 'Case5', 30: 'Case1'}

        self.assertEqual(cases, expected_result, "Incorrect cases")


    def test_all5(self):
        data = self.generate_log("A,A,C,C,B,B,D,D,F,E,G,G,H,C,B,I,D,\
        C,B,E,D,G,F,H,G,I,C,B,J,L,D,F,G,C,B,D,F,G,C,B,D,F,G,H,I,J,K,L")

        constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "A"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "G"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "I"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}}
            ,
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "NotChainSuccession",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "NotSuccession",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "K"},
             "e2": {"attr": "Activity", "value": "L"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case2', 5: 'Case3', 6: 'Case3',
                           7: 'Case4', 8: 'Case5', 9: 'Case4', 10: 'Case1', 11: 'Case5', 12: 'Case1',
                           13: 'Case4', 14: 'Case5', 15: 'Case4', 16: 'Case1', 17: 'Case5', 18: 'Case1',
                           19: 'Case1', 20: 'Case5', 21: 'Case1', 22: 'Case4', 23: 'Case5', 24: 'Case4',
                           25: 'Case1', 26: 'Case5', 27: 'Case1', 28: 'Case1', 29: 'Case5', 30: 'Case1',
                           31: 'Case1', 32: 'Case5', 33: 'Case1', 34: 'Case1', 35: 'Case5', 36: 'Case1',
                           37: 'Case1', 38: 'Case5', 39: 'Case1', 40: 'Case1', 41: 'Case5', 42: 'Case1',
                           43: 'Case1', 44: 'Case5', 45: 'Case1', 46: 'Case1', 47: 'Case5', 48: 'Case1'
                           }

        self.assertEqual(cases, expected_result, "Incorrect cases")



if __name__ == '__main__':
    unittest.main()
