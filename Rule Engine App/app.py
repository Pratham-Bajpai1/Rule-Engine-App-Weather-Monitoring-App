import flask
from flask import Flask, jsonify, request
from extensions import db
from models.ast_node import ASTNode, parse_rule
from models import rule
import re

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#Temporary route to check if server is running
@app.route('/')
def index():
    return "Rule Engine API is running!"

@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get("rule_string")
    rule_name = data.get("name")

    if not rule_string or not rule_name:
        return jsonify({"error": "Rule name and rule string are required"}), 400

    # Parse the rule string into an AST
    ast_root = parse_rule(rule_string)

    ast_json = ast_root.to_dict()

    # Save to the database
    new_rule = rule.Rule(name=rule_name, rule_string=rule_string, ast=ast_json)
    db.session.add(new_rule)
    db.session.commit()

    return jsonify({"message": "Rule created successfully!", "ast": ast_json}), 201

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    data = request.json
    rule_strings = data.get("rules")
    operators = data.get("operators", ["AND"] * (len(rule_strings) - 1))

    if not rule_strings or not isinstance(rule_strings, list):
        return jsonify({"error": "A list of rule strings is required"}), 400
    if len(operators) != len(rule_strings) - 1:
        return jsonify({"error": "Number of operators should be one less than the number of rules"}), 400

    # Parse each rule string into an AST and store in list
    asts = []
    for rule_string in rule_strings:
        ast = parse_rule(rule_string)
        if ast:
            asts.append(ast)

    # Combine ASTs using AND operator
    combined_ast = asts[0]
    for i, next_ast in enumerate(asts[1:]):
        operator = operators[i]
        combined_ast = ASTNode(type="operator", left=combined_ast, right=next_ast, value=operator)

    # Convert the final combined AST to a dictionary for JSON response
    combined_ast_json = combined_ast.to_dict()
    return jsonify({"message": "Rules combined successfully!", "combined_ast": combined_ast_json}), 201


def evaluate_ast(ast_node, user_data):
    """Recursively evaluate the AST against user data."""
    if ast_node.type == "operand":
        # Parse operand condition (e.g., "age > 30")
        attribute, operator, value = re.split(r' (>=|<=|=|>|<) ', ast_node.value)
        value = int(value) if value.isdigit() else value.strip("'")

        # Get the user's attribute value
        user_value = user_data.get(attribute.strip())
        if user_value is None:
            return False

        # Evaluate based on the operator
        if operator == ">":
            return user_value > value
        elif operator == "<":
            return user_value < value
        elif operator == "=":
            return user_value == value
        elif operator == ">=":
            return user_value >= value
        elif operator == "<=":
            return user_value <= value
        elif operator == "!=":
            return user_value != value
        else:
            return False

    elif ast_node.type == "operator":
        # Logical operator (AND/OR)
        left_result = evaluate_ast(ast_node.left, user_data)
        right_result = evaluate_ast(ast_node.right, user_data)

        if ast_node.value == "AND":
            return left_result and right_result
        elif ast_node.value == "OR":
            return left_result or right_result

    return False

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.json
    ast = data.get("combined_ast")
    user_data = data.get("user_data")

    if not ast or not user_data:
        return jsonify({"error": "Both 'combined_ast' and 'user_data' are required"}), 400

    # Reconstruct AST from dictionary format
    def build_ast_from_dict(node_dict):
        if not node_dict:
            return None
        node = ASTNode(type=node_dict["type"], value=node_dict["value"])

        if "left" in node_dict:
            node.left = build_ast_from_dict(node_dict["left"])
        if "right" in node_dict:
            node.right = build_ast_from_dict(node_dict["right"])

        return node

    ast_root = build_ast_from_dict(ast)

    # Evaluate the rule based on the AST and user data
    result = evaluate_ast(ast_root, user_data)
    return jsonify({"result": result}), 200

@app.route('/ui')
def ui():
    return flask.render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)