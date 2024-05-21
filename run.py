import os
import sys
import re
from lark import Lark

try:
    os.remove("parse_history.txt")
except:
    pass

rules_used = []

f = open("alan.lark", "r")
grammar = f.read()
f.close()
parser = parser = Lark(grammar, lexer="basic", parser='lalr')
testing = False

f = open("test.alan", "r")
file = f.read()
f.close()

parser.parse("source test begin relax end")

print("Rules used:")
with open("parse_history.txt", 'r') as file:
    lines = file.readlines()
start_index = len(lines) - 1
for i in range(start_index, -1, -1):
    x = lines[i].rstrip()
    # check if juck is reached
    if re.search(r' _[a-zA-Z]', x) or re.search(r'<_[a-zA-Z]', x):
        break
    
    pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
    match = pattern.search(x)
    rule = match.group(1)
    production = match.group(2)
    print("rule = " + rule + "; production = " + production)
    rules_used.append((rule, production))
