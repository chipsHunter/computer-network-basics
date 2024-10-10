import os
import time

import serial.tools.list_ports
from PyQt5.QtCore import pyqtSignal, QThread

def get_available_ports():
    available_ports = []
    ports = serial.tools.list_ports.comports()

    for port in ports:
        try:
            s = serial.Serial(port.device)
            s.close()  # Закрываем, если успешно открыли
            available_ports.append(port.device)
        except (OSError, serial.SerialException) as e:
            # print(f"Ошибка при открытии {port}: {e}")
            continue

    return available_ports

class PortToRead(QThread):

    def __init__(self, port, display_data_callback, display_received_bytes_callback):
        super().__init__()
        self.port = port
        self._running = False
        self.data_callback = display_data_callback
        self.received_bytes_callback = display_received_bytes_callback

    def run(self):
        self._running = True
        with serial.Serial(self.port, timeout=0.5) as ser:
            while self._running:
                if ser.in_waiting:
                    data = ser.readall().decode('utf-8').strip()
                    self.data_callback(data)
                    self.received_bytes_callback(len(data))
                time.sleep(0.1)

    def stop(self):
        self._running = False
        self.exit()
        self.wait(1)

class PortToWrite(QThread):

    def __init__(self, port, display_transmitted_bytes):
        super().__init__()
        self.port = port
        self._running = False  # Переменная для управления потоком
        self.transmitted_bytes_callback = display_transmitted_bytes

    def write(self, message):
        if self._running:
            with serial.Serial(self.port) as ser:
                ser.write(message.encode('utf-8'))
                self.transmitted_bytes_callback(len(message))
                time.sleep(0.01)

    def run(self):
        self._running = True
        while self._running:
            time.sleep(0.0001)

    def stop(self):
        self._running = False
        self.exit()
        self.wait(1)