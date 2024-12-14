import json
import struct
import sys

#АССЕМБЛЕР

# Константы для определения структуры команд
COMMANDS = {
    "LOAD_CONST": {"opcode": 0, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41)}},
    "LOAD_MEM": {"opcode": 1, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41)}},
    "STORE_MEM": {"opcode": 2, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41), "D": (42, 61)}},
    "BITWISE_OR": {"opcode": 3, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41), "D": (42, 61)}},
    "ADD": {"opcode": 4, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41)}},
    "XOR": {"opcode": 5, "fields": {"A": (0, 5), "B": (6, 25), "C": (26, 41)}},

}

def pack_instruction(opcode, fields, data):
    bitstring = [0] * 72

    # Устанавливаем опкод (6 бит)
    for i in range(6):
        bitstring[i] = (opcode >> (5 - i)) & 1

    # Устанавливаем поля
    for name, (start, end) in fields.items():
        value = data.get(name, 0)
        bit_length = end - start + 1
        max_value = (1 << bit_length) - 1

        # Проверка диапазона
        if value < 0 or value > max_value:
            raise ValueError(f"Value for field '{name}' ({value}) exceeds allowed range: 0-{max_value} (bit range: {start}-{end})")

        # Заполняем битстроку значением
        for i in range(bit_length):
            bitstring[start + i] = (value >> (bit_length - i - 1)) & 1

    # Преобразуем битстроку в строку и затем в байты
    bitstring_str = "".join(map(str, bitstring))
    return int(bitstring_str, 2).to_bytes(9, byteorder="big")



# Ассемблер: компилирует читаемый код в бинарный
def assemble(source_path, binary_path, log_path):
    instructions = []
    log = []
    with open(source_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            command = parts[0].upper()
            args = list(map(int, parts[1:]))
            if command not in COMMANDS:
                raise ValueError(f"Unknown command: {command}")
            opcode = COMMANDS[command]["opcode"]
            fields = COMMANDS[command]["fields"]
            data = {"A": args[0], "B": args[1], "C": args[2]}
            if "D" in fields:
                data["D"] = args[3]
            instruction = pack_instruction(opcode, fields, data)
            instructions.append(instruction)
            log.append({
                "command": command,
                "fields": data,
                "binary": instruction.hex()
            })
    with open(binary_path, "wb") as binary_file:
        binary_file.write(b"".join(instructions))
    with open(log_path, "w") as log_file:
        json.dump(log, log_file, indent=4, ensure_ascii=False)

#ИНТЕРПРЕТАТОР

def extract_bits(bits, start, end):
    """Извлекает биты из строки."""
    return int(bits[start:end + 1], 2)


def unpack_instruction(data):
    """Распаковывает инструкцию из 9 байтов."""
    instruction_bits = bin(int.from_bytes(data, byteorder="big"))[2:].zfill(72)
    opcode = int(instruction_bits[:6], 2)  # Первые 6 бит для opcode
    remaining_bits = instruction_bits[6:]
    return opcode, remaining_bits



def interpret(binary_path, memory_range, result_path):
    memory = [0] * 1024  # Ограничиваем память 1024 ячейками
    result = {}

    with open(binary_path, "rb") as binary_file:
        while instruction := binary_file.read(9):
            opcode, bits = unpack_instruction(instruction)

            try:
                print(f"Interpreting opcode {opcode} with bits: {bits}")

                # Общая логика извлечения полей
                a = extract_bits(bits, 0, 5)  # Поле A: 6 бит
                b = extract_bits(bits, 6, 25) % len(memory) 
                c = extract_bits(bits, 26, 41) % len(memory)  
                d = extract_bits(bits, 42, 61) % len(memory) if opcode in [2, 3] else None  
                print(f"Opcode: {opcode}, A={a}, B={b}, C={c}, D={d}")

                if opcode == 0:  # LOAD_CONST
                    print(f"LOAD_CONST: A={a}, B={b}, C={c}")
                    if b >= len(memory):
                        raise ValueError(f"LOAD_CONST: Address B ({b}) out of bounds.")
                    memory[b] = c
                    print(f"Memory after LOAD_CONST: {memory[:50]}")

                elif opcode == 1:  # LOAD_MEM
                    print(f"LOAD_MEM: A={a}, B={b}, C={c}")
                    if b >= len(memory) or c >= len(memory):
                        raise ValueError(f"LOAD_MEM: Address B ({b}) or C ({c}) out of bounds.")
                    memory[b] = memory[c]
                    print(f"Memory after LOAD_MEM: {memory[:50]}")

                elif opcode == 2:  # STORE_MEM
                    print(f"STORE_MEM: A={a}, B={b}, C={c}, D={d}")
                    if b >= len(memory) or c >= len(memory) or d >= len(memory):
                        raise ValueError(f"STORE_MEM: Address B ({b}), C ({c}), or D ({d}) out of bounds.")
                    memory[b] = memory[c] + memory[d]
                    print(f"Memory after STORE_MEM: {memory[:50]}")

                elif opcode == 3:  # BITWISE_OR
                    print(f"BITWISE_OR: A={a}, B={b}, C={c}, D={d}")
                    if b >= len(memory) or c >= len(memory) or d >= len(memory):
                        raise ValueError(f"BITWISE_OR: Address B ({b}), C ({c}), or D ({d}) out of bounds.")
                    memory[b] = memory[c] | memory[d]
                    print(f"Memory after BITWISE_OR: {memory[:50]}")

                elif opcode == 4:  # ADD
                    print(f"ADD: A={a}, B={b}, C={c}")
                    if b >= len(memory) or c >= len(memory):
                        raise ValueError(f"ADD: Address B ({b}) or C ({c}) out of bounds.")
                    memory[b] = memory[b] + memory[c]  # Сложение значений в ячейках B и C
                    print(f"Memory after ADD: {memory[:50]}")

                elif opcode == 5:  # XOR
                    print(f"XOR: A={a}, B={b}, C={c}")
                    if b >= len(memory) or c >= len(memory):
                        raise ValueError(f"XOR: Address B ({b}) or C ({c}) out of bounds.")
                    memory[b] = memory[b] ^ memory[c]  # Побитовая операция XOR
                    print(f"Memory after XOR: {memory[:50]}")

                else:
                    raise ValueError(f"Unknown opcode: {opcode}")

            except ValueError as e:
                print(f"Error processing instruction: {e}")
                continue

    # Увеличьте диапазон памяти, если нужно увидеть больше данных
    result["memory"] = memory[0:256]  
    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)



if __name__ == "__main__":
    import sys
    source = "program.txt"
    binary = "program.bin"
    log = "program_log.json"
    result = "result.json"

    # Ассемблирование
    assemble(source, binary, log)

    # Интерпретация
    interpret(binary, memory_range=(0, 50), result_path=result)

    print("Ассемблирование завершено. Лог в 'program_log.json'.")
    print("Интерпретация завершена. Результат в 'result.json'.")

