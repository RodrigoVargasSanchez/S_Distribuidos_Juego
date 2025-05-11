import Pyro5.api
import os
from dotenv import load_dotenv

load_dotenv()

server_host = os.getenv("HOST_SERVER_RMI")

@Pyro5.api.expose
class ClienteRMI:
    def __init__(self, nombre_log):
        self.nombre_log = nombre_log

    def enviar_log(self):
        with open(f'logs/{self.nombre_log}', 'r') as f:
            contenido = f.read()

        print(contenido)

        ns = Pyro5.api.locate_ns(host="localhost", port=9090)
        uri = ns.lookup("servidor.logs")
        servidor = Pyro5.api.Proxy(uri)
        recibido = servidor.recibir_logs(contenido)
        print(recibido)

        if recibido:
            os.remove(f'logs/{self.nombre_log}')

