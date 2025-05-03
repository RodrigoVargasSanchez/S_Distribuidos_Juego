import Pyro5.api
from servicioJuego import ServicioJuego

def main():
    daemon = Pyro5.api.Daemon()
    juego = ServicioJuego()
    uri = daemon.register(juego)

    ns = Pyro5.api.locate_ns()
    ns.register("juego.servicio", uri)

    print("Servidor del juego activo. URI:", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()