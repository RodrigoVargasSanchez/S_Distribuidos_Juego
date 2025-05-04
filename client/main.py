import tkinter as tk
from tkinter import messagebox
import threading
import Pyro5.api
from cliente import Cliente  # Asegúrate de tener esta clase definida

cliente = Cliente()
daemon = Pyro5.api.Daemon()
uri_cliente = daemon.register(cliente)

threading.Thread(target=daemon.requestLoop, daemon=True).start()

ns = Pyro5.api.locate_ns()
juego = Pyro5.api.Proxy(ns.lookup("juego.servicio")) 

# Función para manejar el registro
def registrar():
    nombre = entrada_nombre.get()
    equipo = entrada_equipo.get()

    if not nombre or not equipo:
        messagebox.showerror("Error", "Debe ingresar nombre y equipo.")
        return

    try:
        respuesta = juego.registrar_integrante(nombre, equipo, str(uri_cliente))
        messagebox.showinfo("Registro", f"{respuesta}")
        if (respuesta == "Hay integrantes en el equipo. Esperando votación..."):
            votacion = juego.votacion_equipo(nombre, equipo, str(uri_cliente))
            if votacion == "Has sido aceptado por el equipo":
                messagebox.showinfo("Aceptado", f"{votacion}")
            elif votacion == "NO has sido aceptado por el equipo":
                messagebox.showinfo("Aceptado", f"{votacion}")
            else:
                messagebox.showinfo("Aceptado", f"{votacion}") #No se pudo conectar con un integrante del equipo

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar: {e}")

# Función para marcar listo
def marcar_listo():
    equipo = entrada_equipo.get()
    try:
        exito, mensaje = juego.marcar_listo(equipo)
        if exito:
            messagebox.showinfo("Listo", mensaje)
        else:
            messagebox.showwarning("No Listo", mensaje)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo marcar como listo: {e}")

# Iniciar interfaz
ventana = tk.Tk()
ventana.title("Cliente del Juego")

tk.Label(ventana, text="Nombre").grid(row=0, column=0, padx=10, pady=5)
entrada_nombre = tk.Entry(ventana)
entrada_nombre.grid(row=0, column=1)

tk.Label(ventana, text="Equipo").grid(row=1, column=0, padx=10, pady=5)
entrada_equipo = tk.Entry(ventana)
entrada_equipo.grid(row=1, column=1)

tk.Button(ventana, text="Solicitar Ingreso", command=registrar).grid(row=2, column=0, pady=10)

# Hilo separado para el daemon
import threading
def iniciar_pyro():
    print(f"Cliente expuesto en: {uri_cliente}")
    daemon.requestLoop()

threading.Thread(target=iniciar_pyro, daemon=True).start()

ventana.mainloop()