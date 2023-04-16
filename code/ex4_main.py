import grammar
import parse
import parser

with open("../data/abnormal_grammar.srgs", "r") as f:
    lines = f.readlines()
    gr = grammar.Grammar(lines)
print(gr)

sentence = "c d g h f"
tokens = sentence.split(" ")

print("is_in_language", parser.is_in_language(tokens, gr))

parsing_results = parser.parse(tokens, gr)
for tree in parsing_results:
    print('normalized tree\n', tree.to_dot(), '\n===')
    print('denormalized tree\n', parser.de_normalize_tree(tree).to_dot(), '\n---')

# one of the parsing results should yield the same result as the example from above
# assert repr(parser.example_telescope_parse()) in map(repr, parsing_results)
