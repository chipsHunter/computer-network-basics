import threading
import time

import serial.tools.list_ports


def get_available_ports():
    available_ports = []
    ports = serial.tools.list_ports.comports()

    for port in ports:
        try:
            s = serial.Serial(port.device, exclusive=True, write_timeout=0, timeout=0)
            s.close()  # Закрываем, если успешно открыли
            available_ports.append(port.device)
        except (OSError, serial.SerialException) as e:
            # print(f"Ошибка при открытии {port}: {e}")
            continue

    return available_ports


class PortToReceive(threading.Thread):

    def __init__(self, port, display_data_callback, handler):
        super().__init__()
        self.port = port
        self._running = False
        self.data_callback = display_data_callback
        self.handle_port_error = handler

    def run(self):
        self._running = True
        try:
            with serial.Serial(self.port, exclusive=True, timeout=0.5) as ser:
                while self._running:
                    if ser.in_waiting:
                        data = ser.readall().decode('utf-8').strip()
                        self.data_callback(data)
                    time.sleep(0.1)
        except serial.SerialException as e:
            self.handle_port_error(f"{self.port}: {e}", True)
            self.port = None
            self._running = False

    def stop(self):
        self._running = False


class PortToTransmit(threading.Thread):

    def __init__(self, port, display_transmitted_bytes, handler):
        super().__init__()
        self.port = port
        self._running = False  # Переменная для управления потоком
        self.transmitted_bytes_callback = display_transmitted_bytes
        self.ser = None
        self.handle_port_error = handler

    def run(self):
        self._running = True
        try:
            # Открываем порт с эксклюзивным доступом для записи один раз
            self.ser = serial.Serial(self.port, exclusive=True, timeout=0.5)
            while self._running:
                time.sleep(0.001)  # Поток работает, ожидая отправки данных
        except serial.SerialException as e:
            self.handle_port_error(f"{self.port}: {e}", False)
            self._running = False
            self.port = None

    def write(self, message):
        if self._running and self.ser and self.ser.is_open:
            try:
                # Используем уже открытый порт для отправки данных
                self.ser.write(message.encode('utf-8'))  # Отправка сообщения
                self.transmitted_bytes_callback()  # Уведомляем об отправке
                time.sleep(0.01)  # Короткая пауза после отправки
            except serial.SerialException as e:
                print(f"Ошибка при отправке данных: {e}")
        else:
            print("Порт не открыт для передачи данных.")

    def stop(self):
        self._running = False
        if self.ser:
            self.ser.close()  # Закрываем порт при остановке потока
