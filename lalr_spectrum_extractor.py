import os
import re
import math
from lark import Lark, UnexpectedToken

rule_metrics = {}
sus_scores = {}


def create_parser(grammar_path):
    f = open(grammar_path, "r")
    grammar = f.read()
    f.close()
    parser = Lark(grammar, lexer="basic", parser='lalr')
    return parser


def init_rules(parser):
    rules = []
    # indexed by (rule, production) tuple, contains 4 values
    # which, in order, are ep, np, ef, nf
    for x in parser.rules:
        pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
        match = pattern.search(str(x))
        rule = match.group(1)
        production = match.group(2)
        rules.append((rule, production))
        rule_metrics[(rule, production)] = [0, 0, 0, 0]
        sus_scores[(rule, production)] = [0, 0, 0, 0]
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
    except UnexpectedToken as e:
        successful_parse = False
        state_stack = e.interactive_parser.parser_state.state_stack
        pattern = r"<\w+\s\:\s*\w+\s\*\s*\w+>"
        for x in state_stack:
            matches = re.findall(pattern, str(x))
            for rule, production in matches:
                print((rule, production))
                production = production.replace("* ", "")
                if rule in rules and  (rule, production) not in rules_used:
                    rules_used.append((rule, production))
    try:
        # read parse history from _tmp_parse_history.txt
        with open("_tmp_parse_history.txt", 'r') as file:
            lines = file.readlines()
        start_index = len(lines) - 1
        # for each entry, in reverse order
        for i in range(start_index, -1, -1):
            x = lines[i].rstrip()
            # check if juck is reached
            if re.search(r'[ <]_[a-zA-Z]', x):
                break
            # get rule and its production used in that step
            pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
            match = pattern.search(x)
            rule = match.group(1)
            production = match.group(2)
            rules_used.insert(0, (rule, production))
    except:
        # if _tmp_parse_history.txt doesn't exist, no rules were applied
        pass

        # delete temporary parse history file
    try:
        os.remove("_tmp_parse_history.txt")
    except:
        pass
    return (successful_parse, rules_used)

def run_testcase_dir(parser, directory, is_positive):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            result = get_rule_usage(parser, file_path)
            # passed
            if result[0] == (is_positive):
                for x in result[1]:
                    # increment ep
                    rule_metrics[x][0] += 1
                for x in rules:
                    if x not in result[1]:
                        # increment np
                        rule_metrics[x][1] += 1
            #failed
            elif result[0] == (not is_positive):
                print(file_path + " failed")
                for x in result[1]:
                    # increment ep
                    rule_metrics[x][2] += 1
                for x in rules:
                    if x not in result[1]:
                        # increment np
                        rule_metrics[x][3] += 1

def compile_and_write_results():
    try:
        os.remove("results.txt")
    except:
        pass
    # calculate suspiciousness scores
    # metrics: 0:ep, 1:np, 2:ef, 3:nf
    # sus_scores: 0:tarantula, 1:jaccard, 2:ochiai, 3:dstar
    with open("results.txt", 'a') as results:
        for x in rule_metrics:
            vals = rule_metrics[x]
            div_by_zero_fix = 0.000000000000000000001

            tarantula_top = (vals[2]) / (vals[2] + vals[3] + div_by_zero_fix)
            tarantula_bottom = tarantula_top + ((vals[0]) / (vals[0] + vals[1] + div_by_zero_fix)) + div_by_zero_fix
            tarantula = tarantula_top / tarantula_bottom
            sus_scores[x][0] = tarantula
            
            jaccard_bottom = vals[2] + vals[3] + vals[0] + div_by_zero_fix
            jaccard = (vals[2]) / jaccard_bottom
            sus_scores[x][1] = jaccard

            ochiai_bottom = math.sqrt(vals[2] + vals[3]) * (vals[2] + vals[0]) + div_by_zero_fix
            ochiai = (vals[2]) / ochiai_bottom
            sus_scores[x][2] = ochiai

            results.write(str(x) + "\n")
            results.write("\tTarantula: " + str(sus_scores[x][0]) + "\n")
            results.write("\tJaccarda: " + str(sus_scores[x][1]) + "\n")
            results.write("\tOchiai: " + str(sus_scores[x][2]) + "\n")

            #print(str(x) + " metrics = " + str(rule_metrics[x]))

def run_normal():
    run_testcase_dir(parser, "../alan-tests/passing", True)
    print("Done with passing")
    run_testcase_dir(parser, "../alan-tests/failing0", False)
    print("Done with failing0")
    run_testcase_dir(parser, "../alan-tests/failing1", False)
    print("Done with failing1")
    run_testcase_dir(parser, "../alan-tests/failing2", False)
    print("Done with failing2")

def run_special():
    run_testcase_dir(parser, "../alan-tests/special-passing", True)
    print("Done with special-passing")
    run_testcase_dir(parser, "../alan-tests/special-failing", False)
    print("Done with special-failing")

parser = create_parser("alan.lark")
rules = init_rules(parser)
#r = get_rule_usage(parser, "test.alan")

run_normal()
compile_and_write_results()