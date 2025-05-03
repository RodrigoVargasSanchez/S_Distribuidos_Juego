import sys
import threading
import Pyro5.api
import time
from cliente import Cliente

def main():
    if len(sys.argv) != 3:
        print("Uso: python cliente.py <nombre> <numero_equipo>")
        sys.exit(1)

    nombre = sys.argv[1]
    equipo = sys.argv[2]

    cliente = Cliente()
    daemon = Pyro5.api.Daemon()
    uri_cliente = daemon.register(cliente)

    threading.Thread(target=daemon.requestLoop, daemon=True).start()

    ns = Pyro5.api.locate_ns()
    juego = Pyro5.api.Proxy(ns.lookup("juego.servicio"))


    try:
        juego.registrar_integrante(nombre, equipo, uri_cliente)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSaliste del juego")

if __name__ == "__main__":
    main()