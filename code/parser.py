from grammar import *
from parse import *


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
                table[0][j].add(ParseTree(rule.lhs, [ParseTree(Symbol(words[j]))]))

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

    # return grammar.start_symbol in [tree.symbol for tree in table[n - 1][0]]
    return table[n - 1][0]

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
