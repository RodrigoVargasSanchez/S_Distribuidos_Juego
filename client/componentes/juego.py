import tkinter as tk
from tkinter import ttk, messagebox
import Pyro5.api

class Juego:
    def __init__(self, parent_container, nombre, equipo, uri_cliente):
        self.nombre = nombre
        self.equipo = equipo
        self.uri_cliente = uri_cliente
    
        self.frame = tk.Frame(parent_container)
        self.frame.grid(row=1, column=1, sticky="")

        _, meta_pts = self.obtener_datos()

        # Etiquetas informativas
        tk.Label(self.frame, text=f"Meta de puntos: {meta_pts}", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=5, columnspan=2)
        self.lanzando_label = tk.Label(self.frame, text=f"Jugador: {nombre} | Equipo: {equipo}", font=("Arial", 14))
        self.lanzando_label.grid(row=1, column=0, columnspan=2)
        self.equipo_label = tk.Label(self.frame, text=f"Lanzando: Equipo {equipo}", font=("Arial", 14))
        self.equipo_label.grid(row=2, column=0, columnspan=2)
        
        # Tabla
        estilo = ttk.Style()
        estilo.configure("Treeview", font=("Arial", 12))
        estilo.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        self.tabla = ttk.Treeview(self.frame, columns=("Equipo", "Puntaje"), show="headings")
        self.tabla.heading("Equipo", text="Equipo")
        self.tabla.heading("Puntaje", text="Puntaje")
        self.tabla.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure((0, 1), weight=1)

        self.resultado_label = tk.Label(self.frame, text="Presione para lanzar", font=("Arial", 14))
        self.resultado_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.boton_lanzar = tk.Button(
            self.frame,
            text="Lanzar Dado",
            font=("Arial", 14),
            command=self.lanzar_dado,
            state="disabled"
        ) # Inicialmente deshabilitado
        self.boton_lanzar.grid(row=5, column=0, columnspan=2, pady=10)



    # def deshabilitar_boton_lanzar(self):
    #     """Deshabilita el botón para lanzar el dado."""
    #     self.boton_lanzar.config(state=tk.NORMAL)

    # def actualizar_info_turno(self, nombre_jugador, nombre_equipo):
    #         """Actualiza los labels de información del turno."""
    #         self.lanzando_label.config(text=f"Lanzando: {nombre_jugador}")
    #         self.equipo_label.config(text=f"Equipo: {nombre_equipo}")


    def habilitar_lanzar(self):
        """Habilita el botón para lanzar el dado."""
        messagebox.showinfo("Turno", "¡Es el turno de tu equipo!")
        self.boton_lanzar.config(state="normal")

    def actualizar_tabla(self, diccionario_equipos, titulo, mensaje, equipo):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        for equipo_id, datos in diccionario_equipos.items():
            self.tabla.insert("", "end", values=(equipo_id, datos["posicion"]))

        self.equipo_label.config(text=f"Lanzando: Equipo {equipo}")

        messagebox.showinfo(titulo, mensaje)

    def lanzar_dado(self):
        self.boton_lanzar.config(state="disabled")

        try:
            ns = Pyro5.api.locate_ns()
            juego_servicio = Pyro5.api.Proxy(ns.lookup("juego.servicio"))
            juego_servicio.lanzar(self.equipo, self.uri_cliente)

        except Exception as e:
            print(f"Error al lanzar el dado: {e}")
            messagebox.showerror("Error", f"Error al lanzar el dado: {e}")

    def obtener_datos(self):
        try:
            ns = Pyro5.api.locate_ns()
            juego = Pyro5.api.Proxy(ns.lookup("juego.servicio"))
            diccionario_equipos, meta_pts = juego.obtener_datos_juego()
            return diccionario_equipos, meta_pts
            
        except Exception as e:
            print(f"Error durante la votación para {self.nombre}: {e}")

    def get_frame(self):
        return self.frame