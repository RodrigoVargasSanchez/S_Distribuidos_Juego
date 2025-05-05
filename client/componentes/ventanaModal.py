import tkinter as tk
from tkinter import simpledialog

class VentanaModal(simpledialog.Dialog):
    def __init__(self, parent, titulo, mensaje, botones=[]):
        self.mensaje = mensaje
        self.botones = botones
        super().__init__(parent, title=titulo)

    def body(self, master):
        self.geometry("400x300")
        self.resizable(False, False)
        tk.Label(master, text=self.mensaje, wraplength=350, font=("Arial", 14)).pack(pady=20)
        return None  # No foco inicial

    def buttonbox(self):
        if not self.botones:
            return  # No crear botones si la lista está vacía

        box = tk.Frame(self)
        for texto, accion in self.botones:
            tk.Button(box, text=texto, width=10, command=lambda a=accion: self._ejecutar(a), font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        box.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self._no_cerrar)

    def _ejecutar(self, accion):
        if accion:
            accion()
        self.destroy()

    def _no_cerrar(self):
        # No hace nada: previene cerrar con "X"
        pass