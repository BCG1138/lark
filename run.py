import os
from lark import Lark

try:
	#if os.path.exists("parse_history.txt"):
  os.remove("parse_history.txt")
except:
	print("")

f = open("alan.lark", "r")
grammar = f.read()
f.close()
parser = parser = Lark(grammar, lexer="basic", parser='lalr')
testing = False

f = open("test.alan", "r")
file = f.read()
f.close()

parser.parse(file)