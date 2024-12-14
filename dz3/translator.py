import re
import sys
import yaml

class ConfigParser:
    def __init__(self, input_text):
        self.tokens = self.tokenize(input_text)
        self.index = 0
        self.context = {}  # Хранение ранее определенных переменных

    def tokenize(self, text):
        text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
        token_spec = [
            ("NUMBER", r"\d+\.\d*|\d+"),
            ("STRING", r'@"(.*?)"'),
            ("NAME", r"[A-Z_]+"),
            ("ASSIGN", r":="),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("LBRACKET", r"\["),
            ("RBRACKET", r"\]"),
            ("EQUAL", r"="),
            ("COMMA", r","),
            ("TABLE", r"table"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("EXPR", r"!\(([^)]+)\)"),
            ("TRUE", r"true"),
            ("FALSE", r"false"),
            ("SKIP", r"[ \t\n]+"),
            ("MISMATCH", r"."),
        ]
        token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in token_spec)
        tokens = []
        for match in re.finditer(token_regex, text):
            kind = match.lastgroup
            value = match.group(kind)
            if kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"Нераспознанный токен: {value}")
            tokens.append((kind, value))
        return tokens

    def parse(self):
        result = {}
        while self.index < len(self.tokens):
            token_type, token_value = self.tokens[self.index]
            if token_type == "NAME":
                name = self.parse_name()
                if self.index < len(self.tokens) and self.tokens[self.index][0] == "ASSIGN":
                    self.expect("ASSIGN")
                    value = self.parse_value()
                    self.context[name] = value  # Сохраняем в контексте
                    result[name] = value
                else:
                    raise SyntaxError(f"Ожидался оператор присваивания ':=' после {name}")
            else:
                raise SyntaxError(f"Неожиданный токен: {token_type}")
        return result

    def parse_value(self):
        token_type, token_value = self.tokens[self.index]
        if token_type == "STRING":
            self.index += 1
            return token_value[2:-1]
        elif token_type == "NUMBER":
            self.index += 1
            try:
                return int(token_value)
            except ValueError:
                return float(token_value)
        elif token_type == "TRUE":
            self.index += 1
            return True
        elif token_type == "FALSE":
            self.index += 1
            return False
        elif token_type == "LBRACE":
            return self.parse_array()
        elif token_type == "TABLE":
            return self.parse_table()
        elif token_type == "EXPR":
            return self.parse_expr()
        elif token_type == "NAME":
            self.index += 1
            if token_value in self.context:
                return self.context[token_value]
            else:
                raise SyntaxError(f"Неизвестное имя: {token_value}")
        else:
            raise SyntaxError(f"Неизвестный тип токена: {token_type}")

    def parse_expr(self):
        token_type, token_value = self.tokens[self.index]
        if token_type != "EXPR":
            raise SyntaxError(f"Ожидался EXPR, найдено {token_type}")
        expr = token_value[2:-1]
        result = self.evaluate_expression(expr)
        self.index += 1
        return result

    def evaluate_expression(self, expr):
        tokens = expr.split()
        stack = []
        for token in tokens:
            if token.isdigit():
                stack.append(int(token))
            elif token in self.context:
                stack.append(self.context[token])
            elif token == "+":
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            elif token == "-":
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            elif token == "*":
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
            elif token == "/":
                b = stack.pop()
                a = stack.pop()
                stack.append(a / b)
            else:
                raise SyntaxError(f"Нераспознанный оператор или имя: {token}")
        if len(stack) != 1:
            raise SyntaxError("Некорректное выражение")
        return stack[0]

    def parse_array(self):
        self.expect("LBRACE")
        array = []
        while self.tokens[self.index][0] != "RBRACE":
            value = self.parse_value()
            array.append(value)
            if self.tokens[self.index][0] == "COMMA":
                self.index += 1
        self.expect("RBRACE")
        return array

    def parse_table(self):
        self.expect("TABLE")
        self.expect("LPAREN")
        self.expect("LBRACKET")
        table = {}
        while self.tokens[self.index][0] != "RBRACKET":
            key = self.parse_name()
            self.expect("EQUAL")
            value = self.parse_value()
            table[key] = value
            if self.tokens[self.index][0] == "COMMA":
                self.index += 1
        self.expect("RBRACKET")
        self.expect("RPAREN")
        return table

    def parse_name(self):
        token_type, token_value = self.tokens[self.index]
        if token_type != "NAME":
            raise SyntaxError(f"Ожидалось имя, найдено {token_type}")
        self.index += 1
        return token_value

    def expect(self, token_type):
        if self.tokens[self.index][0] != token_type:
            raise SyntaxError(f"Ожидалось {token_type}, найдено {self.tokens[self.index][0]}")
        self.index += 1


def main():
    if len(sys.argv) != 2:
        print("Использование: python3 parser.py <input_file>", file=sys.stderr)
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as file:
            input_text = file.read()
        parser = ConfigParser(input_text)
        parsed_data = parser.parse()
        yaml_output = yaml.safe_dump(parsed_data, default_flow_style=False, allow_unicode=True)
        print(yaml_output)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
