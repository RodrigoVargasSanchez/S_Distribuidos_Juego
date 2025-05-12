import Pyro5.api
import Pyro5.server
from dotenv import load_dotenv
import os

load_dotenv()

ruta_logs = os.getenv("PATH_LOGS")

@Pyro5.api.expose
class ServidorRMI:
    def __init__(self):
        self.ruta_logs = ruta_logs

    def recibir_log(self, contenido):
        print("Recibiendo log...")

        if not os.path.exists(self.ruta_logs) or os.path.getsize(self.ruta_logs) == 0:
            with open(self.ruta_logs, 'w') as f:
                f.write("timestamp,tipo_evento,juego_id,accion,equipo,jugador,resultado\n")

        with open(self.ruta_logs, 'a') as f:
            f.write(contenido)

        return True

def main():
    daemon = Pyro5.server.Daemon(host="localhost")
    ns = Pyro5.api.locate_ns(host="localhost", port=9090)

    servidor = ServidorRMI()
    uri = daemon.register(servidor)
    ns.register("servidor.logs", uri)

    print("Servidor RMI escuchando como: PYRO:servidor.logs@localhost:9090")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
    