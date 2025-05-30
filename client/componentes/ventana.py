import tkinter as tk

from componentes.inicio import Inicio
from componentes.esperandoListo import Listo
from componentes.juego import Juego  # Asegúrate de que el nombre del archivo sea juego.py


class Ventana(tk.Tk):
    def __init__(self, min_ancho=550, min_alto=400, on_close_callback=None):
        super().__init__()
        self.title("Cliente del Juego")
        self.minsize(min_ancho, min_alto)
        # self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.content_frame = tk.Frame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=0) # Fila central
        self.content_frame.grid_rowconfigure(2, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0) # Columna central
        self.content_frame.grid_columnconfigure(2, weight=1)

        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._current_component_frame = None
        self.juego_component = None # Para almacenar la instancia de Juego

    def _clear_content_frame(self):
        if self._current_component_frame:
            self._current_component_frame.destroy()
            self._current_component_frame = None

    def show_inicio(self, num_equipos, unirse_callback):
        self._clear_content_frame()
        # Inicio ya usa grid internamente
        self.inicio_component = Inicio(self.content_frame, num_equipos, unirse_callback)
        self._current_component_frame = self.inicio_component.get_frame()

    def show_listo(self, nombre, equipo, listo_callback):
        self._clear_content_frame()
        # Listo ahora también usará grid internamente
        self.listo_component = Listo(self.content_frame, nombre, equipo, listo_callback)
        self._current_component_frame = self.listo_component.get_frame()

    def show_juego(self, nombre, equipo, uri_cliente):
        self._clear_content_frame()
        self.juego_component = Juego(self.content_frame, nombre, equipo, uri_cliente) # <--- Pasar el callback
        self._current_component_frame = self.juego_component.get_frame

    
    def habilitar_lanzar(self):
        """Habilita el botón para lanzar el dado."""
        if self.juego_component:
            resultado = self.juego_component.habilitar_lanzar()
            return resultado

    # def actualizar_info_turno_juego(self, nombre_jugador, nombre_equipo):
    #     if hasattr(self, 'juego_component') and self.juego_component:
    #         self.juego_component.actualizar_info_turno(nombre_jugador, nombre_equipo)
        # def deshabilitar_boton_lanzar(self):
    #     """Deshabilita el botón para lanzar el dado."""
    #     if self.juego_component:
    #         self.juego_component.deshabilitar_boton_lanzar()

    def actualizar_tabla_juego(self, diccionario_equipos, titulo, mensaje, equipo):
        if hasattr(self, 'juego_component') and self.juego_component:
            self.juego_component.actualizar_tabla(diccionario_equipos, titulo, mensaje, equipo)

    def get_inicio_data(self):
        if hasattr(self, 'inicio_component') and self._current_component_frame == self.inicio_component.get_frame():
            return self.inicio_component.get_datos()
        return None, None

    def on_close(self):
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                print(f"Error al desconectar: {e}")
        self.destroy()