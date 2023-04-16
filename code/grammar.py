import re
from collections import defaultdict
from typing import List, Tuple, Mapping


class Symbol:
    """symbols of the grammar"""

    terminal: bool
    symbol: str
    original: bool

    def __init__(self, symbol: str, original=True):
        self.terminal = not symbol.startswith("$")
        self.symbol = symbol if self.terminal else symbol[1:]
        self.original = original

    def __repr__(self):
        return ("" if self.terminal else "$") + self.symbol

    def __eq__(self, other):
        return self.symbol == other.symbol and self.terminal == other.terminal

    def __hash__(self):
        return hash(self.symbol)


class GrammarRule:
    """
    simple sequence rule.
    We don't support anything more complex;
    alternatives will have to be split into multiple sub-rules """

    lhs: Symbol
    rhs: List[Symbol]  # it's a list of Symbols

    def __init__(self, lhs: Symbol, rhs: list):
        self.lhs, self.rhs = lhs, rhs

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __repr__(self):
        return str(self.lhs) + " = " + " ".join([str(s) for s in self.rhs]) + ";"


class Grammar:
    language: str
    start_symbol: Symbol
    rules: List[GrammarRule] = []  # list of GrammarRules
    symbols: Mapping[str, Symbol] = {}  # map from strings to symbols
    # map from RHSs to the matching rules
    rule_map: Mapping[tuple, GrammarRule]
    original_rules: List[GrammarRule] = []

    """initialize a new grammar from a srgs grammar file"""

    # FIXME: maybe implement JSGF import in the future
    def __init__(self, lines, grammar_format="SRGS"):
        assert grammar_format == "SRGS", "illegal format descriptor: {}".format(
            grammar_format)
        lines = [re.sub("//.*$", "", line)
                 for line in lines]  # remove comment lines
        lines = [line.strip() for line in lines if not re.match(
            r"^ *$", line)]  # remove empty lines
        assert lines.pop(0).lower(
        ) == "#abnf v1.0 utf-8;", "maybe something is wrong with header?"
        lang = re.match(r"language\s+(\S*)\s*;", lines.pop(0).lower())
        assert lang and len(
            lang.groups()) == 1, "cannot find correct language tag: {}".format(lang)
        self.language = lang.group(0)
        for line in lines:
            match = re.match(r"((?:public)?)\s*(\$\S+)\s*=\s*(.*)\s*;", line)
            assert match and len(
                match.groups()) == 3, "cannot parse line {}".format(line)
            is_public = match.group(1) != ""
            lhs = self.get_symbol(match.group(2))
            #
            assert lhs.terminal is False, "a terminal can't produce anything {} !".format(lhs.symbol)
            rhs = [self.get_symbol(s)
                   for s in re.split(r"\s+", match.group(3))]
            rule = GrammarRule(lhs, rhs)
            self.rules.append(rule)
            if is_public:
                self.start_symbol = lhs
        self.original_rules = self.rules
        self.normalize_rules()
        self.build_rule_map()

    def build_rule_map(self):
        self.rule_map = defaultdict(lambda: [])
        for r in self.rules:
            self.rule_map[tuple(r.rhs)].append(r)

    def get_symbol(self, symbol: str):
        if symbol not in self.symbols:
            self.symbols[symbol] = Symbol(symbol)
        return self.symbols[symbol]

    def __repr__(self):
        return "#ABNF V1.0 utf-8\n" + \
            "language " + self.language + "\n" + \
            "\n".join(
                [str(r) if r.lhs != self.start_symbol else "public " + str(r) for r in self.rules])

    def is_CNF(self):
        return all([self._is_valid_CNF_rule(rule) for rule in self.rules])

    def _is_valid_CNF_rule(self, rule: GrammarRule) -> bool:
        lhs, rhs, length = rule.lhs, rule.rhs, len(rule.rhs)
        # if lhs.terminal: return False # we already assert this when reading the grammar
        if length not in (1, 2): return False
        if length == 1 and not rhs[0].terminal: return False
        if length == 2 and (rhs[0].terminal or rhs[1].terminal): return False
        return True

    def is_relaxedCNF(self):
        return all([self._is_valid_relaxed_rule(rule) for rule in self.rules])

    def _is_valid_relaxed_rule(self, rule: GrammarRule) -> bool:
        lhs, rhs, length = rule.lhs, rule.rhs, len(rule.rhs)
        if length not in (1, 2): return False
        if length == 2 and (rhs[0].terminal or rhs[1].terminal): return False
        return True

    def normalize_rules(self):
        normalized_rules = []
        for rule in self.rules:
            if self._is_valid_relaxed_rule(rule):
                normalized_rules.append(rule)
                continue
            else:
                lhs, rhs = rule.lhs, rule.rhs
                new_rules: List[GrammarRule] = []
                _rhs = []

                for s in rhs:
                    if not s.terminal:
                        _rhs.append(s)
                    else:
                        new_s = Symbol('$_' + s.symbol.capitalize(), False)
                        _rhs.append(new_s)
                        new_rules.append(GrammarRule(new_s, [s]))

                # if len(_rhs) % 2 == 1:
                #     last_s = _rhs.pop()
                #     new_rules.append(GrammarRule(Symbol('$_' + last_s.symbol, False), [last_s]))
                #
                # for i in range(0, len(_rhs), 2):
                #     first, second = _rhs[i], _rhs[i + 1]
                #     new_rules.append(GrammarRule(Symbol('$_' + first.symbol + second.symbol, False), [first, second]))

                self.split_rule(rule, new_rules)

                normalized_rules.extend(new_rules)

        self.rules = normalized_rules

    def split_rule(self, rule: GrammarRule, new_rules: List[GrammarRule]):
        if len(rule.rhs) == 2:
            new_rules.append(rule)
        else:
            left_part, right_part = rule.rhs[0], rule.rhs[1:]
            new_sym_for_right_part = Symbol("$_" + "".join([sym.symbol for sym in right_part], False))
            new_rules.append(GrammarRule(rule.lhs, [left_part, new_sym_for_right_part]))
            self.split_rule(GrammarRule(new_sym_for_right_part, right_part))

