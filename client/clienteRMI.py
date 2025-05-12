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
        try:
            with open(f'logs/{self.nombre_log}', 'r') as f:
                contenido = f.read()
            print(contenido)
            
            # Crear el proxy para conectarse al servidor
            servidor = Pyro5.api.Proxy(server_host)
            print("Conectado al servidor, enviando log...")
            
            # Llamar al método remoto (nota: es recibir_log, no recibir_logs)
            recibido = servidor.recibir_log(contenido)
            
            if recibido:
                print("Log enviado correctamente")
                os.remove(f'logs/{self.nombre_log}')
                return True
            else:
                print("Error al enviar el log")
                return False
                
        except Exception as e:
            print(f"Error en enviar_log: {e}")
            return False