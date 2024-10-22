from flask import Flask, request, jsonify
import ast
import sqlite3
from flask import send_from_directory

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('rule_engine.db')
    conn.row_factory = sqlite3.Row
    return conn

# Node class for AST representation
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type
        self.left = left
        self.right = right
        self.value = value

# Create a rule from string
def create_rule(rule_string):
    def parse_expr(expr):
        if 'AND' in expr:
            left, right = expr.split('AND', 1)
            return Node('operator', parse_expr(left.strip()), parse_expr(right.strip()), 'AND')
        elif 'OR' in expr:
            left, right = expr.split('OR', 1)
            return Node('operator', parse_expr(left.strip()), parse_expr(right.strip()), 'OR')
        else:
            return Node('operand', value=expr.strip())

    return parse_expr(rule_string)

# Combine multiple rules
def combine_rules(rules):
    asts = [create_rule(rule) for rule in rules]
    root = asts[0]
    for ast in asts[1:]:
        root = Node('operator', left=root, right=ast, value='AND')
    return root

# Evaluate the rule with data
def evaluate_rule(ast_node, data):
    if ast_node.node_type == 'operand':
        return eval(ast_node.value, {}, data)
    elif ast_node.node_type == 'operator':
        if ast_node.value == 'AND':
            return evaluate_rule(ast_node.left, data) and evaluate_rule(ast_node.right, data)
        elif ast_node.value == 'OR':
            return evaluate_rule(ast_node.left, data) or evaluate_rule(ast_node.right, data)

# API to create a rule
@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    rule_string = request.json['rule_string']
    ast = create_rule(rule_string)
    return jsonify({"AST": repr(ast)})

# API to combine rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    rules = request.json['rules']
    combined_ast = combine_rules(rules)
    return jsonify({"Combined_AST": repr(combined_ast)})

# API to evaluate a rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    rule_string = request.json['rule_string']
    data = request.json['data']
    ast = create_rule(rule_string)
    result = evaluate_rule(ast, data)
    return jsonify({"result": result})


@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
    print("hello")
