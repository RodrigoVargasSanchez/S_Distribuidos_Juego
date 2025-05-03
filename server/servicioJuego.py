import Pyro5.api
import random
from collections import defaultdict

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, max_posiciones=100, dado_min=1, dado_max=6):
        self.max_posiciones = max_posiciones
        self.dado_min = dado_min
        self.dado_max = dado_max

        self.equipos = {
            "1": {
                "integrantes": set(),
                "proxies" : set(),
                "posicion": 0,
                "listo": False
            },
            "2": {
                "integrantes": set(),
                "posicion": 0,
                "listo": False
            }
        }

        self.peticion_union = defaultdict(list)
        self.orden_turnos = []
        self.turno_actual = 0
        self.juego_iniciado = False
        self.ganador = None

    def registrar_integrante(self, nombre, equipo, uri_cliente):
        if self.juego_iniciado:
            return False, "El juego ya ha comenzado."

        cliente_proxy = Pyro5.api.Proxy(uri_cliente)

        if equipo not in self.equipos:
            self.equipos[equipo] = {
                "integrantes": set(),
                "proxies": set(),
                "posicion": 0,
                "listo": False
            }

        for data in self.equipos.values():
            if nombre in data["integrantes"]:
                return False, f"{nombre} ya está registrado en un equipo."

        integrantes = list(self.equipos[equipo]["integrantes"])
        proxies = list(self.equipos[equipo]["proxies"])

        if len(integrantes) == 0:
            self.equipos[equipo]["integrantes"].add(nombre)
            self.equipos[equipo]["proxies"].add(cliente_proxy)
            cliente_proxy.bienvenido_primero()
            return True, f"{nombre} se ha unido directamente al equipo {equipo}."

        votos = []
        for proxy in proxies:
            try:
                voto = proxy.aprobacion_integrante(nombre)
                votos.append(voto)
            except:
                print(f"No se pudo contactar con un miembro del equipo {equipo} para la aprobación.")
                return False, f"No se pudo contactar con todos los miembros del equipo {equipo} para la aprobación."

        if all(votos):
            self.equipos[equipo]["integrantes"].add(nombre)
            self.equipos[equipo]["proxies"].add(cliente_proxy)
            cliente_proxy.esperando_aprobacion()
            return True, f"{nombre} fue aprobado por todos y se ha unido al equipo {equipo}."
        else:
            return False, f"{nombre} no fue aprobado por todos y no se ha unido al equipo {equipo}."
 

    def marcar_listo(self, equipo):
        if equipo in self.equipos and len(self.equipos[equipo]['integrantes']) >= 1:
            self.equipos[equipo]['listo'] = True
            return True, f"{equipo} está listo para jugar."
        return False, f"{equipo} no cumple con los requisitos para iniciar."

    def iniciar_juego(self):
        listos = [eq for eq, data in self.equipos.items() if data['listo'] and data['integrantes']]
        if len(listos) >= 2 and not self.juego_iniciado:
            self.orden_turnos = random.sample(listos, len(listos))
            self.juego_iniciado = True
            return True, f"Juego iniciado con orden: {self.orden_turnos}"
        return False, "Faltan equipos listos para iniciar el juego."

    def lanzar_dados(self, nombre):
        if not self.juego_iniciado:
            return False, "El juego no ha comenzado."
        if self.ganador:
            return False, f"El juego ha terminado. Ganador: {self.ganador}"

        equipo_jugador = None
        for eq, data in self.equipos.items():
            if nombre in data['integrantes']:
                equipo_jugador = eq
                break

        if equipo_jugador is None:
            return False, "Jugador no registrado."

        equipo_turno = self.orden_turnos[self.turno_actual % len(self.orden_turnos)]
        if equipo_jugador != equipo_turno:
            return False, f"No es el turno de tu equipo ({equipo_turno})."

        suma = sum(random.randint(self.dado_min, self.dado_max) for _ in self.equipos[equipo_turno]['integrantes'])
        self.equipos[equipo_turno]['posicion'] += suma

        if self.equipos[equipo_turno]['posicion'] >= self.max_posiciones:
            self.ganador = equipo_turno
            return True, f"{equipo_turno} lanzó {suma} y ganó el juego!"

        self.turno_actual += 1
        return True, f"{equipo_turno} lanzó {suma} y está en la posición {self.equipos[equipo_turno]['posicion']}."

    def obtener_estado(self):
        return {
            "equipos": {k: {"posicion": v['posicion'], "integrantes": list(v['integrantes'])} for k, v in self.equipos.items()},
            "turno_actual": self.orden_turnos[self.turno_actual % len(self.orden_turnos)] if self.juego_iniciado and self.orden_turnos else None,
            "ganador": self.ganador
        }