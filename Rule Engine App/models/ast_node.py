import re

class ASTNode:
    def __init__(self, type, left=None, right=None, value=None):
        self.type = type         # 'operator' or 'operand'
        self.left = left         # Left child (for operators)
        self.right = right       # Right child (for operators)
        self.value = value       # Value for operand nodes

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

    def __repr__(self):
        if self.type == 'operand':
            return f"Operand({self.value})"
        return f"Operator({self.type}, {self.left}, {self.right})"


def parse_rule(rule_string):
    """
    Parses a rule string into an AST.
    Supports AND, OR operations and simple comparisons (e.g., age > 30).
    """
    # Tokenize based on logical operators and parentheses
    tokens = re.findall(r'\(|\)|AND|OR|[a-zA-Z_]+ [<>=]+ \d+|[a-zA-Z_]+ = \'\w+\'', rule_string)

    def parse_expression(index):
        stack = []
        current_node = None

        while index < len(tokens):
            token = tokens[index]

            if token == '(':
                node, index = parse_expression(index + 1)
                stack.append(node)
            elif token == ')':
                break
            elif token in ('AND', 'OR'):
                operator = ASTNode(type="operator", value=token)
                if stack:
                    operator.left = stack.pop()
                current_node = operator
                stack.append(current_node)
            else:
                operand = ASTNode(type="operand", value=token)
                if stack and isinstance(stack[-1], ASTNode) and stack[-1].type == "operator":
                    stack[-1].right = operand
                else:
                    stack.append(operand)

            index += 1

        # Combine operators with their operands
        while len(stack) > 1:
            right = stack.pop()
            if len(stack) > 0:
                operator = stack.pop()
                operator.right = right
                if len(stack) > 0:
                    operator.left = stack.pop()
                stack.append(operator)

        return stack[0] if stack else None, index

    # Parse the rule from the start
    ast_root, _ = parse_expression(0)
    return ast_root