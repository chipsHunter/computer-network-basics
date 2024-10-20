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

        self.transmitter_field = None
        self.receiver_field = None
        self.combo_box_first = None
        self.combo_box_second = None
        self.transmitted_portions_label = None
        self.transmitter_scrollbar = None
        self.receiver_scrollbar = None

        self.setup_ui()

    def setup_ui(self):

        FONT = ("Courier", 14)
        SMALL_FONT = ("Courier", 12)
        BGCOLOR = "#7e9183"
        FGCOLOR = "#C2ACA9"

        self.root.title("Коммуникационная программа: топология x -> x+1")
        self.root.geometry("840x520")
        self.root.configure(bg=BGCOLOR)
        self.root.resizable(width=False, height=False)

        input_output_frame = tk.Frame(self.root, bg=BGCOLOR)
        input_output_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=15)
        # -------- ОКНО ВВОДА ---------------------------------

        input_frame = tk.Frame(input_output_frame, bd=2, relief='groove', bg=FGCOLOR)
        input_frame.grid(row=0, column=0, padx=10, pady=10)
        tk.Label(input_frame, text="Окно ввода", bg="#FFFFFF").pack(padx=10, pady=5)
        self.transmitter_field = tk.Text(input_frame, width=40, height=10)
        self.transmitter_field.pack(side='left', padx=10, pady=5)
        self.transmitter_scrollbar = tk.Scrollbar(input_frame, command=self.transmitter_field.yview)
        self.transmitter_scrollbar.pack(side='right', fill='y', padx=10, pady=10)
        self.transmitter_field['yscrollcommand'] = self.transmitter_scrollbar.set

        # ----- ОКНО ВЫВОДА -------------------------------------------------
        output_frame = tk.Frame(input_output_frame, bd=2, relief='groove', bg=FGCOLOR)
        output_frame.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(output_frame, text="Окно вывода", bg="#FFFFFF").pack(padx=10, pady=5)
        self.receiver_field = tk.Text(output_frame, width=40, height=10)
        self.receiver_field.pack(side='left', padx=10, pady=5)
        self.receiver_scrollbar = tk.Scrollbar(output_frame, command=self.receiver_field.yview)
        self.receiver_scrollbar.pack(side='right', fill='y', padx=10, pady=10)
        self.receiver_field['yscrollcommand'] = self.receiver_scrollbar.set

        # ------- ОКНО УПРАВЛЕНИЯ ------------------------------------------------------

        control_frame = tk.Frame(self.root, bg=FGCOLOR, bd=2, relief=tk.GROOVE)
        control_frame.grid(row=1, column=0, sticky='nw', padx=25, pady=25)

        # Окно управления (правая часть)
        control_label = tk.Label(control_frame, text="Окно управления", font=FONT, bg="#FFFFFF")
        control_label.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для отправителя
        transmit_label = tk.Label(control_frame, text="Отправитель", font=SMALL_FONT, bg="#FFFFFF")
        transmit_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_first = ttk.Combobox(control_frame, font=SMALL_FONT)
        self.combo_box_first.pack(anchor="w", padx=10, pady=5)

        # Комбо-бокс для получателя
        receive_label = tk.Label(control_frame, text="Получатель", font=SMALL_FONT, bg="#FFFFFF")
        receive_label.pack(anchor="w", padx=10, pady=5)

        self.combo_box_second = ttk.Combobox(control_frame, font=("Courier", 12))
        self.combo_box_second.pack(anchor="w", padx=10, pady=5)

        # -----ОКНО СОСТОЯНИЯ---------------------------------------------
        status_frame = tk.Frame(self.root, bg=FGCOLOR, bd=2, relief=tk.GROOVE)
        status_frame.grid(row=1, column=1, sticky='ne', padx=25, pady=25)

        status_label = tk.Label(status_frame, text="Окно состояния", font=FONT, bg="#FFFFFF")
        status_label.pack(anchor="w", padx=15, pady=15)

        port_info = tk.Label(status_frame,
                             text="Скорость передачи данных: 9600\nБит данных: 8\nПаритет: нет\nСтоп-биты: 1",
                             font=SMALL_FONT, bg="#FFFFFF", justify=tkinter.LEFT)
        port_info.pack(side=tk.BOTTOM, anchor="nw", padx=50, pady=10)

        self.transmitted_portions_label = tk.Label(status_frame, text=f"Передано порций: {self.transmitted_portions}",
                                                   font=SMALL_FONT, bg="#FFFFFF", justify=tkinter.LEFT)
        self.transmitted_portions_label.pack(side=tk.BOTTOM, anchor="nw", padx=50, pady=5)

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
        message = self.transmitter_field.get().strip()
        self.transmitter_field.delete(0, tk.END)
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

    def display_received_data(self, data):
        self.receiver_field.config(state='normal')  # Разрешаем редактирование
        self.receiver_field.insert(tk.END, data + "\n")  # Вставляем текст
        # self.receiver_field.config(state='disabled')  # Возвращаем в режим "только для чтения"
        self.receiver_field.yview(tk.END)

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
