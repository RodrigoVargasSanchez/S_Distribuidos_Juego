import Pyro5.api
import tkinter as tk
import logging
from datetime import datetime
from clienteRMI import ClienteRMI
import subprocess
import sys
import os

@Pyro5.api.expose
class Cliente:
    def __init__(self):
        # Referencias que serán configuradas desde main.py
        self.ventana = None
        self.ventana_modal_activa = None
        self.VentanaModal = None
        self.callback_continuar = None
        self.callback_salir = None

        self.nombre_actual = None
        self.equipo_actual = None
        self.uri = None
        self.listo = False
        self.juego_id = None

    def configurar_logger(self):
        if self.nombre_actual is None or self.juego_id is None or self.equipo_actual is None:
            raise ValueError("Faltan datos para configurar el logger")

        self.logger = logging.getLogger(f"juego{str(self.juego_id)}{self.nombre_actual}")
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(f'logs/{self.nombre_actual}.log')
        fh.setFormatter(logging.Formatter('%(message)s'))

        # Evita agregar múltiples handlers si se vuelve a llamar
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def log(self, estado, accion, valor=None):
        timestamp = datetime.now().isoformat()
        componentes = [timestamp,estado,f"juego{str(self.juego_id)}",accion,f"equipo{str(self.equipo_actual)}",self.nombre_actual]

        if valor is not None:
            componentes.append(str(valor))

        mensaje = ",".join(componentes)
        self.logger.info(mensaje)

    
    def get_Listo(self):
        return self.listo
        
    def configurar_referencias(self, ventana, VentanaModal, continuar, salir):
        """Configura las referencias necesarias para la interfaz gráfica"""
        self.ventana = ventana
        self.VentanaModal = VentanaModal
        self.callback_continuar = continuar
        self.callback_salir = salir
        
    def solicitud(self, apodo):
        """Notifica que un usuario ha solicitado unirse al equipo"""
        print(f"\n{apodo} ha solicitado unirse a su equipo.")
    
    def bienvenido_primero(self):
        """Notifica que es el primer integrante del equipo"""
        print(f"\n ¡Bienvenido al juego! Eres el primer integrante del equipo.")
    
    def esperando_aprobacion(self):
        """Notifica que está esperando aprobación para unirse al equipo"""
        print(f"\n ¡Bienvenido al juego! Esperando aprobacion para unirte al equipo.")
        # No necesita hacer nada aquí, la ventana modal ya se muestra en main.py
    
    def nombre_existe(self):
        """Notifica que el nombre ya existe en un equipo"""
        print(f"\n Este usuario ya se encuentra en un equipo.")
    
    def aprobacion_confirmada(self, jugando):
        """Método remoto llamado cuando el cliente ha sido aceptado en el equipo"""
        print(f"\n Has sido aceptado en el equipo!.")
        
        # Esta función se ejecutará en el hilo principal de tkinter
        def actualizar_ui():
            # Cerrar la ventana modal de espera si existe
            if hasattr(self, 'ventana_modal_activa') and self.ventana_modal_activa:
                try:
                    self.ventana_modal_activa.destroy()
                except:
                    pass  # La ventana puede haberse cerrado ya
            
            # Mostrar ventana de éxito
            if self.VentanaModal and self.callback_continuar and self.nombre_actual and self.equipo_actual:
                self.VentanaModal(self.ventana, "¡Genial!", "Has sido aceptado por el equipo", 
                          botones=[("Continuar", lambda: self.callback_continuar(self.nombre_actual, self.equipo_actual, self.uri, jugando))])
        
        # Ejecutar en el hilo principal si la ventana está disponible
        if self.ventana:
            self.ventana.after(0, actualizar_ui)
    
    def aprobacion_denegada(self):
        """Método remoto llamado cuando el cliente ha sido rechazado"""
        print(f"\n No has sido aceptado en el equipo.")
        
        # Esta función se ejecutará en el hilo principal de tkinter
        def actualizar_ui():
            # Cerrar la ventana modal de espera si existe
            if hasattr(self, 'ventana_modal_activa') and self.ventana_modal_activa:
                try:
                    self.ventana_modal_activa.destroy()
                except:
                    pass  # La ventana puede haberse cerrado ya
            
            # Mostrar ventana de rechazo
            if self.VentanaModal and self.callback_salir:
                self.VentanaModal(self.ventana, ":(", "NO has sido aceptado por el equipo", 
                          botones=[("Salir", self.callback_salir)])
        
        # Ejecutar en el hilo principal si la ventana está disponible
        if self.ventana:
            self.ventana.after(0, actualizar_ui)

    
    def aprobacion_integrante(self, nombre):
        """Método remoto llamado para solicitar aprobación de un nuevo integrante"""
        print(f"\n{nombre} ha solicitado unirse a tu equipo.")       
        
        # Si estamos en modo gráfico
        resultado = {"voto": False, "completado": False}
        
        # Función para mostrar la ventana modal en el hilo principal
        def mostrar_ventana_votacion():
            # Crear ventana modal para votación
            ventana_modal = tk.Toplevel(self.ventana)
            ventana_modal.title("Votación de Equipo")
            ventana_modal.geometry("400x200")
            ventana_modal.transient(self.ventana)
            ventana_modal.grab_set()
            
            # Contenido de la ventana
            tk.Label(ventana_modal, text=f"¿Aceptas a {nombre} en tu equipo?", font=("Arial", 14)).pack(pady=20)
            
            frame_botones = tk.Frame(ventana_modal)
            frame_botones.pack(pady=20)
            
            def votar(voto):
                resultado["voto"] = voto
                resultado["completado"] = True
                ventana_modal.destroy()
            
            tk.Button(frame_botones, text="Aceptar", command=lambda: votar(True), 
                      width=10, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
            tk.Button(frame_botones, text="Rechazar", command=lambda: votar(False), 
                      width=10, bg="red", fg="white").pack(side=tk.LEFT, padx=10)
        
        # Ejecutar en el hilo principal
        self.ventana.after(0, mostrar_ventana_votacion)
        
        # Esperar hasta que se complete la votación (este enfoque no es el más eficiente,
        # pero es una solución simple para nuestro caso)
        while not resultado["completado"]:
            pass  # Esperar a que se complete la votación
        
        return resultado["voto"]
    
    def iniciar_juego(self):
        """Método remoto llamado por el servidor para iniciar el juego"""
        print(f"\n ¡Has sido aceptado! Iniciando juego...")
        self.es_mi_turno = False

        def actualizar_ui():
            # Cerrar ventana modal si sigue activa
            if hasattr(self, 'ventana_modal_activa') and self.ventana_modal_activa:
                try:
                    self.ventana_modal_activa.destroy()
                except:
                    pass

            # Cargar la pantalla del juego
            if self.ventana:
                self.ventana.show_juego(
                    self.nombre_actual,
                    self.equipo_actual,
                    self.uri,
                )

        # Ejecutar en el hilo principal
        if self.ventana:
            self.ventana.after(0, actualizar_ui)

    def actualizar_tabla(self, diccionario_equipos, titulo, mensaje, equipo):
        """Método remoto llamado por el servidor para actualizar la tabla del juego"""
        
        def actualizar_ui():
            if hasattr(self, 'ventana') and self.ventana:
                self.ventana.actualizar_tabla_juego(diccionario_equipos, titulo, mensaje, equipo)

        if self.ventana:
            self.ventana.after(0, actualizar_ui)

    def habilitar_lanzar(self):        
        if hasattr(self, 'ventana') and self.ventana:
            # Usar after para ejecutar la actualización UI de forma asíncrona
            self.ventana.after(0, self.ventana.habilitar_lanzar)

    def lanzar_victoria(self, equipo):
        """Método remoto llamado cuando el cliente ha sido aceptado en el equipo"""
        print(f"\n Has sido aceptado en el equipo!.")
        
        # Esta función se ejecutará en el hilo principal de tkinter
        def actualizar_ui():
            if self.VentanaModal and self.callback_salir:
                self.VentanaModal(self.ventana, "!!!!", f"¡¡El equipo {equipo} ha ganado el juego!!", 
                          botones=[("Salir", self.ejecutar_stats)])
                
        if self.ventana:
            self.ventana.after(0, actualizar_ui)

    def ejecutar_stats(self):
        ruta_script = os.path.join(os.path.dirname(__file__), '../stats/ejecutar.py')
        subprocess.Popen([sys.executable, ruta_script])
        
        # Luego cerrar la ventana principal
        if self.ventana:
            self.ventana.destroy()


    def centralizar_logs(self):
        cliente_rmi = ClienteRMI(f"{self.nombre_actual}.log")
        cliente_rmi.enviar_log()
        print("se envió el log")
