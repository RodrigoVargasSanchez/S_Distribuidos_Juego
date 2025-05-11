import tkinter as tk
from tkinter import ttk

class Inicio:
    def __init__(self, parent_container, num_equipos, unirse_callback):
        self.frame = tk.Frame(parent_container, padx=15, pady=15)
        # Colocar el frame en la celda central (1,1) del contenedor padre
        self.frame.grid(row=1, column=1, sticky="") # Usa grid

        # --- Widgets internos usando grid ---
        tk.Label(self.frame, text="Nombre:", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entrada_nombre = tk.Entry(self.frame, width=30)
        self.entrada_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.frame, text="Equipo:", font=("Arial", 16)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        opciones_equipos = [str(i) for i in range(1, int(num_equipos) + 1)]
        self.entrada_equipo = ttk.Combobox(self.frame, values=opciones_equipos, state="readonly", width=28)
        self.entrada_equipo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entrada_equipo.current(0)

        btn = tk.Button(self.frame, text="Solicitar Ingreso", command=unirse_callback, font=("Arial", 14))
        btn.grid(row=2, column=0, columnspan=2, pady=20)

        self.entrada_nombre.focus_set()

    def get_datos(self):
        return self.entrada_nombre.get(), self.entrada_equipo.get()

    def get_frame(self):
        return self.frame