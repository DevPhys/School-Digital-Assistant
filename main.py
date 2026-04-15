import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import statistics,re,json,os
import chemlib as ch
import matplotlib
matplotlib.use('TkAgg') # Принудительно используем движок Tkinter
import matplotlib.pyplot as plt
import numpy as np

# Класс Clearing для работы со строками
class Clearing:
    # Подготовка переменных
    def __init__(self,string="",ach = r"-+*:/^v().x=",n=-1,bl=True):
        self.string = string
        self.ach = ach
        self.n = n
        self.bl = bl

    # Функция очистки для физики(возвращает строку-ключ и список чисел)
    def clear_p(self) -> (list, str):
        s = self.string[self.n + 1:].lower().replace(",", ".")

        pairs = re.findall(r"([a-z])\s*(-?\d+\.?\d*)", s)

        if 'g' in s and not any(p[0] == 'g' for p in pairs):
            pairs.append(('g', '9.8'))

        pairs.sort(key=lambda x: x[0])
        letters = "".join([p[0] for p in pairs])

        num_list = []
        for _, val in pairs:
            n = float(val)
            num_list.append(int(n) if n % 1 == 0 else n)

        #print(f"Числа: {num_list}\nКлюч: {letters}")
        return num_list, letters

    # Функция очистки для всего остального
    def clear(self,var=None) -> str:
        s = var[self.n + 1:] if var is not None else self.string[self.n + 1:]
        math_str1 = re.sub(f"[^0-9{re.escape(self.ach)}]", '', s.replace(",", "."))

        #if self.bl: print("первый этап очистки:", math_str1)
        s2 = math_str1

        s2 = re.sub(r'(\d|x)\(', r'\1*(', s2)
        s2 = re.sub(r'\)(\d|x)', r')*\1', s2)

        s2 = re.sub(r'(?<=\d)\.(?=\d)', 'TEMP_DOT', s2)
        s2 = s2.replace('.', '')
        s2 = s2.replace('TEMP_DOT', '.')
        s2 = re.sub(r'(?<=\d|x)\^(?=\d|x|-)', r'^', s2)
        s2 = re.sub(r'(?<=\d|x)v(?=\d|x|-)', r'*v', s2)
        s2 = re.sub(r'([+*:^v])\1+', r'\1', s2)
        s2 = re.sub(r'[+*:^v\-]$', '', s2)
        s2 = re.sub(r'(\d)x', r'\1*x', s2)
        s2 = re.sub(r'x(\d)', r'\1*x', s2)

        #if self.bl: print("Второй этап очистки:", s2)
        return s2

    # Функция токенизации
    def tokenize(self, var=None) -> list:
        string = var if var is not None else self.string
        # Паттерн: ищем числа (включая точки), x, g, v или операторы
        pattern = r"\d+\.?\d*|[xgv]|[-+*:/^()=*]"
        tokens = re.findall(pattern, string)

        final_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == "-" and (i == 0 or tokens[i - 1] in "+*:/^("):
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token == "v":
                        final_tokens.append("-v")
                        i += 2
                        continue
                    elif re.match(r"\d+\.?\d*", next_token):
                        final_tokens.append("-" + next_token)
                        i += 2
                        continue

            final_tokens.append(token)
            i += 1

        return final_tokens

    # Обратная токенизация
    def back_tokenize(self,var=None,string=""):
        res = "".join(var) if var is not None else "".join(self.string)
        log(f"{string}{res}")

        return f"{string}{res}"

# Сласс Match_xy в виде доп. функций для класса Match
class Math_xy:
    x = None
    y = None

    # Подготовка переменных
    def __init__(self,x: int|float,y: int|float):
        self.x = x
        self.y = y

    # Сумма
    def sum_of_numbers(self) -> int|float:
        res = self.x + self.y
        return int(res) if res % 1 == 0 else round(res,2)
    # Вычитание
    def calculation(self) -> int|float:
        res = self.x - self.y
        return int(res) if res % 1 == 0 else round(res,2)
    # Умножение
    def multiplication(self) -> int|float:
        res = self.x * self.y
        return int(res) if res % 1 == 0 else round(res,2)
    # Деление
    def division(self) -> int|float:
        res = self.x / self.y
        return int(res) if res % 1 == 0 else round(res,2)
    # Возведение в степень (два числа)
    def degree(self) -> int|float:
        res = self.x ** self.y
        return int(res) if res % 1 == 0 else round(res,2)
    # Извлечение корня
    def root(self) -> int|float:
        res = self.x ** 0.5
        return int(res) if res % 1 == 0 else round(res,2)

# Класс Match для математической логики
class Math:

    # Подготовка переменных
    def __init__(self,var=None):
        self.var = var

    # Вычисление корня
    def beauty_root(self):
        n = self.var
        try:
            n = float(n)
        except ValueError:
            return "Ошибка!"

        if n < 0: return "Ошибка! Корень из отрицательного числа!"
        if n == 0: return "0"

        root_val = n ** 0.5

        # 1. Если извлекается ровно (v25 -> 5, v0.25 -> 0.5)
        if root_val == int(root_val) or round(root_val ** 2, 10) == n:
            res = round(root_val, 10)
            return str(int(res) if res % 1 == 0 else res)

        # 2. Если число целое, пробуем вынести множитель
        if n % 1 == 0:
            n = int(n)
            outside = 1
            inside = n
            d = 2
            # Цикл до корня из n — это быстрее
            while d * d <= inside:
                # Пока число делится на квадрат d
                while inside % (d * d) == 0:
                    inside //= (d * d)
                    outside *= d
                d += 1

            if inside == 1: return str(outside)
            if outside == 1: return f"v{inside}"
            return f"{outside}v{inside}"

        # 3. Если дробь и не извлекается ровно
        return f"v{n}"

    # Функция Корня
    def main_r(self,var=None):
        list_expression = var if var is not None else self.var
        while "v" in list_expression or "-v" in list_expression:
            if "v" in list_expression:
                i = list_expression.index("v")

                if float(list_expression[i + 1]) < 0:
                    return "Ошибка: корень из отрицательного числа!"
                mt = Math_xy(float(list_expression[i + 1]),0)
                result = mt.root()
                list_expression[i:i + 2] = [str(result)]
            if "-v" in list_expression:
                i = list_expression.index("-v")

                if float(list_expression[i + 1]) < 0:
                    return "Ошибка: корень из отрицательного числа!"
                mt = Math_xy(float(list_expression[i + 1]), 0)
                result = mt.root()
                result *= -1
                list_expression[i:i + 2] = [str(result)]

        return list_expression

    # Функция степени
    def main_d(self,var=None):
        list_expression = var if var is not None else self.var
        while "^" in list_expression:
            i = list_expression.index("^")
            mt = Math_xy(float(list_expression[i - 1]), float(list_expression[i + 1]))
            result = mt.degree()
            list_expression[i - 1: i + 2] = [str(result)]

        return list_expression

    # Функция умножения/деления
    def main_divis(self,var=None):
        list_expression = var if var is not None else self.var
        while ":" in list_expression or "*" in list_expression or "/" in list_expression:
            for i in range(len(list_expression)):
                if list_expression[i] in [":", "*", "/"]:
                    if list_expression[i] == "*":
                        mt = Math_xy(float(list_expression[i - 1]), float(list_expression[i + 1]))
                        res = mt.multiplication()
                    else:
                        mt = Math_xy(float(list_expression[i - 1]), float(list_expression[i + 1]))
                        res = mt.division()

                    list_expression[i - 1: i + 2] = [str(res)]

                    break
        return list_expression

    # Функция суммы/вычитания
    def main_sum_sub(self,var=None):
        list_expression = var if var is not None else self.var
        while "+" in list_expression or "-" in list_expression:
            for i in range(len(list_expression)):
                if list_expression[i] == "+" or list_expression[i] == "-":
                    x = float(list_expression[i - 1])
                    y = float(list_expression[i + 1])

                    mt = Math_xy(x, y)
                    if list_expression[i] == "+":
                        res = mt.sum_of_numbers()
                    else:
                        res = mt.calculation()

                    list_expression[i - 1: i + 2] = [str(res)]

                    break

        return list_expression

    # Функция сокращения дробей
    def main_fraction(self,var=None):
        list_expression = var if var is not None else self.var
        list_expression = list(list_expression)

        i = 0
        while i < len(list_expression):
            if list_expression[i] == "/":
                try:
                    x = int(float(list_expression[i - 1]))
                    y = int(float(list_expression[i + 1]))
                except ValueError:
                    i += 1
                    continue

                n = 2
                limit = min(abs(x), abs(y))
                while n <= limit:
                    if x % n == 0 and y % n == 0:
                        x //= n
                        y //= n
                        limit = min(abs(x), abs(y))
                    else:
                        n += 1

                list_expression[i - 1] = str(x)
                list_expression[i + 1] = str(y)

                i += 2
            else:
                i += 1

        return list_expression

    # Функция вычислений в скобках для строк
    def solve_brackets(self,var=None):
        expression_str = var if var is not None else self.var
        cl = Clearing()
        while "(" in expression_str:
            start = expression_str.rfind("(")
            end = expression_str.find(")", start)

            if end == -1:
                return "Ошибка: не закрыта скобка!"

            sub_expr = expression_str[start + 1:end]
            tokens = cl.tokenize(var=sub_expr)
            result = self.main_sum_sub(self.main_divis(self.main_d(self.main_r(tokens))))
            res_str = str(result[0])

            expression_str = expression_str[:start] + res_str + expression_str[end + 1:]

        return expression_str

    # Функция вычислений в скобках для списков
    def solve_list_brackets(self,var=None):
        tokens = var if var is not None else self.var
        while "(" in tokens:
            start = 0
            for i in range(len(tokens)):
                if tokens[i] == "(":
                    start = i

            end = tokens.index(")", start)
            sub_tokens = tokens[start + 1: end]
            sub_res = self.main_sum_sub(self.main_divis(self.main_d(self.main_r(sub_tokens))))

            tokens[start: end + 1] = [str(sub_res[0])]

        return tokens

    def equation_x(self,my_list, x_value):
        for i in range(len(my_list)):
            if my_list[i] in ["x", "х"]:
                my_list[i] = str(x_value)
        return my_list

    # Функция для нохаждения х в линейных уравнениях
    def equation(self):
        cl = Clearing()

        str_equation = self.var
        str_equation = str_equation.replace(" ", "")
        for i in "0123456789":
            str_equation = str_equation.replace(f"{i}x", f"{i}*x").replace(f"{i}х", f"{i}*x")

        parts = str_equation.split("=")

        tokens_l_raw = cl.tokenize(var=parts[0])
        tokens_r_raw = cl.tokenize(var=parts[1])

        x = -500.0
        prev_diff = None

        result = []
        while x <= 500.0:
            current_l = [str(x) if t in ["x", "х"] else t for t in tokens_l_raw]
            current_r = [str(x) if t in ["x", "х"] else t for t in tokens_r_raw]

            current_l = self.solve_list_brackets(var=current_l)
            current_r = self.solve_list_brackets(var=current_r)

            res_l = float(self.main_sum_sub(self.main_divis(self.main_d(self.main_r(current_l))))[0])
            res_r = float(self.main_sum_sub(self.main_divis(self.main_d(self.main_r(current_r))))[0])

            diff = res_l - res_r

            if abs(diff) < 0.000001:
                res = x
                return int(res) if res % 1 == 0 else res

            if prev_diff is not None and (prev_diff * diff < 0):
                res = x
                return int(res) if res % 1 == 0 else res

            prev_diff = diff
            x = round(x + 0.01, 2)

        if len(result) < 1: return "Решение не найдено"
        else: return result

    # Нахождение a, b, c для квадратных уравнений
    def find_abc(self):
        s = "".join(self.var)

        match_a = re.search(r'([-+]?\d*\.?\d*)\*?x\^2', s)
        if match_a:
            val = match_a.group(1)
            if val in ['', '+']:
                a = 1
            elif val == '-':
                a = -1
            else:
                a = float(val) if float(val) % 1 != 0 else int(val)
        else:
            a = 0.0

        match_b = re.search(r'([-+]?\d*\.?\d*)\*?x(?!\^2)', s)
        if match_b:
            val = match_b.group(1)
            if val in ['', '+']:
                b = 1.0
            elif val == '-':
                b = -1.0
            else:
                b = float(val) if float(val) % 1 != 0 else int(val)
        else:
            b = 0.0

        temp_s = re.sub(r'([-+]?\d*\.?\d*)\*?x(\^2)?', '', s)
        match_c = re.search(r'[-+]?\d+\.?\d*', temp_s)
        c = float(match_c.group(0)) if match_c else 0.0
        if c % 1 == 0: c = int(c)

        return a, b, c

    # Нахождение дискреминанта
    def solve_quadratic(self,a, b, c):
        # D = -b^2 - 4ac
        d = (b) ** 2 - 4 * a * c

        steps = [f"Уравнение: {a}x^2 + ({b})x + ({c}) = 0", f"Дискриминант D = b^2 - 4ac = {b}^2 - 4*{a}*{c} = {d}"]

        if d < 0:
            steps.append("D < 0, корней нет\n")
            return steps, d

        elif d == 0:
            x = -b / (2 * a)
            steps.append(f"D = 0, один корень: x = -({b}) / (2*{a}) = {x}")
            return steps, d

        else:
            sqrt_d = d ** 0.5
            x1 = (-b + sqrt_d) / (2 * a)
            x2 = (-b - sqrt_d) / (2 * a)
            steps.append(f"D > 0, два корня:")

            steps.append(f"x1 = (-({b}) + v{d}) / (2 * {a}) = {round(x1, 2) if round(x1, 2) % 1 != 0 else int(x1)}")
            steps.append(f"x2 = (-({b}) - v{d}) / (2 * {a}) = {round(x2, 2) if round(x2, 2) % 1 != 0 else int(x2)}")

            return steps, d

    # НОД
    def nod(self,x, y):
        x, y = abs(int(x)), abs(int(y))
        if x == 0 or y == 0: return x + y

        n = min(x, y)
        while x % n != 0 or y % n != 0:
            n -= 1

        return n

    # НОК
    def nok(self,x, y):
        x, y = abs(int(x)), abs(int(y))
        if x == 0 or y == 0: return 0
        # Формула: произведение делим на НОД
        return (x * y) // self.nod(x, y)

    # уневирсальная функция для физики
    def physical_formulas(self,num_list, bl, num):
        y = num_list[1]
        x = num_list[0]

        if len(num_list) == 2:
            if bl:
                n = x / y
                con = round(n * num, 2)
                return f"= {x} / {y} = {con if con % 1 != 0 else int(con)}", n * num
            elif not bl:
                n = x * y
                con = round(n * num, 2)
                return f"= {x} * {y} = {con if con % 1 != 0 else int(con)}", n * num

        elif len(num_list) == 3:
            z = num_list[2]
            if bl:
                n = x * y / z
                con = round(n * num, 2)
                return f"= {x} * {y} / {z} = {con if con % 1 != 0 else int(con)}", n * num
            elif not bl:
                n = x * y * z
                con = round(n * num, 2)
                return f"= {x} * {y} * {z} = {con if con % 1 != 0 else int(con)}", n * num

    # Статистика
    def stat(self, string):
        target_match = re.search(r'\(([-+]?\d*\.?\d*)\)', string)
        target_num = float(target_match.group(1)) if target_match else 0.0

        clean_string = re.sub(r'\(.*?\)', ' ', string).replace(',', '.')

        data = [float(n) for n in re.findall(r"-?\d+\.?\d*", clean_string)]

        if not data:
            return [0] * 8

        # 3. Базовые расчеты
        n = len(data)
        mean_val = statistics.mean(data)

        if n > 1:
            variance_val = statistics.variance(data)
            stdev_val = statistics.stdev(data)
        else:
            variance_val = stdev_val = 0

        freq = data.count(target_num)
        rel_freq = freq / n

        med = round(statistics.median(data), 3)
        moda = statistics.multimode(data)
        if len(moda) != 1: moda = "Больше 2 значений"
        rasmax = round(max(data) - min(data), 3)

        return [
            rasmax if rasmax % 1 != 0 else int(rasmax),  # Размах
            moda,  # Мода (список)
            med if med % 1 != 0 else int(med),  # Медиана
            round(mean_val, 3),  # Среднее
            round(variance_val, 3),  # Дисперсия
            round(stdev_val, 3),  # Станд. отклонение
            freq,  # Частота target_num
            round(rel_freq, 3)  # Относ. частота target_num
        ]

# Класс File для сохранения и чтения файлов
class File:

    def __init__(self):
        self.n = 15

    def save(self, file_name, data):
        n = self.n
        history = []
        if os.path.exists(file_name):
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    history = json.load(f)
                if not isinstance(history, list):
                    history = []
            except (json.JSONDecodeError, ValueError):
                history = []

        history.append(data)

        if len(history) > n:
            history = history[-n:]

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    def read(self, file_name="", bl=False):
        if not os.path.exists(file_name):
            return "файл не найден"

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                history = json.load(f)

            last_records = history

            if bl:
                formatted_history = ""
                for item in last_records:
                    formatted_history += f"[{item['date']}] {item['expression']} {item['result']}\n"

                return formatted_history
            return last_records


        except (json.JSONDecodeError, ValueError):
            return f"Ошибка: файл {file_name} поврежден."

    def delete_history(self, file_name,bl=True):
        try:
            # Перезаписываем файл пустым списком
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump([], f)
                if bl: log("История успешно очищена!\n")
        except Exception as e:
            log(f"Ошибка при удалении истории: {e}\n")

# Класс Solutions вместо бесконечных if-elif-else
class Solutions:

    def __init__(self,text):
        self.text = text

        self.exp = []
        self.result = []

        self.data = {}
        self.fl = File()
        self.letters_dict = self.fl.read(file_name="physics_dict.json")
        self.form = self.fl.read(file_name="formulas.json")

        self.cl = Clearing()
        self.mt = Math()

    def formulas(self):
        log(self.form[0]["formulas_7"])
        log(self.form[1]["formulas_8"])

    def example(self):
        self.cl.__init__(ach="-+*:/^v().")
        res = self.cl.clear(var=self.text)
        log(f"Выражение: {res}")
        self.exp.append(f"Выражение: {res}")

        # 1. Скобачки
        res_solve = self.mt.solve_brackets(var=res)
        if res_solve != res:
            log(f"Раскрытие скобочек: {res_solve}")
            self.exp.append(f"Раскрытие скобочек: {res_solve}")

        current_res = self.cl.tokenize(var=res_solve)

        # 2. Корень
        new_res = self.mt.main_r(current_res.copy())
        if new_res != current_res:
            exp = self.cl.back_tokenize(string="Корень: ", var=new_res)
            self.exp.append(exp)
            current_res = new_res

        # 3. Степень
        new_res = self.mt.main_d(current_res.copy())
        if new_res != current_res:
            exp = self.cl.back_tokenize(string="Степень: ", var=new_res)
            self.exp.append(exp)
            current_res = new_res

        # 4. Умножение/деление
        new_res = self.mt.main_divis(current_res.copy())
        if new_res != current_res:
            exp = self.cl.back_tokenize(string="Умножение/деление: ", var=new_res)
            self.exp.append(exp)
            current_res = new_res

        # 5. Сумма/вычитание
        res_ss = self.mt.main_sum_sub(current_res.copy())

        log(f"Ответ: {res_ss[0]}")
        log(f"Округление: {round(float(res_ss[0]) ,1)}\n")

        self.result.append(f"\nОтвет: {res_ss[0]}\n")

    def linear_equation(self):
        res = self.text.replace("х", "x")
        res = self.cl.clear(var=res)
        log(f"Уравнение: {res}")
        self.exp.append(f"Уравнение: {res}")

        self.mt.__init__(var=res)
        res = self.mt.equation()

        log(f"Ответ: {res}\n")
        self.result.append(f"\nОтвет: {res}\n")

    def quadratic_equation(self):
        res = self.text.replace("х", "x")
        res = self.cl.clear(var=res)
        log(f"Уравнение: {res}")
        self.exp.append(f"Уравнение: {res}")

        res = self.cl.tokenize(var=res)
        self.mt.__init__(var=res)
        a,b,c = self.mt.find_abc()
        log(f"a={a} b={b} c={c}")
        self.exp.append(f"a={a} b={b} c={c}")

        res,D = self.mt.solve_quadratic(a=a,b=b,c=c)
        log(f"{res[1]}\n{res[2]}")
        self.exp.append(f"{res[1]}\n{res[2]}")
        try:
            x1,x2 = res[3],res[4]
            log(f"{x1}\n{x2}\n")
            self.result.append(f"\n{x1}\n{x2}\n")
        except Exception:
            pass

    def plot_graph(self):

        # Очищаем выражение: заменяем ^ на ** для Python
        expr = self.text.replace("^", "**").replace(":", "/").replace("х","x")

        try:
            # Создаем массив точек X от -10 до 10 (1000 точек для плавности)
            x = np.linspace(-10, 10, 1000)

            # Безопасно вычисляем значения Y для каждого X
            # Используем eval с ограниченным словарем
            safe_dict = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "sqrt": np.sqrt}
            y = eval(expr, {"__builtins__": None}, safe_dict)

            # Настройка внешнего вида
            plt.figure(figsize=(8, 6))
            plt.plot(x, y, label=f"y = {self.text}", color="blue", linewidth=2)

            # Добавляем оси координат (крест в центре)
            plt.axhline(0, color='black', linewidth=1)
            plt.axvline(0, color='black', linewidth=1)

            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            plt.title(f"График функции {self.text}")
            plt.xlabel("X")
            plt.ylabel("Y")

            log("График построен в отдельном окне\n")
            plt.show()  # Открывает окно с графиком

        except Exception as e:
            log(f"Ошибка при построении графика: {e}\n")

    def root(self):
        self.cl.__init__(ach=".,")
        res = self.cl.clear(var=self.text)
        self.exp.append(f"Ввод: {res}")

        self.mt.__init__(var=res)
        res = self.mt.beauty_root()

        result = f"Корень: {round(float(res), 2) if round(float(res), 2) % 1 != 0 else res}\n"
        log(result)
        self.result.append(f"\n{result}")

    def reducing_fractions(self):
        self.cl.__init__(ach="./,-",string=self.text)
        res = self.cl.clear()
        self.exp.append(f"Ввод: {res}")

        res = self.cl.tokenize(var=res)
        res = self.mt.main_fraction(var=res)

        total_dashes = sum(item.count("-") for item in res)

        if total_dashes > 1:
            res = [item.replace("-", "") for item in res]

         
        res = self.cl.back_tokenize(string="Ответ сокращения:", var=res)
        self.result.append(f"\n{res}\n")

    def statistics(self):
        self.exp.append(f"Ввод: {self.text}\n")
        res = self.mt.stat(string=self.text)
        razmax, moda, mediana, mean, variance, stdev, frequency, rel_frequency = res

        res1 = f"\nРазмах:{razmax}\nМода:{moda}\nМедиана:{mediana}\nСреднее арифметическое:{mean}\nДисперсия:{variance}\n"
        res2 = f"Стандартное (среднеквадратичное) отклонение:{stdev}\nЧастота конкретного числа:{frequency}\nОтносительная частота:{rel_frequency}\n"

        log(f"{res1}{res2}")
        self.result.append(f"{res1}{res2}")

    def physics(self):
        self.cl.__init__(string=self.text,ach="qwertyuiopasdfghjklzxcvbnmQ")
        self.exp.append(f"Ввод: {self.text}")
        num_list, letters = self.cl.clear_p()

        if len(num_list) == 1:
            num_list = [1.0, num_list[0]]

        data = self.letters_dict.get(letters, [])
        formulas_to_solve = data if isinstance(data[0], (list, tuple)) else [data]

        for f_info in formulas_to_solve:
            m_d, SI_unit, formula, trans_n, trans_unit, is_mult = f_info

            calc_num = 100 if letters in ["pp", "aq"] else 1
            if letters == "irt":
                num_list[0] **= 2

            res, n = self.mt.physical_formulas(num_list, m_d, calc_num)

            _res_ = round(n * trans_n if is_mult else n / trans_n, 5)

            result = f"{formula} {res} {SI_unit} (~{_res_} {trans_unit})\n"
            log(result)
            self.result.append(f"\n{result}")

    def chemistry_moll_m(self):
        moll_m = ch.Compound(self.text)
        self.exp.append(f"Ввод: {self.text}")

        moll_m = round(moll_m.molar_mass())
        if moll_m % 1 == 0: moll_m = int(moll_m)

        log(f"Молярная масса {self.text} равна {moll_m}\n")
        self.result.append(f"\nМолярная масса равна {moll_m}\n")

    def chemistry_m_d(self):
        compound = ch.Compound(self.text)
        molar_mass = compound.molar_mass()

        log(f"Анализ соединения: {compound.formula.replace("₁", "").replace("1","")}")
        self.exp.append(f"Анализ соединения: {compound.formula}")

        log(f"Молярная масса: {molar_mass:.2f} г/моль")
        self.exp.append(f"Молярная масса: {molar_mass:.2f} г/моль")

        log("Массовые доли:")
        self.exp.append("Массовые доли:")

        for symbol in compound.occurences.keys():
            percentage = compound.percentage_by_mass(symbol)
            self.exp.append(f"{symbol}: {percentage:.2f}%")
            log(f"{symbol}: {percentage:.2f}%")

        self.result.append("")
        log("\n")

    def chemistry_qua(self):
        try:
            raw_input = self.text
            self.exp.append(f"Ввод: {raw_input}")

            if "=" in raw_input:
                left_part, right_part = raw_input.split("=")
            elif "->" in raw_input:
                left_part, right_part = raw_input.split("->")
            else:
                log("Ошибка: используйте '=' или '->' для разделения частей реакции")
                return

            reactants = [ch.Compound(formula.strip()) for formula in left_part.split("+")]
            products = [ch.Compound(formula.strip()) for formula in right_part.split("+")]

            reaction = ch.Reaction(reactants, products)
            reaction.balance()

            log(f"Уравненная реакция: {reaction.formula.replace("₁", "").replace("1","")}\n")
            self.result.append(f"\nУравненная реакция: {reaction.formula.replace("₁", "").replace("1","")}\n")
        except ValueError:
            log("Уровнять реакцию невозможно\n")
            return
        except Exception:
            log("Системная ошибка. Примите извинения\n")

    def nok(self):
        self.cl.__init__(ach="-")
        res = self.cl.clear(var=self.text)
        self.exp.append(f"Ввод: {res}")
        res = self.cl.tokenize(var=res)

        res = self.mt.nok(float(res[0]), float(res[2]))
        log(f"НОК: {res}\n")
        self.result.append(f"\nНОК: {res}\n")

    def nod(self):
        self.cl.__init__(ach="-")
        res = self.cl.clear(var=self.text)
        self.exp.append(f"Ввод: {res}")
        res = self.cl.tokenize(var=res)

        res = self.mt.nod(float(res[0]), float(res[2]))
        log(f"НОД: {res}\n")
        self.result.append(f"\nНОД: {res}\n")

    def help(self):
        log(f"{'-' * 60}Справка{'-' * 60}")
        log("1. Алгебра. Команды:\n/nok - НОК, записывать так: (число)-(число)), /nod - НОД, записывать так: (число)-(число)")
        log("/frc - сокращение дробей, записывать так: (число)/(число), /rot - извлечение квадрат. корня, записывать так: /rot (число)")
        log("/exp - решение примеров, записывать так: /exp (выражение), /plt - графики функций, пример записи: /plt x^2")
        log("/lin - решение линейных уравнений, /qua - решение квадратных уравнений")
        log("2. Статистика. Команда:")
        log("/sta - нахождение медианы, моды(если есть), частоты и тд, пример: /sta 1 2 2 3 (2) - в скобках то число, которое вы хотите посчитать сколько оно кол. раз встречается")
        log("3. Физика. Команды:")
        log("/phs - для решения формул, пример: /phs m40,6 c4200 t3 - находит количества темлоты (Q)")
        log("/frm - справочник по формулам 7-8 классы")
        log("4. Химия. Команды:")
        log("/chm - расчет молярной массы, пример: /chm H2O, /chd - расчет молярной доли каждого элемента")
        log("/chq - уравнивает уравнения химических реакций")
        log("5. Пользовательские команды:")
        log("/clr и /del очищают историю")
        log("/wrt - просмотр истории(последние 15 запросов + решение + ответ)")
        log("Условные обозначения:\nv(число или выражение(выражение в скобках)) - корень, (число)^(степень) - возведение в степень\n(число или выражение(выражение в скобках))/(число или выражение(выражение в скобках)) - дробь")
        log(f"{'-' * 65}{'-' * 64}")

    def save_history(self):
        try:
            self.data = {
                'date': f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",
                'expression': f"\n{"\n".join(str(item) for item in self.exp)}",
                'result': f"{self.result[0]}"
            }
            self.fl.save(file_name="history.json", data=self.data)
        except IndexError:
            pass

    def write_history(self):
        history = self.fl.read(file_name="history.json", bl=True)
        if len(history) == 0: history = "История пуста\n"
        log(history)

    def delete_history(self):
        self.fl.delete_history(file_name="history.json")

fl = File()
topic_list = fl.read(file_name="sistem.json")[0]
topic = topic_list["topic"]

root = tk.Tk()
root = root

img = tk.PhotoImage(file="icon.png")
root.iconphoto(False, img)

root.title("Школьный цифровой ассистент")
# Размеры окна
window_width = 1250
window_height = 750

# Получаем ширину и высоту экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Вычисляем координаты центра
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

# Устанавливаем размер и позицию: "ШиринаxВысота+ОтступX+ОтступY"
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

root.configure(bg=topic)

# Текстовое поле с прокруткой (аналог консоли)
chat_area = scrolledtext.ScrolledText(root, width=170, height=35, font=("Consolas", 10))
chat_area.pack(pady=10, padx=10)
chat_area.tag_config("user", foreground="#3498db", font=("Consolas", 10, "bold"))
chat_area.tag_config("bot", foreground="#000000")
chat_area.tag_config("error", foreground="#e74c3c")
chat_area.configure(state='disabled')

def open_settings():
    # Создаем новое (дочернее) окно
    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки темы")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#f5f5f5")  # Светлый фон для окна настроек

    # Заголовок внутри окна
    label = tk.Label(settings_window, text="Выберите тему приложения:", bg="#f5f5f5", font=("Arial", 10))
    label.pack(pady=10)

    # Кнопка для Бежевой темы
    beige_btn = tk.Button(settings_window, text="Бежевая (Теплая)",
                          command=lambda: apply_theme("#FAEBD7"),
                          width=20, bg="#FAEBD7")
    beige_btn.pack(pady=5)

    # Кнопка для Темной темы
    dark_btn = tk.Button(settings_window, text="Темная (Ночная)",
                         command=lambda: apply_theme("#2c3e50"),
                         width=20, bg="#2c3e50", fg="white")
    dark_btn.pack(pady=5)

# Создаем кнопку настроек
settings_btn = tk.Button(
            root,
            text="⚙ Настройки",  # Текст или иконка
            command=open_settings,  # Функция, которая сработает при нажатии
            bg="#D2B48C",  # Светло-коричневый (под бежевый)
            fg="#3E2723",  # Темно-коричневый текст
            activebackground="#C19A6B",  # Цвет при нажатии
            font=("Arial", 10, "bold"),
            relief="flat"  # Плоский современный стиль
)

# Размещаем кнопку (например, в углу)
settings_btn.pack(pady=10, padx=10, side="top", anchor="ne")

entry = tk.Entry(root, font=("Arial", 12), width=70)
entry.pack(pady=5)
entry.bind("<Return>", lambda e: handle_command())

def apply_theme(bg_color):
        # Меняем фон главного окна
        root.configure(bg=bg_color)
        fl.delete_history(file_name="sistem.json", bl=False)
        fl.save(file_name="sistem.json", data={"topic":bg_color})
        # Сообщаем в лог о смене
        log(f"Тема изменена", tag="bot")

def add_command(command_text):
        # Очищаем поле ввода (от 0 индекса до конца)
        entry.delete(0, tk.END)
        # Вставляем текст команды
        entry.insert(0, command_text)
        # Опционально: ставим фокус на поле ввода, чтобы сразу можно было нажать Enter
        entry.focus()

def log(message, tag="bot", color="#000000"):
        chat_area.configure(state='normal')

        # Настраиваем цвет для конкретного тега
        chat_area.tag_config(tag, foreground=color)

        # Вставляем текст с указанием этого тега
        chat_area.insert(tk.END, message + "\n", tag)

        chat_area.see(tk.END)
        chat_area.configure(state='disabled')

def main_loop():
        # Добавляем self. перед entry, чтобы поле было доступно во всем классе

        btn = tk.Button(root, text="ОТПРАВИТЬ", command=handle_command,
                        bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        btn.pack(pady=10)

        commands = ["/help", "/wrt", "/clr", "/del", "/exp", "/lin", "/qua", "/plt", "/nod", "/nok", "/rot", "/frc","/sta",
                    "/phs","/chm","/chd","/chq","/frm"]

        current_x = 4
        for cmd in commands:
            btn = tk.Button(
                text=cmd,
                command=lambda c=cmd: add_command(c),
                bg="#D2B48C",
                relief="flat",
                width=10
            )
            # 2. Ставим кнопку по точным координатам
            btn.place(y=700, x=current_x,width=65, height=20)
            current_x += 69

        log("Бот запущен. Введи /help для справки!", "bot")
        root.mainloop()

def handle_command():

        text = entry.get().strip()
        entry.delete(0, tk.END)

        if text != "": log(f"Ввод: {text}", "user",color="blue")

        try:

            if not text: return

            sl = Solutions(text=text[4:])
            command = {
                    "/exp": sl.example,
                    "/lin": sl.linear_equation,
                    "/qua": sl.quadratic_equation,
                    "/plt": sl.plot_graph,

                    "/sta": sl.statistics,

                    "/rot": sl.root,
                    "/nok": sl.nok,
                    "/nod": sl.nod,
                    "/frc": sl.reducing_fractions,

                    "/phs": sl.physics,
                    "/frm": sl.formulas,

                    "/chm": sl.chemistry_moll_m,
                    "/chd": sl.chemistry_m_d,
                    "/chq": sl.chemistry_qua,

                    "/wrt": sl.write_history,
                    "/clr": sl.delete_history,
                    "/del": sl.delete_history,
                }

            cmd = text[:4]
            if cmd in command:
                command[cmd]()
                sl.save_history()
                return
            elif text == "/help":
                sl.help()
            else:
                log("Ошибка! Неопознанная команда!",color="red",tag="error")
                log("Error! Unrecognized command!\n",color="red",tag="error")

        except Exception as e:
            log("Системная ошибка. Примите извинения",color="red",tag="error")
            log("System error. Please accept our apologies",tag="error",color="red")
            log(f"{e}\n",color="red",tag="error")

main_loop()