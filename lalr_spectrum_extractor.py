import os
import re
from lark import Lark


def create_parser(grammar_path):
    f = open(grammar_path, "r")
    grammar = f.read()
    f.close()
    parser = Lark(grammar, lexer="basic", parser='lalr')
    return parser


def get_rules(parser):
    rules = []
    for x in parser.rules:
        pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
        match = pattern.search(str(x))
        rule = match.group(1)
        production = match.group(2)
        rules.append((rule, production))
    return rules


def get_rule_usage(parser, testcase_path):
    try:
        os.remove("_tmp_parse_history.txt")
    except:
        pass
    # list of rules used during parse
    rules_used = []

    successful_parse = False

	# read testcase
    f = open(testcase_path, "r")
    file = f.read()
    f.close()

    try:
        parser.parse(file)
        successful_parse = True
    except:
        successful_parse = False

    # read parse history from _tmp_parse_history.txt
    with open("_tmp_parse_history.txt", 'r') as file:
        lines = file.readlines()
    start_index = len(lines) - 1
    # for each entry, in reverse order
    for i in range(start_index, -1, -1):
        x = lines[i].rstrip()
        # check if juck is reached
        if re.search(r' _[a-zA-Z]', x) or re.search(r'<_[a-zA-Z]', x):
            break
        # get rule and its production used in that step
        pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
        match = pattern.search(x)
        rule = match.group(1)
        production = match.group(2)
        rules_used.insert(0, (rule, production))

	# delete temporary parse history file
    try:
        os.remove("_tmp_parse_history.txt")
    except:
        pass
    return (successful_parse, rules_used)


parser = create_parser("alan.lark")
rules = get_rules(parser)

result = get_rule_usage(parser, "test.alan")
print(result[1])
