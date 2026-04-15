"""
Expression evaluator for ai_persona.arc_reactions[*].when conditions.

Grammar (in informal EBNF):

    expr     := or_expr
    or_expr  := and_expr ("OR" and_expr)*
    and_expr := not_expr ("AND" not_expr)*
    not_expr := "NOT" not_expr | atom
    atom     := "(" expr ")" | comparison
    comparison := path operator value
    operator := "==" | "!=" | ">=" | "<=" | ">" | "<"
    path     := IDENT ("." IDENT)*
    value    := IDENT | NUMBER | STRING

Supported left-hand paths:
    <item_id>.state                           — checklist item state
    <item_id>.detail.<key>                    — checklist item detail value
    arc.status                                — the arc's own status
    arc.flags.<key>                           — arc-level flag

Examples:
    met_maeren.state == checked
    met_maeren.state == checked AND met_maeren.detail.trust == warm
    NOT (met_joe.state == checked) AND arc.status != resolved
    learned_x.state == detailed AND learned_x.detail.depth >= 3

No `eval()`. No regex. Pure parser, evaluator is type-coerced for ints/floats
where both sides parse as numbers.
"""

import re
from typing import Optional


class ArcExpressionError(ValueError):
    """Raised when an expression cannot be parsed."""


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

_TOKEN_REGEX = re.compile(
    r'\s*(?:'
    r'(?P<LPAREN>\()|'
    r'(?P<RPAREN>\))|'
    r'(?P<OP>==|!=|>=|<=|>|<)|'
    r'(?P<STRING>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')|'
    r'(?P<NUMBER>-?\d+\.\d+|-?\d+)|'
    r'(?P<IDENT>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)'
    r')'
)


def _tokenize(expr: str) -> list:
    """Return list of (type, value) tuples, or raise ArcExpressionError."""
    tokens = []
    pos = 0
    expr = expr.strip()
    while pos < len(expr):
        m = _TOKEN_REGEX.match(expr, pos)
        if not m or m.end() == pos:
            raise ArcExpressionError(
                f"Unexpected character at position {pos}: {expr[pos]!r}"
            )
        for tok_type in ("LPAREN", "RPAREN", "OP", "STRING", "NUMBER", "IDENT"):
            val = m.group(tok_type)
            if val is not None:
                # Promote keyword-like idents to logical ops
                if tok_type == "IDENT" and val.upper() in ("AND", "OR", "NOT"):
                    tokens.append(("LOGIC", val.upper()))
                elif tok_type == "STRING":
                    # Strip quotes; unescape backslashes
                    inner = val[1:-1].replace('\\"', '"').replace("\\'", "'")
                    tokens.append(("STRING", inner))
                else:
                    tokens.append((tok_type, val))
                break
        pos = m.end()
    return tokens


# ---------------------------------------------------------------------------
# Parser — recursive descent producing a tree of dicts
# ---------------------------------------------------------------------------

def _parse(tokens: list) -> dict:
    parser = _Parser(tokens)
    tree = parser.parse_or()
    if parser.pos < len(parser.tokens):
        unexpected = parser.tokens[parser.pos]
        raise ArcExpressionError(f"Unexpected token after expression: {unexpected}")
    return tree


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None, expected_value=None):
        if self.pos >= len(self.tokens):
            raise ArcExpressionError("Unexpected end of expression")
        tok = self.tokens[self.pos]
        if expected_type and tok[0] != expected_type:
            raise ArcExpressionError(f"Expected {expected_type}, got {tok}")
        if expected_value and tok[1] != expected_value:
            raise ArcExpressionError(f"Expected {expected_value!r}, got {tok[1]!r}")
        self.pos += 1
        return tok

    def parse_or(self):
        node = self.parse_and()
        while self.peek() == ("LOGIC", "OR"):
            self.consume()
            right = self.parse_and()
            node = {"op": "OR", "left": node, "right": right}
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.peek() == ("LOGIC", "AND"):
            self.consume()
            right = self.parse_not()
            node = {"op": "AND", "left": node, "right": right}
        return node

    def parse_not(self):
        if self.peek() == ("LOGIC", "NOT"):
            self.consume()
            inner = self.parse_not()
            return {"op": "NOT", "inner": inner}
        return self.parse_atom()

    def parse_atom(self):
        tok = self.peek()
        if tok is None:
            raise ArcExpressionError("Unexpected end of expression in atom")
        if tok[0] == "LPAREN":
            self.consume("LPAREN")
            inner = self.parse_or()
            self.consume("RPAREN")
            return inner
        return self.parse_comparison()

    def parse_comparison(self):
        # path operator value
        path_tok = self.consume("IDENT")
        op_tok = self.consume("OP")
        val_tok = self.peek()
        if val_tok is None:
            raise ArcExpressionError("Comparison missing right-hand value")
        if val_tok[0] not in ("IDENT", "NUMBER", "STRING"):
            raise ArcExpressionError(f"Invalid right-hand value: {val_tok}")
        self.consume()
        return {
            "op": "CMP",
            "operator": op_tok[1],
            "path": path_tok[1],
            "value": val_tok[1],
            "value_type": val_tok[0],
        }


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def _resolve_path(path: str, context: dict):
    """Resolve a dotted path against the context dict.

    Returns the raw value, or a sentinel-string ("__MISSING__") if not found.
    Missing paths must NOT crash the evaluation — they evaluate to false in
    comparisons (per BUILDOUT_ARC_MODULE §2.2 acceptance criteria).
    """
    parts = path.split(".")
    node = context
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return _MISSING
    return node


_MISSING = object()


def _coerce_for_comparison(left, right_str: str, right_type: str):
    """Try to coerce both sides to numbers if either looks numeric."""
    if right_type == "NUMBER":
        try:
            right_val = float(right_str) if "." in right_str else int(right_str)
        except ValueError:
            right_val = right_str
        # Coerce left to same type if possible
        if isinstance(left, (int, float)):
            return left, right_val
        if isinstance(left, str):
            try:
                left_val = float(left) if "." in left else int(left)
                return left_val, right_val
            except ValueError:
                return left, right_val
        return left, right_val
    if right_type == "STRING":
        return left, right_str
    # IDENT — treat as bare-word string
    return left, right_str


def _evaluate_node(node: dict, context: dict) -> bool:
    op = node.get("op")

    if op == "OR":
        return _evaluate_node(node["left"], context) or _evaluate_node(node["right"], context)
    if op == "AND":
        return _evaluate_node(node["left"], context) and _evaluate_node(node["right"], context)
    if op == "NOT":
        return not _evaluate_node(node["inner"], context)
    if op == "CMP":
        left = _resolve_path(node["path"], context)
        if left is _MISSING:
            return False
        left_v, right_v = _coerce_for_comparison(left, node["value"], node["value_type"])
        operator = node["operator"]
        try:
            if operator == "==":
                return left_v == right_v
            if operator == "!=":
                return left_v != right_v
            if operator == ">":
                return left_v > right_v
            if operator == "<":
                return left_v < right_v
            if operator == ">=":
                return left_v >= right_v
            if operator == "<=":
                return left_v <= right_v
        except TypeError:
            return False
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_expression(expr: str) -> dict:
    """Parse an expression string into an AST. Raises ArcExpressionError on failure."""
    if not isinstance(expr, str) or not expr.strip():
        raise ArcExpressionError("Expression must be a non-empty string")
    tokens = _tokenize(expr)
    if not tokens:
        raise ArcExpressionError("Expression has no tokens")
    return _parse(tokens)


def evaluate_expression(expr: str, context: dict) -> bool:
    """Parse + evaluate an expression. Returns False for any parse/runtime error."""
    try:
        tree = parse_expression(expr)
        return bool(_evaluate_node(tree, context or {}))
    except ArcExpressionError:
        return False
    except Exception:
        return False


def validate_expression(expr: str) -> list:
    """Return list of error strings; empty list means parses cleanly."""
    if not isinstance(expr, str):
        return [f"expression must be string, got {type(expr).__name__}"]
    if not expr.strip():
        return ["expression is empty"]
    try:
        parse_expression(expr)
        return []
    except ArcExpressionError as e:
        return [str(e)]
