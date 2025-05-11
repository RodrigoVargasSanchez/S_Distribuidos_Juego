import Pyro5.api
import Pyro5.server
import csv
import threading

@Pyro5.api.expose
class LogCentral:
    def __init__(self):
        self.logs = []

    def registrar_log(self, timestamp, evento, juego_id, operacion, equipo, jugador, dado):
        log_entry = {
            "timestamp": timestamp,
            "tipo_evento": evento,
            "juego_id": juego_id,
            "accion": operacion,
            "equipo": equipo,
            "jugador": jugador,
            "resultado": dado
        }
        self.logs.append(log_entry)
        print(f"[LOG] {log_entry}")

    def guardar_logs_csv(self, filename="logs.csv"):
        if not self.logs:
            print("No hay logs para guardar.")
            return

        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.logs[0].keys())
            writer.writeheader()
            for log in self.logs:
                writer.writerow(log)
        print(f"Logs guardados en {filename}")


# Crear el servidor Pyro5
daemon = Pyro5.server.Daemon()
ns = Pyro5.api.locate_ns()
log_central = LogCentral()
uri = daemon.register(log_central)
ns.register("log.central", uri)

print("Log central registrado con URI:", uri)

# Hilo para manejar las peticiones del daemon
def correr_daemon():
    print("Servidor escuchando... (presione Enter para detener y guardar logs)")
    daemon.requestLoop()

daemon_thread = threading.Thread(target=correr_daemon)
daemon_thread.start()

# Esperar Enter
print("Presione Enter para detener el servidor y guardar los logs...")
input()
print("\nEnter detectado. Guardando logs...")
log_central.guardar_logs_csv("logs.csv")
daemon.shutdown()
print("Servidor detenido.")
