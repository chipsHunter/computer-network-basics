import queue
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox

from ports import get_available_ports, PortToWrite, PortToRead

class MyMainWindow:
    def __init__(self, root):
        self.root = root
        self.transmit_thread = None
        self.receive_thread = None
        self.transmit_port = None
        self.receive_port = None
        self.ports = None

        self.input_field = None
        self.output_field = None
        self.combo_box_first = None
        self.combo_box_second = None
        self.transmit_bytes_label = None
        self.receive_bytes_label = None

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Коммуникационная программа: топология x -> x+1")
        self.root.geometry("700x500")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(width=False, height=False)

        # Создаем фреймы для различных секций
        top_frame = tk.Frame(self.root, bg="#FFFFFF")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        left_frame = tk.Frame(top_frame, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = tk.Frame(top_frame, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # -----ОКНО СОСТОЯНИЯ---------------------------------------------
        status_frame = tk.Frame(self.root, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        status_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        transceiver_frame = tk.Frame(status_frame, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        transceiver_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        transmit_info = tk.Frame(transceiver_frame, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        transmit_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        receive_info = tk.Frame(transceiver_frame, bg="#FFFFFF", bd=2, relief=tk.GROOVE)
        receive_info.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.transmit_bytes_label = tk.Label(transmit_info, text="Отправлено 0 байт", font=("Courier", 14), bg="#FFFFFF")
        self.transmit_bytes_label.pack(anchor="w", padx=10, pady=5)
        self.receive_bytes_label = tk.Label(receive_info, text="Принято 0 байт", font=("Courier", 14), bg="#FFFFFF")
        self.receive_bytes_label.pack(anchor="w", padx=10, pady=5)

        port_info = tk.Label(status_frame, text="Скорость передачи данных: 9600\n8-битный\nЗадержка: 0.5с\n", font=("Courier", 14), bg="#FFFFFF", justify=tkinter.LEFT)
        port_info.pack(side=tk.BOTTOM, padx=10, pady=5)

        # ------------------------------------------------------------------

        # Окно ввода (левая часть)
        input_label = tk.Label(left_frame, text="Окно ввода", font=("Courier", 14), bg="#FFFFFF")
        input_label.pack(anchor="w", padx=10, pady=5)

        self.input_field = tk.Entry(left_frame, width=50)
        self.input_field.insert(0, "Введите текст здесь...")
        self.input_field.config(fg="grey")  # Сначала текст серый
        self.input_field.pack(anchor="w", padx=10, pady=5)

        # Привязываем события к полю ввода
        self.input_field.bind("<FocusIn>", self.on_entry_click)
        self.input_field.bind("<FocusOut>", self.on_focusout)

        # Окно вывода и количество символов (левая часть)
        output_label = tk.Label(left_frame, text="Окно вывода", font=("Courier", 14), bg="#FFFFFF")
        output_label.pack(anchor="w", padx=10, pady=5)

        self.output_field = tk.Entry(left_frame, width=50, state='readonly')
        self.output_field.pack(anchor="w", padx=10, pady=5)

        # Окно управления (правая часть)
        control_label = tk.Label(right_frame, text="Окно управления", font=("Courier", 14), bg="#FFFFFF")
        control_label.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для отправителя
        transmit_label = tk.Label(right_frame, text="Отправитель", font=("Courier", 12), bg="#FFFFFF")
        transmit_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_first = ttk.Combobox(right_frame, font=("Courier", 12))
        self.combo_box_first.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для получателя
        receive_label = tk.Label(right_frame, text="Получатель", font=("Courier", 12), bg="#FFFFFF")
        receive_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_second = ttk.Combobox(right_frame, font=("Courier", 12))
        self.combo_box_second.pack(anchor="w", padx=10, pady=5)

        # Окно состояния
        status_label = tk.Label(status_frame, text="Окно состояния", font=("Courier", 14), bg="#FFFFFF")
        status_label.pack(anchor="w", padx=10, pady=10)

        #----РАБОТА С ПОРТАМИ----------------------------------------------------------------------------

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

        self.lock_input_if_transmit_port_not_chosen()

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
            if self.transmit_port:
                self.set_receive_port(available_ports[2])
        elif self.receive_port != available_ports[2]:
            self.set_null_port(self.receive_port, self.receive_thread)
            self.setup_combo_box(self.combo_box_second, available_ports)
            self.set_receive_port(available_ports[2])

    def open_transmit_port(self, port):
        self.transmit_port = port
        self.transmit_thread = PortToWrite(port, self.set_transmitted_bytes)
        self.transmit_thread.start()

    def set_receive_port(self, port):
        if self.receive_port:
            self.receive_thread.stop()
            self.receive_port = None
            self.receive_thread = None
        if port != "Выберите порт":
            self.receive_port = port
            self.receive_thread = PortToRead(port, self.display_received_data, self.set_received_bytes)
            self.receive_thread.start()

        self.combo_box_second.current(self.combo_box_second['values'].index(port))

    def send_data(self):
        message = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)
        if self.transmit_thread:
            self.transmit_thread.write(message)

    #-------ИНТЕРФЕЙС---------------------------------------------------------------------------
    
    def set_current_combo_box(self, combo_box, index):
        combo_box.current(index)
        
    def lock_input_if_transmit_port_not_chosen(self):
        if self.transmit_port:
            self.input_field.config(state="normal")
        else:
            self.input_field.config(state="readonly")

    def clear_combo_box_except_first(self, combo_box):
        combo_box['values'] = combo_box['values'][:1]

    def set_received_bytes(self, rbytes):
        self.receive_bytes_label.config(text=f"Принято {rbytes} байт")

    def set_transmitted_bytes(self, tbytes):
        self.transmit_bytes_label.config(text=f"Отправлено {tbytes} байт")

    def connect_signals(self):
        self.combo_box_first.bind("<<ComboboxSelected>>", lambda e: self.set_transmit_port(self.combo_box_first.get()))
        self.combo_box_second.bind("<<ComboboxSelected>>", lambda e: self.set_receive_port(self.combo_box_second.get()))
        self.input_field.bind("<Return>", lambda e: self.send_data())

    def display_received_data(self, data):
        self.output_field.config(state='normal')
        self.output_field.delete(0, tk.END)
        self.output_field.insert(0, data)
        self.output_field.config(state='readonly')

    def setup_combo_box(self, combo_box, available_ports):
        self.clear_combo_box_except_first(combo_box)
        combo_box['values'] = available_ports
        combo_box.current(0)

    def on_entry_click(self, event):
        if self.input_field.get() == "Введите текст здесь...":
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg="black")

    def on_focusout(self, event):
        if self.input_field.get() == "":
            self.input_field.insert(0, "Введите текст здесь...")
            self.input_field.config(fg="grey")

    def close(self):
        if self.transmit_thread:
            self.transmit_thread.stop()
        if self.receive_thread:
            self.receive_thread.stop()
        self.root.quit()
