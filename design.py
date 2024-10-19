import queue
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox

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

        self.input_field = None
        self.output_field = None
        self.combo_box_first = None
        self.combo_box_second = None
        self.transmitted_portions_label = None
        self.debug_label = None

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Коммуникационная программа: топология x -> x+1")
        self.root.geometry("700x400")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(width=False, height=False)

        FONT = ("Courier", 14)
        SMALL_FONT = ("Courier", 12)

        # Создаем фреймы для различных секций
        top_frame = tk.Frame(self.root, bg="#FFFFFF")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        left_frame = tk.Frame(top_frame, bg="#7e9183", bd=2, relief=tk.GROOVE, height=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        right_frame = tk.Frame(top_frame, bg="#7e9183", bd=2, relief=tk.GROOVE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # -----ОКНО СОСТОЯНИЯ---------------------------------------------
        status_frame = tk.Frame(self.root, bg="#7e9183", bd=2, relief=tk.GROOVE, height=100)
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        status_label = tk.Label(status_frame, text="Окно состояния", font=FONT, bg="#FFFFFF")
        status_label.pack(anchor="w", padx=10, pady=10)

        port_info = tk.Label(status_frame,
                             text="Скорость передачи данных: 9600\nБит данных: 8\nПаритет: нет\nСтоп-биты: 1",
                             font=SMALL_FONT, bg="#FFFFFF", justify=tkinter.LEFT)
        port_info.pack(side=tk.BOTTOM, anchor="nw", padx=50, pady=5)

        self.transmitted_portions_label = tk.Label(status_frame, text=f"Передано порций: {self.transmitted_portions}",
                                                   font=SMALL_FONT, bg="#FFFFFF", justify=tkinter.LEFT)
        self.transmitted_portions_label.pack(side=tk.BOTTOM, anchor="nw", padx=50, pady=5)

        # ------ ОТЛАДОЧНОЕ ОКНО ------------------------------------------

        debug_frame = tk.Frame(self.root, bg="#7e9183", bd=2, relief=tk.GROOVE)
        debug_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)  # Новый фрейм справа от остальных

        debug_label = tk.Label(debug_frame, text="Отладочное окно", font=FONT, bg="#FFFFFF")
        debug_label.pack(anchor="w", padx=10, pady=10)

        self.debug_label = tk.Label(debug_frame, text="", font=SMALL_FONT, bg="#FFFFFF", fg="red", width=100, height=100, justify=tkinter.LEFT)  # Лейбл для ошибок
        self.debug_label.pack(side=tk.TOP, anchor="nw", padx=10, pady=5)

        #-------------------------------------------------------------------

        # Окно ввода (левая часть)
        input_label = tk.Label(left_frame, text="Окно ввода", font=FONT, bg="#FFFFFF")
        input_label.pack(anchor="w", padx=10, pady=5)

        self.input_field = tk.Entry(left_frame, width=50)
        self.input_field.insert(0, "Введите текст здесь...")
        self.input_field.config(fg="grey")  # Сначала текст серый
        self.input_field.pack(anchor="w", padx=10, pady=5)

        # Привязываем события к полю ввода
        self.input_field.bind("<FocusIn>", self.on_entry_click)
        self.input_field.bind("<FocusOut>", self.on_focusout)

        # Окно вывода и количество символов (левая часть)
        output_label = tk.Label(left_frame, text="Окно вывода", font=FONT, bg="#FFFFFF")
        output_label.pack(anchor="w", padx=10, pady=5)

        self.output_field = tk.Entry(left_frame, width=50, bg="#FFFFFF")
        self.output_field.pack(side="top", padx=10, pady=5)

        # Создаём горизонтальную прокрутку
        h_scrollbar = tk.Scrollbar(left_frame, orient="horizontal", command=self.output_field.xview)
        h_scrollbar.pack(side="bottom", fill="x")

        # Связываем прокрутку с Entry
        self.output_field.config(xscrollcommand=h_scrollbar.set)

        # Окно управления (правая часть)
        control_label = tk.Label(right_frame, text="Окно управления", font=FONT, bg="#FFFFFF")
        control_label.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для отправителя
        transmit_label = tk.Label(right_frame, text="Отправитель", font=SMALL_FONT, bg="#FFFFFF")
        transmit_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_first = ttk.Combobox(right_frame, font=SMALL_FONT)
        self.combo_box_first.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для получателя
        receive_label = tk.Label(right_frame, text="Получатель", font=SMALL_FONT, bg="#FFFFFF")
        receive_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_second = ttk.Combobox(right_frame, font=("Courier", 12))
        self.combo_box_second.pack(anchor="w", padx=10, pady=5)

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
        message = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)
        if self.transmit_thread:
            self.transmit_thread.write(message)

    # ------- ИНТЕРФЕЙС ---------------------------------------------------------------------------

    # ------- ОКНО СОСТОЯНИЯ ----------------------------------------------------------------------

    def set_transmitted_bytes(self):
        self.transmitted_portions += 1
        self.transmitted_portions_label.config(text=f"Передано порций: {self.transmitted_portions}")

    # ------- ДЕБАГ ОКНО -------------------------------------------------------------------------

    def handle_port_error(self, message, isReceiver):
        self.debug_label.config(text=message)
        if isReceiver:
            self.setup_combo_box(self.combo_box_second,
                                 self.get_available_receive_ports()
                                 )
        else:
            self.setup_combo_box(self.combo_box_first,
                                 get_available_ports()
                                 )

    # ------ КОМБО БОКСЫ ----------------------------------------------------------------------

    def connect_signals(self):
        self.combo_box_first.bind("<Button-1>", lambda e: self.check_combo_box(self.combo_box_first,
                                                                               self.transmit_port,
                                                                               self.transmit_thread,
                                                                               [port for port in (get_available_ports() + [self.transmit_port]) if port is not None]
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
        self.input_field.bind("<Return>", lambda e: self.send_data())

    def display_received_data(self, data):
        self.output_field.config(state='normal')  # Разрешаем редактирование
        self.output_field.insert(tk.END, data + "\n")  # Вставляем текст
        # self.output_field.config(state='disabled')  # Возвращаем в режим "только для чтения"
        self.output_field.yview(tk.END)

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
        if self.input_field.get() == "Введите текст здесь...":
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg="black")

    def on_focusout(self, event):
        if self.input_field.get() == "":
            self.input_field.insert(0, "Введите текст здесь...")
            self.input_field.config(fg="grey")

    def lock_input_if_transmit_port_not_chosen(self):
        if self.transmit_port:
            self.input_field.config(state="normal")
        else:
            self.input_field.config(state="readonly")

    # ------- ВЫХОД --------------------------------------------------------------

    def close(self):
        if self.transmit_thread:
            self.transmit_thread.stop()
        if self.receive_thread:
            self.receive_thread.stop()
        self.root.quit()