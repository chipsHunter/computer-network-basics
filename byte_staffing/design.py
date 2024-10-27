import math
import queue
import time
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import BOTTOM

from package import PackageManager, Package, get_data_from_package
from ports import get_available_ports, PortToTransmit, PortToReceive


class MyMainWindow:
    def __init__(self, root):

        self.root = root
        self.transmit_thread = None
        self.receive_thread = None
        self.transmit_port = None
        self.receive_port = None
        self.ports = None

        self.transmitted_portions = 0
        self.received_data = ""
        self.variant = 22

        self.transmitter_field = None
        self.receiver_field = None
        self.combo_box_first = None
        self.combo_box_second = None
        self.transmitted_portions_label = None
        self.transmitter_scrollbar = None
        self.receiver_scrollbar = None
        self.packages = None

        self.setup_ui()

    def setup_ui(self):

        FONT = ("Courier", 14)
        SMALL_FONT = ("Courier", 12)
        BGCOLOR = "#7e9183"
        FGCOLOR = "#C2ACA9"

        self.root.title("Коммуникационная программа: топология x -> x+1")
        self.root.geometry("950x570")
        self.root.configure(bg=BGCOLOR)
        self.root.resizable(width=False, height=False)

        input_output_frame = tk.Frame(self.root, bg=BGCOLOR)
        input_output_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")

        # -------- ОКНО ВВОДА ---------------------------------
        input_frame = tk.Frame(input_output_frame, bd=2, relief='groove', bg=FGCOLOR)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(input_frame, text="Окно ввода", bg="#FFFFFF").pack(padx=10, pady=5)
        self.transmitter_field = tk.Text(input_frame, width=40, height=10)
        self.transmitter_field.pack(side='left', padx=10, pady=5, fill="both", expand=True)
        self.transmitter_scrollbar = tk.Scrollbar(input_frame, command=self.transmitter_field.yview)
        self.transmitter_scrollbar.pack(side='right', fill='y')
        self.transmitter_field['yscrollcommand'] = self.transmitter_scrollbar.set

        # ----- ОКНО ВЫВОДА -------------------------------------------------
        output_frame = tk.Frame(input_output_frame, bd=2, relief='groove', bg=FGCOLOR)
        output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(output_frame, text="Окно вывода", bg="#FFFFFF").pack(padx=10, pady=5)
        self.receiver_field = tk.Text(output_frame, width=40, height=10)
        self.receiver_field.pack(side='left', padx=10, pady=5, fill="both", expand=True)
        self.receiver_scrollbar = tk.Scrollbar(output_frame, command=self.receiver_field.yview)
        self.receiver_scrollbar.pack(side='right', fill='y')
        self.receiver_field['yscrollcommand'] = self.receiver_scrollbar.set

        # Настройки для равномерного распределения окна ввода и вывода
        input_output_frame.grid_columnconfigure(0, weight=1)
        input_output_frame.grid_columnconfigure(1, weight=1)
        input_output_frame.grid_rowconfigure(0, weight=1)

        # ------- ОКНО УПРАВЛЕНИЯ ------------------------------------------------------
        control_frame = tk.Frame(self.root, bg=FGCOLOR, bd=2, relief=tk.GROOVE)
        control_frame.grid(row=1, column=0, padx=25, pady=25, sticky="nsew")

        # Окно управления
        control_label = tk.Label(control_frame, text="Окно управления", font=FONT, bg="#FFFFFF")
        control_label.pack(anchor="w", padx=10, pady=5)

        # Комбо-боксы для отправителя и получателя
        transmit_label = tk.Label(control_frame, text="Отправитель", font=SMALL_FONT, bg="#FFFFFF")
        transmit_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_first = ttk.Combobox(control_frame, font=SMALL_FONT)
        self.combo_box_first.pack(anchor="w", padx=10, pady=5)

        receive_label = tk.Label(control_frame, text="Получатель", font=SMALL_FONT, bg="#FFFFFF")
        receive_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_second = ttk.Combobox(control_frame, font=SMALL_FONT)
        self.combo_box_second.pack(anchor="w", padx=10, pady=5)

        # -----ОКНО СОСТОЯНИЯ---------------------------------------------
        status_frame = tk.Frame(self.root, bg=FGCOLOR, bd=2, relief=tk.GROOVE)
        status_frame.grid(row=1, column=1, padx=25, pady=25, sticky="nsew")

        # Левая часть с информацией о портах и переданными порциями
        text_frame = tk.Frame(status_frame, bg=FGCOLOR)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=10)

        status_label = tk.Label(text_frame, text="Окно состояния", font=FONT, bg="#FFFFFF")
        status_label.pack(side=tk.TOP, anchor="w", padx=15, pady=10)

        port_info = tk.Label(text_frame,
                             text="Скорость передачи данных: 9600\nБит данных: 8\nПаритет: нет\nСтоп-биты: 1",
                             font=SMALL_FONT, bg="#FFFFFF", justify=tk.LEFT)
        port_info.pack(side=tk.TOP, anchor="nw", padx=15, pady=10)

        self.transmitted_portions_label = tk.Label(text_frame, text=f"Передано порций: {self.transmitted_portions}",
                                                   font=SMALL_FONT, bg="#FFFFFF", justify=tk.LEFT)
        self.transmitted_portions_label.pack(side=tk.TOP, anchor="nw", padx=15, pady=5)

        # Правая часть со структурой кадра и прокруткой
        package_frame = tk.Frame(status_frame, bg=FGCOLOR)
        package_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=10, expand=True)

        package_label = tk.Label(package_frame, text="Структура кадра", font=SMALL_FONT, bg="#FFFFFF")
        package_label.pack(side=tk.TOP, anchor="w", padx=10, pady=10)

        # Текстовое поле для структуры кадра и скроллбар
        self.packages = tk.Text(package_frame, width=30, height=10)
        self.packages.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        package_scrollbar = tk.Scrollbar(package_frame, command=self.packages.yview)
        package_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.packages['yscrollcommand'] = package_scrollbar.set

        # Настройки grid для равномерного распределения пространства между окнами
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # ------ РАБОТА С ПОРТАМИ ----------------------------------------------------------------------------

        self.ports = get_available_ports()
        available_options = self.ports
        available_options.insert(0, "Выберите порт")
        if self.ports:
            self.combo_box_first['values'] = available_options
            self.set_current_combo_box(self.combo_box_first, 0)
            self.set_transmit_port(available_options[0])

            self.combo_box_second['values'] = available_options
            self.set_current_combo_box(self.combo_box_second, 0)
            self.set_receive_port(available_options[0])
        else:
            messagebox.showerror("Error", "No available ports.")

        self.connect_signals()

    def port_chosen(self, port):
        return port != "Выберите порт"

    def set_null_port(self, port, thread):
        thread.stop()
        thread = None
        port = None

    def set_transmit_port(self, port):
        self.set_current_combo_box(self.combo_box_first,
                                   self.combo_box_first['values'].index(port))

        if self.transmit_port:
            self.set_null_port(self.transmit_port, self.transmit_thread)

        if self.port_chosen(port):
            self.open_transmit_port(port)

        self.lock_transmitter_if_transmit_port_not_chosen()

        self.update_receive_ports_list()

    def get_available_receive_ports(self):
        ports = get_available_ports()
        if self.transmit_port:
            excluded_ports = [self.transmit_port, f"/dev/ttyS{int(self.transmit_port[-1]) + 1}"]
            return [port for port in self.ports if port not in excluded_ports]
        else:
            return ports

    def update_receive_ports_list(self):
        available_ports = self.get_available_receive_ports()
        if not self.receive_port:
            self.setup_combo_box(self.combo_box_second, available_ports)
        elif self.receive_port != available_ports[2]:
            self.set_null_port(self.receive_port, self.receive_thread)
            self.setup_combo_box(self.combo_box_second, available_ports)

    def open_transmit_port(self, port):
        self.transmit_port = port
        self.transmit_thread = PortToTransmit(port, self.set_transmitted_bytes, self.handle_port_error)
        self.transmit_thread.start()

    def set_receive_port(self, port):
        if self.receive_port:
            self.receive_thread.stop()
            self.receive_port = None
            self.receive_thread = None
        if port != "Выберите порт":
            self.receive_port = port
            self.receive_thread = PortToReceive(port, self.display_received_data, self.handle_port_error)
            self.receive_thread.start()

        self.combo_box_second.current(self.combo_box_second['values'].index(port))

    def send_data(self):
        message = self.transmitter_field.get("1.0", 'end-1c').strip()
        self.transmitter_field.delete(1.0, tk.END)

        # data_in_buffer = self.receiver_field.get("1.0", 'end')
        self.receiver_field.insert(tk.END, "\n")
        self.received_data = ""

        manager = PackageManager(self.variant, message)
        message_to_transmit = manager.transform_data_to_package()
        length = len(message_to_transmit)

        for i in range(length // self.variant):
            package_part = message_to_transmit[i * self.variant:(i + 1) * self.variant]
            package_to_transmit = Package(self.variant, self.transmit_port, package_part)
            print(f"{package_to_transmit.package} : {package_part}")
            if self.transmit_thread:
                self.transmit_thread.write(package_to_transmit.package)
                self.print_package(package_to_transmit.package)
                time.sleep(0.2)

    # ------- ИНТЕРФЕЙС ---------------------------------------------------------------------------

    # ------- ОКНО СОСТОЯНИЯ ----------------------------------------------------------------------

    def set_transmitted_bytes(self):
        self.transmitted_portions += 1
        self.transmitted_portions_label.config(text=f"Передано порций: {self.transmitted_portions}")

    # ------- ДЕБАГ ------------------------------------------------------------------------------

    def handle_port_error(self, is_receiver):
        if is_receiver:
            self.setup_combo_box(self.combo_box_second,
                                 self.get_available_receive_ports()
                                 )
            self.set_current_combo_box(self.combo_box_second, 0)
        else:
            self.setup_combo_box(self.combo_box_first,
                                 get_available_ports()
                                 )
            self.set_current_combo_box(self.combo_box_first, 0)

    # ------ КОМБО БОКСЫ ----------------------------------------------------------------------

    def connect_signals(self):
        self.combo_box_first.bind("<Button-1>", lambda e: self.check_combo_box(self.combo_box_first,
                                                                               self.transmit_port,
                                                                               self.transmit_thread,
                                                                               [port for port in (
                                                                                       get_available_ports() + [
                                                                                   self.transmit_port]) if
                                                                                port is not None]
                                                                               )
                                  )
        self.combo_box_second.bind("<Button-1>", lambda e: self.check_combo_box(self.combo_box_second,
                                                                                self.receive_port,
                                                                                self.receive_thread,
                                                                                self.get_available_receive_ports()
                                                                                )
                                   )
        self.combo_box_first.bind("<<ComboboxSelected>>", lambda e: self.set_transmit_port(self.combo_box_first.get()))
        self.combo_box_second.bind("<<ComboboxSelected>>", lambda e: self.set_receive_port(self.combo_box_second.get()))
        self.transmitter_field.bind("<Return>", lambda e: self.send_data())

    def display_received_data(self, package):

        self.receiver_field.config(state='normal')  # Разрешаем редактирование
        data = self.read_from_package(package)
        print(f"READ DATA : {data}")
        self.received_data += data
        # self.receiver_field.delete(1.0, tk.END)
        self.receiver_field.insert(tk.END, data)  # Вставляем текст
        # self.receiver_field.config(state='disabled')  # Возвращаем в режим "только для чтения"
        self.receiver_field.yview(tk.END)

    def print_package(self, package):
        self.packages.config(state=tk.NORMAL)
        self.packages.insert(tk.END, "\n")

        # Получаем подстроки для выделения
        manager = PackageManager(self.variant, package)
        replacements = manager.get_controlls().values()

        # Разбиваем пакет на обычные и замененные части
        start = 0
        for i in range(len(package)):
            for replacement in replacements:
                if package[i:i + len(replacement)] == replacement:
                    # Вставляем обычный текст перед заменённой частью
                    if start < i:
                        self.packages.insert(tk.END, package[start:i])
                    # Вставляем жирный текст для замененной подстроки
                    self.packages.insert(tk.END, replacement, 'bold')
                    start = i + len(replacement)

        # Вставляем оставшийся текст
        if start < len(package):
            self.packages.insert(tk.END, package[start:])

        # Настраиваем жирный шрифт
        self.packages.tag_configure('bold', font=("Courier", 12, "bold"))

        self.packages.config(state=tk.DISABLED)

    def read_from_package(self, package):

        raw_data = get_data_from_package(package)
        manager = PackageManager(self.variant, raw_data)
        real_data = manager.transform_package_data_to_real()

        return real_data

    def setup_combo_box(self, combo_box, available_ports):
        real_list = ["Выберите порт"] + available_ports
        combo_box['values'] = real_list
        combo_box.current(0)

    def check_combo_box(self, combobox, port, thread, portlist):
        self.setup_combo_box(combobox, portlist)
        print(f"{port}: {portlist}")

        if port and port not in portlist:
            self.set_null_port(port, thread)
            self.set_current_combo_box(combobox, 0)
        elif port and port in portlist:
            self.set_current_combo_box(combobox,
                                       portlist.index(port) + 1)

    def set_current_combo_box(self, combo_box, index):
        combo_box.current(index)

    # ------ ПОЛЕ ВВОДА ------------------

    def on_entry_click(self, event):
        if self.transmitter_field.get() == "Введите текст здесь...":
            self.transmitter_field.delete(0, tk.END)
            self.transmitter_field.config(fg="black")

    def on_focusout(self, event):
        if self.transmitter_field.get() == "":
            self.transmitter_field.insert(0, "Введите текст здесь...")
            self.transmitter_field.config(fg="grey")

    def lock_transmitter_if_transmit_port_not_chosen(self):
        if self.transmit_port:
            self.transmitter_field.config(state="normal")
        else:
            self.transmitter_field.config(state="disabled")

    # ------- ВЫХОД --------------------------------------------------------------

    def close(self):
        if self.transmit_thread:
            self.transmit_thread.stop()
        if self.receive_thread:
            self.receive_thread.stop()
        self.root.quit()
