# rs_calculator/__init__.py

def calculate(num1, num2, operator):
    if operator == "x":
        operator = "*"
    elif operator == "^":
        operator = "**"

    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        if num2 == 0:
            return "Error: Division by zero"
        return num1 / num2
    elif operator == "**":
        return num1 ** num2
    elif operator == "%":
        if num2 == 0:
            return "Error: Modulo by zero"
        return num1 % num2
    elif operator == "//":
        if num2 == 0:
            return "Error: Integer division by zero"
        return num1 // num2
    else:
        return "Invalid operator"

def show_help():
    print(
        "How to use (In order):\n"
        " number 1, number 2, operator\n"
        "Operators supported: +, -, *, x, /, //, %, **, ^\n"
        "RS Calculator - simplest calculator library in Python!"
    )

__version__ = "0.1.0"
