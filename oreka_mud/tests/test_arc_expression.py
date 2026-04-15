"""Tests for the arc condition expression evaluator."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_schemas.arc_expression import (
    parse_expression, evaluate_expression, validate_expression,
    ArcExpressionError,
)


class TestTokenizer(unittest.TestCase):
    def test_simple_comparison_parses(self):
        # Just don't crash
        tree = parse_expression("met_maeren.state == checked")
        self.assertIsInstance(tree, dict)

    def test_string_value_parses(self):
        tree = parse_expression('met_maeren.detail.trust == "warm"')
        self.assertIsInstance(tree, dict)

    def test_number_value_parses(self):
        tree = parse_expression('met_maeren.detail.depth >= 3')
        self.assertIsInstance(tree, dict)


class TestParseErrors(unittest.TestCase):
    def test_empty_raises(self):
        with self.assertRaises(ArcExpressionError):
            parse_expression("")

    def test_garbage_raises(self):
        with self.assertRaises(ArcExpressionError):
            parse_expression("!!!! ?? @@@")

    def test_missing_value_raises(self):
        with self.assertRaises(ArcExpressionError):
            parse_expression("met_maeren.state ==")

    def test_unbalanced_parens_raises(self):
        with self.assertRaises(ArcExpressionError):
            parse_expression("(met_maeren.state == checked")


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.ctx_simple = {
            "met_maeren": {"state": "checked", "detail": {"trust": "warm"}},
            "met_kael": {"state": "unchecked", "detail": {}},
            "arc": {"status": "aware", "flags": {"key": "value"}},
        }

    # ----- Simple comparisons -----

    def test_eq_true(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.state == checked", self.ctx_simple
        ))

    def test_eq_false(self):
        self.assertFalse(evaluate_expression(
            "met_maeren.state == unchecked", self.ctx_simple
        ))

    def test_neq(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.state != unchecked", self.ctx_simple
        ))

    def test_detail_lookup(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.detail.trust == warm", self.ctx_simple
        ))

    def test_arc_status_lookup(self):
        self.assertTrue(evaluate_expression(
            "arc.status == aware", self.ctx_simple
        ))

    def test_arc_flag_lookup(self):
        self.assertTrue(evaluate_expression(
            "arc.flags.key == value", self.ctx_simple
        ))

    # ----- Logical combinations -----

    def test_and_true(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.state == checked AND met_maeren.detail.trust == warm",
            self.ctx_simple,
        ))

    def test_and_false(self):
        self.assertFalse(evaluate_expression(
            "met_maeren.state == checked AND met_maeren.detail.trust == hostile",
            self.ctx_simple,
        ))

    def test_or_true(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.state == checked OR met_kael.state == checked",
            self.ctx_simple,
        ))

    def test_or_short_circuit(self):
        # Right side has missing path; should not crash
        self.assertTrue(evaluate_expression(
            "met_maeren.state == checked OR nonexistent.state == checked",
            self.ctx_simple,
        ))

    def test_not(self):
        self.assertTrue(evaluate_expression(
            "NOT (met_kael.state == checked)", self.ctx_simple
        ))

    def test_not_with_and(self):
        self.assertTrue(evaluate_expression(
            "met_maeren.state == checked AND NOT (met_kael.state == checked)",
            self.ctx_simple,
        ))

    def test_parens_grouping(self):
        # (A OR B) AND C
        ctx = {
            "a": {"state": "checked"},
            "b": {"state": "unchecked"},
            "c": {"state": "checked"},
        }
        self.assertTrue(evaluate_expression(
            "(a.state == checked OR b.state == checked) AND c.state == checked",
            ctx,
        ))

    # ----- Missing paths -----

    def test_missing_path_evaluates_false_no_crash(self):
        self.assertFalse(evaluate_expression(
            "nonexistent.state == checked", self.ctx_simple
        ))

    def test_missing_subpath_evaluates_false(self):
        self.assertFalse(evaluate_expression(
            "met_maeren.detail.nonexistent == warm", self.ctx_simple
        ))

    def test_missing_path_with_neq(self):
        # neq against missing should be false (consistent with eq false)
        self.assertFalse(evaluate_expression(
            "nonexistent.state != checked", self.ctx_simple
        ))

    # ----- Numeric coercion -----

    def test_numeric_gte(self):
        ctx = {"x": {"detail": {"depth": 5}}}
        self.assertTrue(evaluate_expression("x.detail.depth >= 3", ctx))

    def test_numeric_lt(self):
        ctx = {"x": {"detail": {"depth": 2}}}
        self.assertTrue(evaluate_expression("x.detail.depth < 3", ctx))

    def test_numeric_string_coercion(self):
        ctx = {"x": {"detail": {"depth": "5"}}}
        self.assertTrue(evaluate_expression("x.detail.depth >= 3", ctx))

    # ----- String values -----

    def test_quoted_string(self):
        self.assertTrue(evaluate_expression(
            'met_maeren.detail.trust == "warm"', self.ctx_simple
        ))


class TestValidate(unittest.TestCase):
    def test_valid_expression(self):
        self.assertEqual(validate_expression("a.state == checked"), [])

    def test_empty_expression(self):
        errors = validate_expression("")
        self.assertTrue(len(errors) >= 1)

    def test_non_string(self):
        errors = validate_expression(123)
        self.assertTrue(len(errors) >= 1)

    def test_garbage_expression(self):
        errors = validate_expression("@@@ !!!")
        self.assertTrue(len(errors) >= 1)


if __name__ == "__main__":
    unittest.main()
