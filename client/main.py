import Pyro5.api
import tkinter as tk
from tkinter import messagebox
import threading

from cliente import Cliente

from componentes.ventana import Ventana
from componentes.inicio import Inicio
from componentes.ventanaModal import VentanaModal
from componentes.modalEsperando import VentanaModalEsperando
from componentes.esperandoListo import Listo

# Inicializar cliente Pyro5
cliente = Cliente()
daemon = Pyro5.api.Daemon()
uri_cliente = daemon.register(cliente)
threading.Thread(target=daemon.requestLoop, daemon=True).start()
ns = Pyro5.api.locate_ns()
juego = Pyro5.api.Proxy(ns.lookup("juego.servicio"))

# Función para continuar después de ser aceptado
def continuar(nombre, equipo):
    print("Continuar fue presionado")
    ventana.show_listo(nombre, equipo, marcar_listo)

# Función para salir
def desconectar():
    juego.desconectar(uri_cliente, cliente.nombre_actual)
    ventana.after(100, ventana.destroy)

def salir():
    ventana.after(100, ventana.destroy)
    
# Función para unirse a un equipo
def unirse():
    nombre, equipo = ventana.get_inicio_data()
    if not nombre or not equipo:
        messagebox.showerror("Error", "Debe ingresar nombre y equipo.")
        return
    
    try:
        estado, mensaje = juego.registrar_integrante(nombre, equipo, str(uri_cliente))
        
        # Guardar los datos del usuario en el cliente para usarlos en callbacks
        cliente.nombre_actual = nombre
        cliente.equipo_actual = equipo
        cliente.uri = uri_cliente
        
        if estado == 1:
            VentanaModalEsperando(ventana, "Votación", nombre, equipo, uri_cliente)

        elif (estado == 2):
            # Error - Mostrar ventana de advertencia
            VentanaModal(ventana, "¡Advertencia!", f"{mensaje}", botones=[("Salir", salir)])
        else:
            # Éxito inmediato - Mostrar ventana de éxito
            VentanaModal(ventana, "¡Genial!", f"{mensaje}", botones = [("Continuar", lambda: continuar(nombre, equipo))])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo unir a la partida: {e}")


# Función para marcar listo
def marcar_listo():
    cliente.listo = True
    estado, mensaje = juego.marcar_listo(cliente.equipo_actual)


# Iniciar interfaz
ventana = Ventana(on_close_callback=desconectar)
ventana.show_inicio(unirse)

# Configurar referencias en el cliente
cliente.configurar_referencias(ventana, VentanaModal, continuar, desconectar)

# Iniciar la interfaz de usuario
ventana.mainloop()