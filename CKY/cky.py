import sys
import os
import copy
import string


rules_dict = {}
nonTerm = set()
grammar = {}

def read_grammar(grammar_file):
    with open(grammar_file) as cfg:
        lines = cfg.readlines()
        lines = [x.replace("->", "").replace("→","").split() for x in lines]

        for line in lines:
            nonTerm.add(line[0])
        # print(lines)
    return lines


def add_rule(rule):
    if rule[0] not in rules_dict:
        rules_dict[rule[0]] = []

    if len(rule) == 3:
        grammar[(rule[0], rule[1])] = rule[-1]
    else:
        grammar[(rule[0], rule[1], rule[2])] = rule[-1]

    # print(grammar)

    rules_dict[rule[0]].append(rule[1:])

    # if len(rule) == 3:  # and rule[2][0] != "'":
    #     unit_rules.add((rule[0], rule[1]))


def convert_grammar(grammar):
    for rule in grammar:
        add_rule(rule)

class Parser:

    def __init__(self, grammar_path, sentences):
        self.parse_table = None
        self.prods = {}
        self.grammar = None

        if os.path.isfile(grammar_path):
            convert_grammar(read_grammar(grammar_path))

        self.rules = rules_dict
        self.nonTerm = rules_dict
        self.grammar = grammar

        # print(rules_dict)
        if os.path.isfile(sentences):
            self.parseSents(sentences)


    def parseSents(self, sentences):
        if os.path.isfile(sentences):
            with open(sentences) as inp:
                for sentence in inp:
                    # sentence = inp.readline()
                    # print(sentence)
                    self.parse(sentence)


    def parse(self, sentence):
        print("\n\nPROCESSING SENTENCE: " + sentence)

        sentence = sentence.split()
        n = len(sentence)
        scores = [[{} for j in range(n + 1)] for i in range(n + 1)]
        back = [[{} for j in range(n + 1)] for i in range(n + 1)]

        # First the Lexicon
        for i in range(n):
            word = sentence[i]
            print("\n \nSPAN: ", word)

            modified1 = set()

            for A in self.nonTerm:
                if (A, word) in self.grammar.keys():
                    scores[i][i + 1][A] = self.grammar[(A,word)]
                    print("P(" + A + " " + word + ") = ", scores[i][i + 1][A])
                else:
                    scores[i][i + 1][A] = 0
                # back[i][i + 1][A] = None

            # handle unaries
            added = True
            while added:
                added = False
                # Don't modify the dict we are iterating
                B_scores = copy.copy(scores[i][i + 1])
                for B in B_scores:
                    for A in self.nonTerm:
                        if float(B_scores[B]) > 0 and (A,B) in self.grammar.keys():
                            prob = float(self.grammar[(A,B)]) * float(B_scores[B])
                            if prob > float(B_scores[A]):
                                scores[i][i + 1][A] = prob
                                back[i][i + 1][A] = B
                                modified1.add(A)
                                added = True

            for A in modified1:
                print("P(" + A + ") = ", scores[i][i + 1][A], "(Backpointer = (", back[i][i + 1][A], "))")

        # Do higher layers
        for span in range(2, n + 1):
            for begin in range(n - span + 1):
                end = begin + span

                str1 = "\n\nSPAN: "
                for i in range(begin, end):
                    str1 += sentence[i] + " "

                print(str1)

                modified = set()

                for split in range(begin + 1, end):
                    B_scores = scores[begin][split]
                    C_scores = scores[split][end]
                    for B in B_scores:
                        for A in self.nonTerm:
                            # C2_scores = [C for C in C_scores if C.parent == A.right_child]
                            for C in C_scores:
                                # Now have A which has B as left child and C as right child
                                if (A, B, C) in self.grammar.keys():
                                    prob = float(B_scores[B]) * float(C_scores[C]) * float(self.grammar[(A,B,C)])

                                    if(prob <= 0):
                                        continue

                                    if not scores[begin][end] or A not in scores[begin][end] or prob > float(scores[begin][end][A]):
                                        scores[begin][end][A] = prob
                                        back[begin][end][A] = str(split) + ", " +  B + ", " + C
                                        modified.add(A)
                                        # print("P(" + A + ") = ", scores[begin][end][A], "(Backpointer = ", back[begin][end][A], ")")

                # Handle unaries
                added = True
                while added:
                    added = False
                    B_scores = copy.copy(scores[begin][end])
                    for B in B_scores:
                        for A in self.nonTerm:
                            if (A, B) in self.grammar.keys():
                                prob = float(self.grammar[(A,B)]) * float(B_scores[B])
                                if not B_scores or A not in B_scores or prob > float(B_scores[A]):
                                    scores[begin][end][A] = prob
                                    back[begin][end][A] = B
                                    modified.add(A)
                                    added = True

                for A in modified:
                    print("P(" + A + ") = ", scores[begin][end][A], "(Backpointer = (", back[begin][end][A], "))")


if __name__ == '__main__':
    arg = sys.argv

    if len(arg) > 3 or len(arg) <= 2:
        print("Usage: python3 Parser.py <grammar.file> <sentence.file>\n"
              "or: python3 Parser.py <grammar as string> <sentence as string>")
        exit(1)

    # parser = Parser(arg[1], arg[2])
    parser = Parser("grammar_rules.txt", "sents.txt")
    # parser.print_tree()