import Pyro5.api

@Pyro5.api.expose
class Cliente:
    def solicitud(self, apodo):
        print(f"\n{apodo} ha solicitado unirse a su equipo.")

    def bienvenido_primero(self):
        print(f"\n ¡Bienvenido al juego! Eres el primer integrante del equipo.")

    def esperando_aprobacion(self):
        print(f"\n ¡Bienvenido al juego! Esperando aprobacion para unirte al equipo.")

    def aprobacion_integrante(self, nombre):
        while True:
            respuesta = input(f"\n{nombre} ha solicitado unirse a tu equipo. ¿Aceptas? (S/N): ").strip().upper()
            if respuesta == 'S':
                return True
            elif respuesta == 'N':
                return False
            else:
                print("Entrada no válida. Por favor, ingresa 'S' para sí o 'N' para no.")
