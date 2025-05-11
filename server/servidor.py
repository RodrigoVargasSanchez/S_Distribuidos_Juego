import Pyro5.api
import os
from servicioJuego import ServicioJuego
from dotenv import load_dotenv

load_dotenv()

dado_min = os.getenv("DADO_MIN")
dado_max = os.getenv("DADO_MAX")
num_posiciones = os.getenv("NUM_POSICIONES")
num_jugadores = os.getenv("NUM_JUGADORES")
num_equipos = os.getenv("NUM_EQUIPOS")

def main():
    daemon = Pyro5.api.Daemon()
    juego = ServicioJuego(dado_min, dado_max, num_posiciones, num_jugadores, num_equipos)
    uri = daemon.register(juego)

    ns = Pyro5.api.locate_ns()
    ns.register("juego.servicio", uri)

    print("Servidor del juego activo. URI:", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()