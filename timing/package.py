import re
from sys import byteorder


class PackageManager:
    """
        FEND (frame end) - symbol indicates frame starts
        FESC (frame escape) - symbol indicates something was replaced
        TFEND (transposed frame end) - symbol replaces real FEND
        TFESC (transposed frame escape) - symbol replaces real FESC
    """

    def __init__(self, n, data):
        self.__n = n

        self.__FEND = "@" + chr(ord('a') + (n - 1))
        self.__FESC = "$"
        self.__TFEND = "*"
        self.__TFESC = "%"
        self.__EOD = "\\n"
        self.__data = data

    def get_controlls(self):
        return {"end": self.__FESC + self.__TFEND,
                "esc": self.__FESC + self.__TFESC,
                "eod": self.__EOD}

    def transform_data_to_package(self):
        self.__data = re.sub(re.escape(self.__FESC), self.__FESC + self.__TFESC, self.__data)
        self.__data = re.sub(re.escape(self.__FEND), self.__FESC + self.__TFEND, self.__data)
        if len(self.__data) % self.__n != 0:
            self.__data += "\\n"
        while len(self.__data) % self.__n != 0:
            self.__data += "0"
        return self.__data

    def transform_package_data_to_real(self):
        # print(f"WAS {self.__data}")
        eol = self.__data.find("\\n")
        if eol != -1:
            self.__data = self.__data[0:eol]
        self.__data = re.sub(re.escape(self.__FESC) + re.escape(self.__TFEND), self.__FEND, self.__data)
        self.__data = re.sub(re.escape(self.__FESC) + re.escape(self.__TFESC), self.__FESC, self.__data)
        # print(f"NOW {self.__data}")

        return self.__data

def get_data_from_package(data):
    return data[4:-1]


class Package:

    def __init__(self, *args):
        if len(args) == 3:  # Первый вариант конструктора
            self.__n = args[0]
            self.flag = "@"
            self.destination_address = "0"
            self.source_address = f"{args[1][-1]}"
            self.data = args[2]
            self.fcs = "0"
            self.package = ""
            self.form_package()
        elif len(args) == 1 and isinstance(args[0], str):  # Второй вариант конструктора
            self.data = get_data_from_package(args[0])
            self.fcs = args[0][-8:]
            self.check_control_sum()
        else:
            raise ValueError("Invalid arguments")

    def set_fcs(self):
        binary_string = int.from_bytes(self.data.encode(), byteorder="big")
        divider = int("111100111", 2)
        result = binary_string
        while result > divider & result.bit_length() - divider.bit_length():
            shifted_divider = divider << result.bit_length() - divider.bit_length()
            result = result ^ shifted_divider
        self.fcs = result
        print(f"FCS after setting: {self.fcs}")

    def form_package(self):
        task_num = self.__n - 1
        self.flag += chr(ord('a') + task_num)
        self.package += self.flag
        self.package += self.destination_address
        self.package += self.source_address
        self.package += self.data
        self.set_fcs()
        self.package += chr(self.fcs )

    def check_control_sum(self, polynomial: str = "111100111", output_length: int = 23*8):
        # Шаг 1: Инициализация
        divider = int(polynomial, 2)  # Полином
        binary_string = int.from_bytes(self.data.encode(), byteorder="big")  # Основное число
        fsc_binary = int.from_bytes(self.fcs.encode(), byteorder="big")  # FCS
        binary_string <<= fsc_binary.bit_length()  # Сдвигаем для подготовки
        final_binary_string = binary_string + fsc_binary

        def count_ones(x):
            """Функция для подсчёта количества единиц в числе."""
            return bin(x).count('1')

        def cyclic_shift_left(x, bit_length):
            """Циклический сдвиг числа влево на 1 бит."""
            return ((x << 1) & ((1 << bit_length) - 1)) | (x >> (bit_length - 1))

        def cyclic_shift_right(x, bit_length):
            """Циклический сдвиг числа вправо на 1 бит."""
            return (x >> 1) | ((x & 1) << (bit_length - 1))

        result = final_binary_string
        shift_count = 0  # Счётчик циклических сдвигов

        # Шаг 2: Основной цикл деления
        while True:
            # "Делим" и получаем остаток
            while result >= divider and result.bit_length() >= divider.bit_length():
                shifted_divider = divider << (result.bit_length() - divider.bit_length())
                result ^= shifted_divider  # XOR для деления

            # Проверяем количество единиц в остатке
            if count_ones(result) <= 1:
                break  # Условие завершения: в остатке <= 1 единица

            # Циклический сдвиг final_binary_string
            final_binary_string = cyclic_shift_left(final_binary_string, final_binary_string.bit_length())
            shift_count += 1  # Увеличиваем счётчик сдвигов
            result = final_binary_string  # Пересчитываем остаток заново

        # Шаг 4: XOR с остатком и финальный результат
        final_result = final_binary_string ^ result

        # Шаг 3: Циклический сдвиг вправо (если были сдвиги влево)
        for _ in range(shift_count):
            final_binary_string = cyclic_shift_right(final_binary_string, final_binary_string.bit_length())

        # Шаг 5: Обрезка до 30 бит
        final_result &= (1 << output_length) - 1  # Маска для сохранения 30 бит

        self.data, self.fcs = split_final_result(final_result)

        return final_result

def split_final_result(final_result, data_bits_length=22 * 8, fcs_bits_length=1 * 8):
    # Извлекаем FCS (младшие 8 бит)
    fcs_bits = final_result & ((1 << fcs_bits_length) - 1)  # Маска для младших бит
    # Извлекаем данные (первые 22 бита)
    data_bits = final_result >> fcs_bits_length  # Сдвиг вправо на длину FCS

    # Преобразуем данные и FCS в строки символов
    def bits_to_string(bits, length):
        """Преобразует битовое число в строку символов заданной длины"""
        byte_str = ''
        for i in range(length // 8):
            byte_value = (bits >> (8 * (length // 8 - i - 1))) & 0xFF
            byte_str += chr(byte_value)
        return byte_str

    # Данные в строке
    data_str = bits_to_string(data_bits, data_bits_length)
    # FCS в строке (один байт)
    fcs_str = chr(fcs_bits)  # Преобразуем числовое значение FCS в символ
    print(f"DATA {data_str} : FCS {fcs_str}")

    return data_str, fcs_str


