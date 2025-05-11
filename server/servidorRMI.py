import Pyro5.api
import Pyro5.server

@Pyro5.api.expose
class ServidorRMI:
    def __init__(self):
        self.ruta_logs = '../stats/logs_centralizados.log'

    def recibir_log(self, contenido):
        print("Recibiendo log...")
        with open(f'{self.ruta_logs}', 'w') as f:
            f.write(contenido)

        return True

def main():
    daemon = Pyro5.server.Daemon(host="localhost")  # Puerto aleatorio
    ns = Pyro5.api.locate_ns(host="localhost", port=9090)

    servidor = ServidorRMI()
    uri = daemon.register(servidor)
    ns.register("servidor.logs", uri)

    print("Servidor RMI escuchando como: PYRO:servidor.logs@localhost:9090")
    daemon.requestLoop()

if __name__ == "__main__":
    main()