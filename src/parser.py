import math
from decimal import Decimal, getcontext
getcontext().prec = 28

# maping of mathematical functions
FUNCTIONS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log10,  # log base 10
    'ln': math.log,     # Natural log
    'sqrt': math.sqrt,
    'fact': math.factorial
}

def calculate(exper):
    try:
        tokens = tokenize(exper)
        result = parse_expression(tokens)
        if tokens:
            return "Mismatched parentheses or invalid expression"
        return result
    except ZeroDivisionError:
        return "Division by Zero"
    except Exception as e:
        return str(e)

def tokenize(expression):
    allowed = "1234567890()-+/*.^abcdefghijklmnopqrstuvwxyz!"
    for ch in expression:
        if ch not in allowed:
            raise Exception("Invalid character: "+ ch)
    tokens = []
    current_token = ""

    for ch in expression:
        if ch.isdigit() or ch ==".":
            current_token += ch
        elif ch.isalpha():
            current_token += ch
        else:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            if ch in "+-*/()":
                tokens.append(ch)
    if current_token:
        tokens.append(current_token)
    return tokens

def parse_factor(tokens):
    token = tokens.pop(0)

    if token == "(":
        value = parse_expression(tokens)
        tokens.pop(0)   # closing ')' remove karna
        return value
    elif token in FUNCTIONS:
        if tokens[0] == "(":
            tokens.pop(0)  #Remove open bracketd
            val = parse_expression(tokens)
            tokens.pop(0)   #Remove close bracket
            return FUNCTIONS[token](val)
        else:
            raise Exception("Function missing brackets")
    else:
        return Decimal(token)
    
def parse_term(tokens):
    value = parse_factor(tokens)

    while tokens and tokens[0] in ("*", "/", "^"):
        op = tokens.pop(0)
        next_value = parse_factor(tokens)
        if op == "*":
            value *= next_value
        elif op == "/":
            # divide by zero check
            if next_value == 0:
                raise ZeroDivisionError("Division by Zero")
            value /= next_value
        elif op == "^":
            value = math.pow(value, next_value)
    return value

def parse_expression(tokens):
    value = parse_term(tokens)

    while tokens and tokens[0] in ("+", "-"):
        op = tokens.pop(0)
        next_value = parse_term(tokens)
        if op == "+":
            value += next_value
        elif op == "-":
            value -= next_value
    return value