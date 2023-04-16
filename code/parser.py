from grammar import *
from parse import *
from typing import List, Set


def is_in_language(words: list, grammar: Grammar) -> bool:
    # raise NotImplementedError  # TODO: in the beginning, this is your job.
    # it is easier to start out with a parser that merely
    # checks if the sentence is in the language at all (without returning
    # the derivations).
    # eventually, once you have implemented parse() below,
    # you can simply write
    return len(parse(words, grammar)) > 0


def parse(words: list, grammar: Grammar) -> list:
    """
    parses the list of words with grammar and returns the (possibly empty) list
    of possible parses. The ordering of possible parses is arbitrary.
    returns a list of ParseTree
    """

    n = len(words)
    table = [[set() for _ in range(n - i)] for i in range(n)]

    for j in range(n):
        for rule in grammar.rules:
            if [Symbol(words[j])] == rule.rhs:
                equivalents = {rule.lhs}
                add_equivalents(rule.lhs, grammar.rules, equivalents)
                for e in equivalents:
                    table[0][j].add(ParseTree(e, [ParseTree(Symbol(words[j]))]))

    for i in range(1, n):
        for j in range(n - i):
            for k in range(i):
                left_set = table[k][j]
                right_set = table[i - k - 1][j + k + 1]
                for rule in grammar.rules:
                    if len(rule.rhs) == 2:
                        for left_tree in left_set:
                            if rule.rhs[0] == left_tree.symbol:
                                for right_tree in right_set:
                                    if rule.rhs[1] == right_tree.symbol:
                                        table[i][j].add(ParseTree(rule.lhs, [left_tree, right_tree]))

            # unary rule:
            new_table_cell_value = set()
            for tree in table[i][j]:
                s = tree.symbol
                equivalents = {s}
                add_equivalents(s, grammar.rules, equivalents)
                for e in equivalents:
                    new_table_cell_value.add(ParseTree(e, tree.productions))
            table[i][j] = new_table_cell_value

    # print(table)
    return list(table[n - 1][0])


def add_equivalents(s: Symbol, rules: List[GrammarRule], equivalents: Set[Symbol]):
    for rule in rules:
        if len(rule.rhs) == 1 and not rule.rhs[0].terminal:
            left_symbol, right_symbol = rule.lhs, rule.rhs[0]
            if left_symbol == s:
                if right_symbol not in equivalents:
                    equivalents.add(right_symbol)
                    add_equivalents(right_symbol, rules, equivalents)
            elif right_symbol == s:
                if left_symbol not in equivalents:
                    equivalents.add(left_symbol)
                    add_equivalents(left_symbol, rules, equivalents)


def de_normalize_tree(tree: ParseTree, ):
    if len(tree.productions) == 0:
        return tree

    new_productions = []
    for node in tree.productions:
        if node.symbol.original:
            new_productions.append(de_normalize_tree(node))
        else:
            new_productions.extend(de_normalize_tree(node))

    if tree.symbol.original:
        return ParseTree(tree.symbol, new_productions)
    else:
        return new_productions


def example_telescope_parse():
    return \
        ParseTree(Symbol("$S"),
                  [ParseNode(Symbol("$NP"),
                             [ParseNode(Symbol("I"))]),
                   ParseNode(Symbol("$VP"),
                             [ParseNode(Symbol("$VP"),
                                        [ParseNode(Symbol("$V"),
                                                   [ParseNode(Symbol("saw"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("the"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("duck"))])])]),
                              ParseNode(Symbol("$PP"),
                                        [ParseNode(Symbol("$P"),
                                                   [ParseNode(Symbol("with"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("a"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("telescope"))])])])])])
