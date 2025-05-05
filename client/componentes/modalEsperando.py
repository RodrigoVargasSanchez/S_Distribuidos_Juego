import tkinter as tk
from tkinter import simpledialog
import threading
import Pyro5.api

class VentanaModalEsperando(simpledialog.Dialog):
    def __init__(self, parent, titulo, nombre, equipo, uri_cliente):
        self.nombre = nombre
        self.equipo = equipo
        self.uri_cliente = uri_cliente
        super().__init__(parent, title=titulo)

    def body(self, master):
        self.geometry("400x300")
        self.resizable(False, False)
        tk.Label(master, text="Esperando votación de los jugadores...", wraplength=350, font=("Arial", 14)).pack(pady=20)
        
        # Iniciar hilo de votación
        self._iniciar_votacion_en_hilo()
        return None  # No foco inicial

    def buttonbox(self):
        self.protocol("WM_DELETE_WINDOW", self._no_cerrar)

    def _no_cerrar(self):
        # Desactiva el cierre con la X
        pass

    def _iniciar_votacion_en_hilo(self):
        hilo = threading.Thread(target=self._votar, daemon=True)
        hilo.start()

    def _votar(self):
        try:
            ns = Pyro5.api.locate_ns()
            juego = Pyro5.api.Proxy(ns.lookup("juego.servicio"))
            juego.votacion_equipo(self.nombre, self.equipo, str(self.uri_cliente))
            
        except Exception as e:
            print(f"Error durante la votación para {self.nombre}: {e}")
        finally:
            self.after(0, self.destroy)
