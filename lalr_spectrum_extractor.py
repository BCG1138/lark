import os
import re
import math
import copy
from lark import Lark, UnexpectedToken

rules = []
rule_metrics = {}
rule_sus_scores = {}

items = []
item_metrics = {}
item_sus_scores = {}


def create_parser(grammar_path):
    f = open(grammar_path, "r")
    grammar = f.read()
    f.close()
    parser = Lark(grammar, lexer="basic", parser='lalr')
    return parser


def init_rules(parser):
    # indexed by (rule, production) tuple, contains 4 values
    # which, in order, are ep, np, ef, nf
    for x in parser.rules:
        clean = str(x).strip('<>')
        rule, production = clean.split(":")
        rule = rule.strip()
        production = production.strip()
        rules.append((rule, production))
        rule_metrics[(rule, production)] = [0, 0, 0, 0]
        rule_sus_scores[(rule, production)] = [0, 0, 0, 0]


def init_items():
    for x in rules:
        num_tokens = len(str(x[1]).split())
        for i in range(num_tokens + 1):
            items.append((x, i))
            item_metrics[(x, i)] = [0, 0, 0, 0]
            item_sus_scores[(x, i)] = [0, 0, 0, 0]


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
        lstate = ""
        for x in state_stack:
            lstate = x
        pattern = r"<\w+\s*\:\s*[\w][ \w]*\s\*\s*[\w][ \w]*>"
        matches = re.findall(pattern, str(lstate))
        for r in matches:
            r = str(r).replace("* ", "")
            clean = str(r).strip('<>')
            rule, production = clean.split(":")
            rule = rule.strip()
            production = production.strip()
            if (rule, production) in rules and (rule, production) not in rules_used:
                rules_used.append((rule, production))
    try:
        # read parse history from _tmp_parse_history.txt
        with open("_tmp_parse_history.txt", 'r') as file:
            lines = file.readlines()
        start_index = len(lines) - 1
        # for each entry, in reverse order
        for i in range(start_index, -1, -1):
            x = lines[i].rstrip()
            # check if junk is reached
            if re.search(r'[ <]_[a-zA-Z]', x):
                break
            # get rule and its production used in that step
            pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
            match = pattern.search(x)
            rule = match.group(1)
            production = match.group(2)
            if (rule, production) not in rules_used:
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


def get_item_usage(parser, testcase_path):
    try:
        os.remove("_tmp_parse_history.txt")
    except:
        pass
    # list of rules used during parse
    items_used = []

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
        lstate = ""
        for x in state_stack:
            lstate = x
        pattern = r"<\w+\s*\: [\s\w*]*>"
        matches = re.findall(pattern, str(x))
        for r in matches:
            clean = str(r).strip('<>')
            rule, production = clean.split(":")
            rule = rule.strip()
            production = production.strip()
            item_list = production.split()
            production = production.replace("* ", "")
            count = item_list.index("*")
            for i in range(count + 1):
                if ((rule, production), i) in items and ((rule, production), i) not in items_used:
                    items_used.append(((rule, production), i))
    try:
        # read parse history from _tmp_parse_history.txt
        with open("_tmp_parse_history.txt", 'r') as file:
            lines = file.readlines()
        start_index = len(lines) - 1
        # for each entry, in reverse order
        for i in range(start_index, -1, -1):
            x = lines[i].rstrip()
            # check if junk is reached
            if re.search(r'[ <]_[a-zA-Z]', x):
                break
            # get rule and its production used in that step
            pattern = re.compile(r"<(\w+)\s*:\s*([^>]+)>")
            match = pattern.search(x)
            rule = match.group(1)
            production = match.group(2)
            for i in range(len(production.split()) + 1):
                if ((rule, production), i) not in items_used:
                    items_used.insert(0, ((rule, production), i))
    except:
        # if _tmp_parse_history.txt doesn't exist, no rules were applied
        pass

    # delete temporary parse history file
    try:
        os.remove("_tmp_parse_history.txt")
    except:
        pass
    return (successful_parse, items_used)


def rule_run_testcase_dir(parser, directory, is_positive):
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
                    # increment ef
                    rule_metrics[x][2] += 1
                for x in rules:
                    if x not in result[1]:
                        # increment nf
                        rule_metrics[x][3] += 1

def item_run_testcase_dir(parser, directory, is_positive):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            result = get_item_usage(parser, file_path)
            # passed
            if result[0] == (is_positive):
                for x in result[1]:
                    # increment ep
                    item_metrics[x][0] += 1
                for x in items:
                    if x not in result[1]:
                        # increment np
                        item_metrics[x][1] += 1
            #failed
            elif result[0] == (not is_positive):
                print(file_path + " failed")
                for x in result[1]:
                    # increment ef
                    item_metrics[x][2] += 1
                for x in items:
                    if x not in result[1]:
                        # increment nf
                        item_metrics[x][3] += 1


def rule_compile_and_write_results():
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
            rule_sus_scores[x][0] = tarantula
            
            jaccard_bottom = vals[2] + vals[3] + vals[0] + div_by_zero_fix
            jaccard = (vals[2]) / jaccard_bottom
            rule_sus_scores[x][1] = jaccard

            ochiai_bottom = math.sqrt(vals[2] + vals[3]) * (vals[2] + vals[0]) + div_by_zero_fix
            ochiai = (vals[2]) / ochiai_bottom
            rule_sus_scores[x][2] = ochiai

            dstar_top = vals[2] ** 2
            dstar_bottom = vals[3] + vals[0] + div_by_zero_fix
            dstar = dstar_top / dstar_bottom
            rule_sus_scores[x][3] = dstar

        # rank rules by sus scores
        tarantula_scores = []
        trules = copy.deepcopy(rules)
        jaccarda_scores = []
        jrules = copy.deepcopy(rules)
        ochiai_scores = []
        orules = copy.deepcopy(rules)
        dstar_scores = []
        drules = copy.deepcopy(rules)
        for x in rules:
            tarantula_scores.append(rule_sus_scores[x][0])
            jaccarda_scores.append(rule_sus_scores[x][1])
            ochiai_scores.append(rule_sus_scores[x][2])
            dstar_scores.append(rule_sus_scores[x][3])
        n = len(rules)
        # tarantula
        for i in range(n):
            for j in range(0, n-i-1):
                if tarantula_scores[j] < tarantula_scores[j+1]:
                    #forbidden swapping
                    tarantula_scores[j], tarantula_scores[j+1] = tarantula_scores[j+1], tarantula_scores[j]
                    trules[j], trules[j+1] = trules[j+1], trules[j]
        # jaccarda
        for i in range(n):
            for j in range(0, n-i-1):
                if jaccarda_scores[j] < jaccarda_scores[j+1]:
                    #forbidden swapping
                    jaccarda_scores[j], jaccarda_scores[j+1] = jaccarda_scores[j+1], jaccarda_scores[j]
                    jrules[j], jrules[j+1] = jrules[j+1], jrules[j]
        # ochiai
        for i in range(n):
            for j in range(0, n-i-1):
                if ochiai_scores[j] < ochiai_scores[j+1]:
                    #forbidden swapping
                    ochiai_scores[j], ochiai_scores[j+1] = ochiai_scores[j+1], ochiai_scores[j]
                    orules[j], orules[j+1] = orules[j+1], orules[j]
        # dstar
        for i in range(n):
            for j in range(0, n-i-1):
                if dstar_scores[j] < dstar_scores[j+1]:
                    #forbidden swapping
                    dstar_scores[j], dstar_scores[j+1] = dstar_scores[j+1], dstar_scores[j]
                    drules[j], drules[j+1] = drules[j+1], drules[j]

        # write results to file
        results.write("Ranking by tarantula\n")
        for i in range(n):
            results.write(str(trules[i]) + " : " + str(tarantula_scores[i]) + "\n")
        results.write("\nRanking by jaccarda\n")
        for i in range(n):
            results.write(str(jrules[i]) + " : " + str(jaccarda_scores[i]) + "\n")
        results.write("\nRanking by ochiai\n")
        for i in range(n):
            results.write(str(orules[i]) + " : " + str(ochiai_scores[i]) + "\n")
        results.write("\nRanking by dstar\n")
        for i in range(n):
            results.write(str(drules[i]) + " : " + str(dstar_scores[i]) + "\n")


def item_compile_and_write_results():
    try:
        os.remove("results.txt")
    except:
        pass
    # calculate suspiciousness scores
    # metrics: 0:ep, 1:np, 2:ef, 3:nf
    # sus_scores: 0:tarantula, 1:jaccard, 2:ochiai, 3:dstar
    with open("results.txt", 'a') as results:
        for x in item_metrics:
            vals = item_metrics[x]
            div_by_zero_fix = 0.000000000000000000001

            tarantula_top = (vals[2]) / (vals[2] + vals[3] + div_by_zero_fix)
            tarantula_bottom = tarantula_top + ((vals[0]) / (vals[0] + vals[1] + div_by_zero_fix)) + div_by_zero_fix
            tarantula = tarantula_top / tarantula_bottom
            item_sus_scores[x][0] = tarantula
            
            jaccard_bottom = vals[2] + vals[3] + vals[0] + div_by_zero_fix
            jaccard = (vals[2]) / jaccard_bottom
            item_sus_scores[x][1] = jaccard

            ochiai_bottom = math.sqrt(vals[2] + vals[3]) * (vals[2] + vals[0]) + div_by_zero_fix
            ochiai = (vals[2]) / ochiai_bottom
            item_sus_scores[x][2] = ochiai

            dstar_top = vals[2] ** 2
            dstar_bottom = vals[3] + vals[0] + div_by_zero_fix
            dstar = dstar_top / dstar_bottom
            item_sus_scores[x][3] = dstar

        # rank rules by sus scores
        tarantula_scores = []
        trules = copy.deepcopy(items)
        jaccarda_scores = []
        jrules = copy.deepcopy(items)
        ochiai_scores = []
        orules = copy.deepcopy(items)
        dstar_scores = []
        drules = copy.deepcopy(items)
        for x in items:
            tarantula_scores.append(item_sus_scores[x][0])
            jaccarda_scores.append(item_sus_scores[x][1])
            ochiai_scores.append(item_sus_scores[x][2])
            dstar_scores.append(item_sus_scores[x][3])
        n = len(items)
        # tarantula
        for i in range(n):
            for j in range(0, n-i-1):
                if tarantula_scores[j] < tarantula_scores[j+1]:
                    #forbidden swapping
                    tarantula_scores[j], tarantula_scores[j+1] = tarantula_scores[j+1], tarantula_scores[j]
                    trules[j], trules[j+1] = trules[j+1], trules[j]
        # jaccarda
        for i in range(n):
            for j in range(0, n-i-1):
                if jaccarda_scores[j] < jaccarda_scores[j+1]:
                    #forbidden swapping
                    jaccarda_scores[j], jaccarda_scores[j+1] = jaccarda_scores[j+1], jaccarda_scores[j]
                    jrules[j], jrules[j+1] = jrules[j+1], jrules[j]
        # ochiai
        for i in range(n):
            for j in range(0, n-i-1):
                if ochiai_scores[j] < ochiai_scores[j+1]:
                    #forbidden swapping
                    ochiai_scores[j], ochiai_scores[j+1] = ochiai_scores[j+1], ochiai_scores[j]
                    orules[j], orules[j+1] = orules[j+1], orules[j]
        # dstar
        for i in range(n):
            for j in range(0, n-i-1):
                if dstar_scores[j] < dstar_scores[j+1]:
                    #forbidden swapping
                    dstar_scores[j], dstar_scores[j+1] = dstar_scores[j+1], dstar_scores[j]
                    drules[j], drules[j+1] = drules[j+1], drules[j]

        # write results to file
        results.write("Ranking by tarantula\n")
        for i in range(n):
            results.write(str(trules[i]) + " : " + str(tarantula_scores[i]) + "\n")
        results.write("\nRanking by jaccarda\n")
        for i in range(n):
            results.write(str(jrules[i]) + " : " + str(jaccarda_scores[i]) + "\n")
        results.write("\nRanking by ochiai\n")
        for i in range(n):
            results.write(str(orules[i]) + " : " + str(ochiai_scores[i]) + "\n")
        results.write("\nRanking by dstar\n")
        for i in range(n):
            results.write(str(drules[i]) + " : " + str(dstar_scores[i]) + "\n")


def rules_run_normal():
    rule_run_testcase_dir(parser, "../alan-tests/passing", True)
    print("Done with passing")
    rule_run_testcase_dir(parser, "../alan-tests/failing0", False)
    print("Done with failing0")
    rule_run_testcase_dir(parser, "../alan-tests/failing1", False)
    print("Done with failing1")
    rule_run_testcase_dir(parser, "../alan-tests/failing2", False)
    print("Done with failing2")

def rules_run_special():
    rule_run_testcase_dir(parser, "../alan-tests/special-passing", True)
    print("Done with special-passing")
    rule_run_testcase_dir(parser, "../alan-tests/special-failing", False)
    print("Done with special-failing")

def rules_run_quick():
    rule_run_testcase_dir(parser, "../alan-2022-examples/passing", True)
    print("Done with passing")
    rule_run_testcase_dir(parser, "../alan-2022-examples/failing", False)
    print("Done with failing")


def items_run_normal():
    item_run_testcase_dir(parser, "../alan-tests/passing", True)
    print("Done with passing")
    item_run_testcase_dir(parser, "../alan-tests/failing0", False)
    print("Done with failing0")
    item_run_testcase_dir(parser, "../alan-tests/failing1", False)
    print("Done with failing1")
    item_run_testcase_dir(parser, "../alan-tests/failing2", False)
    print("Done with failing2")

def items_run_special():
    item_run_testcase_dir(parser, "../alan-tests/special-passing", True)
    print("Done with special-passing")
    item_run_testcase_dir(parser, "../alan-tests/special-failing", False)
    print("Done with special-failing")

def items_run_quick():
    item_run_testcase_dir(parser, "../alan-2022-examples/passing", True)
    print("Done with passing")
    item_run_testcase_dir(parser, "../alan-2022-examples/failing", False)
    print("Done with failing")

parser = create_parser("toy_grammar/toy.lark")
#parser = create_parser("alan.lark")
init_rules(parser)
init_items()
item_run_testcase_dir(parser, "toy_grammar/testsuite", True)

#result = get_item_usage(parser, "test2.txt")
#for x in result[1]:
#    print(x)

#item_run_testcase_dir(parser, "../alan-2022-examples/passing", True)
item_compile_and_write_results()