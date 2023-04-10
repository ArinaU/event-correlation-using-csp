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
    def test_responded_existence_with_absence(self):
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


    def test_responded_existence_with_abrupted_event_log(self):
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
        expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 7: 'Case3',
                           4: 'Case2', 5: 'Case2', 6: 'Case1', 8: 'Case3'}
        self.assertEqual(cases, expected_result, "Incorrect cases")

    def test_response2(self):
        data = self.generate_log('A,A,B,B,C,C,A,B')

        constraints = [
            {'constraint': 'Response',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': 'Absence',
             'e': {'attr': 'Activity', 'value': 'B'}}
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

    # def test_chain_response(self):
    #     data = self.generate_log('A,B,A,B,C,C')
    #
    #     constraints = [
    #         {'constraint': 'ChainResponse',
    #          'e': {'attr': 'Activity', 'value': 'B'},
    #          'e2': {'attr': 'Activity', 'value': 'C'}},
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'B'}}
    #     ]
    #
    #     cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
    #     expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1', 6: 'Case2'}
    #     self.assertEqual(cases, expected_result, "Incorrect cases")
    #
    #
    # def test_chain_response2(self):
    #     data = self.generate_log('A,B,A,D,C,B,A,D,C,C')
    #
    #     constraints = [
    #         {'constraint': 'ChainResponse',
    #          'e': {'attr': 'Activity', 'value': 'B'},
    #          'e2': {'attr': 'Activity', 'value': 'C'}},
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'D'}},
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'B'}}
    #     ]
    #
    #     cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
    #     expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2', 5: 'Case1',
    #                        6: 'Case2', 7: 'Case3', 8: 'Case1', 9: 'Case2', 10: 'Case1'}
    #     self.assertEqual(cases, expected_result, "Incorrect cases")
    #
    #
    # def test_chain_response3(self):
    #     data = self.generate_log('A,H,A,D,E,D,G,H')
    #
    #     constraints = [
    #         {'constraint': 'ChainResponse',
    #          'e': {'attr': 'Activity', 'value': 'E'},
    #          'e2': {'attr': 'Activity', 'value': 'G'}},
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'H'}},
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'D'}},
    #         {'constraint': 'NotChainSuccession',
    #          'e': {'attr': 'Activity', 'value': 'D'},
    #          'e2': {'attr': 'Activity', 'value': 'H'}},
    #     ]
    #
    #     cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
    #     expected_result = {1: 'Case1', 2: 'Case1', 3: 'Case2', 4: 'Case2',
    #                        5: 'Case2', 6: 'Case1', 7: 'Case2', 8: 'Case2' }
    #     self.assertEqual(cases, expected_result, "Incorrect cases")
    #
    #
    # # test deadlock when ChainResponse(F, G) and ChainResponse(E, G)
    # # and ...E,F,G,G; assign G to E first
    # def test_chain_response4(self):
    #     data = self.generate_log('A,A,G,A,F,E,G,G')
    #
    #     constraints = [
    #         {'constraint': 'Absence',
    #          'e': {'attr': 'Activity', 'value': 'G'}},
    #         {'constraint': 'ChainResponse',
    #          'e': {'attr': 'Activity', 'value': 'F'},
    #          'e2': {'attr': 'Activity', 'value': 'G'}},
    #         {'constraint': 'ChainResponse',
    #          'e': {'attr': 'Activity', 'value': 'E'},
    #          'e2': {'attr': 'Activity', 'value': 'G'}}
    #     ]
    #
    #     cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)
    #     expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case1', 4: 'Case3',
    #                        5: 'Case2', 6: 'Case3', 7: 'Case2', 8: 'Case3' }
    #     self.assertEqual(cases, expected_result, "Incorrect cases")


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

        expected_result = {1: 'Case1', 2: 'Case2', 5: 'Case3', 3: 'Case1',
                           4: 'Case2', 6: 'Case1', 7: 'Case2'}
        self.assertEqual(cases, expected_result, "Incorrect cases")


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
    def test_coexistence_without_absence(self):
        data = self.generate_log('A,A,A,B,C,B')

        constraints = [
            {'constraint': 'Coexistence',
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}}
        ]

        cases = EventCorrelationEngine(self.start_event, constraints).assign_cases(data)

        expected_result = {1: 'Case1', 2: 'Case2', 3: 'Case3', 4: 'Case1', 5: 'Case1', 6: 'Case1'}
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


if __name__ == '__main__':
    unittest.main()
