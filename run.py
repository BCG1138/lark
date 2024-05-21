import os
import sys
import re
from lark import Lark

try:
    os.remove("parse_history.txt")
except:
    pass

# list of all rules in parser
rules = []
# list of rules used during parse
rules_used = []

f = open("alan.lark", "r")
grammar = f.read()
f.close()
parser = parser = Lark(grammar, lexer="basic", parser='lalr')
testing = False

f = open("test.alan", "r")
file = f.read()
f.close()

# gather all exisiting rules
for x in parser.rules:
    pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
    match = pattern.search(str(x))
    rule = match.group(1)
    production = match.group(2)
    rules.insert(0, (rule, production))

try:
    parser.parse(file)
except:
    pass

# read parse history from parse_history.txt
with open("parse_history.txt", 'r') as file:
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

# print rules used
for x in rules_used:
    print("rule = " + x[0] + " : production = " + x[1])
