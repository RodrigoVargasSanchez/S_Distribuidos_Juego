import tkinter as tk

class Listo:
    def __init__(self, parent_container, nombre, equipo, listo_callback):
        self.frame = tk.Frame(parent_container, padx=15, pady=15)
        # Colocar el frame en la celda central (1,1) del contenedor padre
        self.frame.grid(row=1, column=1, sticky="") # Usa grid

        # Mostrar nombre del jugador
        label_nombre = tk.Label(self.frame, text=f"{nombre}", font=("Arial", 16))
        label_nombre.grid(row=0, column=0, pady=(0, 10)) # Padding inferior

        # Mostrar equipo
        label_equipo = tk.Label(self.frame, text=f"Equipo {equipo}", font=("Arial", 14))
        label_equipo.grid(row=1, column=0, pady=10) # Padding arriba y abajo

        # Botón "Listo para jugar"
        self.btn_listo = tk.Button(
            self.frame,
            text="Listo para jugar",
            command=self.on_listo,
            width=20,
            font=("Arial", 14)
        )
        self.btn_listo.grid(row=2, column=0, pady=(10, 0))
        self.btn_listo.focus_set()

        # Label de estado (oculto al inicio)
        self.label_estado = tk.Label(self.frame, text="", font=("Arial", 12), fg="gray")
        self.label_estado.grid(row=3, column=0, pady=(10, 0))

        self.callback = listo_callback

    def on_listo(self):
        # Desactivar botón
        self.btn_listo.config(state="disabled")

        # Mostrar mensaje de espera
        self.label_estado.config(text="Esperando jugadores...")

        # Llamar callback
        self.callback()


    def get_frame(self):
        return self.frame