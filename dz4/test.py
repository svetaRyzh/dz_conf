import unittest
import os
import json
import subprocess

class TestAssemblerInterpreter(unittest.TestCase):
    def setUp(self):
        """Создает временные файлы для тестирования."""
        self.source_file = "test_program.txt"
        self.binary_file = "test_program.bin"
        self.log_file = "test_program_log.json"
        self.result_file = "test_result.json"

    def tearDown(self):
        """Удаляет временные файлы после тестирования."""
        for file in [self.source_file, self.binary_file, self.log_file, self.result_file]:
            if os.path.exists(file):
                os.remove(file)

    def write_program(self, lines):
        """Записывает строки в исходный файл."""
        with open(self.source_file, "w") as f:
            f.write("\n".join(lines))

    def run_program(self):
        """Запускает ассемблер и интерпретатор."""
        subprocess.run(["python", "assembler_interpreter.py"], check=True)

    def read_result(self):
        """Считывает результат интерпретации."""
        with open(self.result_file, "r") as f:
            return json.load(f)

    def test_load_const(self):
        """Тестирование команды LOAD_CONST."""
        self.write_program([
            "LOAD_CONST 0 10 42",  # Загружаем 42 в память (ячейка 10)
            "LOAD_CONST 0 20 99"  # Загружаем 99 в память (ячейка 20)
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][10], 42)
        self.assertEqual(result["memory"][20], 99)

    def test_load_mem(self):
        """Тестирование команды LOAD_MEM."""
        self.write_program([
            "LOAD_CONST 0 10 42",  # Загружаем 42 в память (ячейка 10)
            "LOAD_MEM 0 20 10"    # Копируем значение из ячейки 10 в ячейку 20
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][20], 42)

    def test_add(self):
        """Тестирование команды ADD."""
        self.write_program([
            "LOAD_CONST 0 10 42",  # Загружаем 42 в память (ячейка 10)
            "LOAD_CONST 0 20 58",  # Загружаем 58 в память (ячейка 20)
            "ADD 0 10 20"          # Складываем значения в ячейках 10 и 20
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][10], 42 + 58)

    def test_bitwise_or(self):
        """Тестирование команды BITWISE_OR."""
        self.write_program([
            "LOAD_CONST 0 10 1",   # Загружаем 1 в память (ячейка 10)
            "LOAD_CONST 0 20 2",   # Загружаем 2 в память (ячейка 20)
            "BITWISE_OR 0 30 10 20"  # OR значений ячеек 10 и 20, результат в ячейке 30
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][30], 1 | 2)

    def test_xor(self):
        """Тестирование команды XOR."""
        self.write_program([
            "LOAD_CONST 0 10 6",   # Загружаем 6 в память (ячейка 10)
            "LOAD_CONST 0 20 3",   # Загружаем 3 в память (ячейка 20)
            "XOR 0 10 20"          # XOR значений ячеек 10 и 20
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][10], 6 ^ 3)

    def test_store_mem(self):
        """Тестирование команды STORE_MEM."""
        self.write_program([
            "LOAD_CONST 0 10 5",   # Загружаем 5 в память (ячейка 10)
            "LOAD_CONST 0 20 7",   # Загружаем 7 в память (ячейка 20)
            "STORE_MEM 0 30 10 20"  # Сумма ячеек 10 и 20 в ячейку 30
        ])
        self.run_program()
        result = self.read_result()
        self.assertEqual(result["memory"][30], 5 + 7)

if __name__ == "__main__":
    unittest.main()
