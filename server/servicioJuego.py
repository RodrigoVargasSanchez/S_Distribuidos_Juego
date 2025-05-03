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
                "integrantes": [],
                "uris": [],  # Lista de URIs (str)
                "posicion": 0,
                "listo": False
            },
            "2": {
                "integrantes": [],
                "uris": [],
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
        print("Cliente conectado:", uri_cliente)

        cliente_proxy = Pyro5.api.Proxy(uri_cliente)

        # Verificar si el nombre ya existe en cualquier equipo
        for data in self.equipos.values():
            if nombre in data["integrantes"]:
                cliente_proxy.nombre_existe()
                return

        # Si el equipo no existe, se crea
        if equipo not in self.equipos:
            self.equipos[equipo] = {
                "integrantes": [],
                "uris": [],
                "posicion": 0,
                "listo": False
            }

 
        # Si es el primer integrante, se acepta automáticamente
        if len(self.equipos[equipo]["integrantes"]) == 0:
            self.equipos[equipo]["integrantes"].append(nombre)
            self.equipos[equipo]["uris"].append(uri_cliente)
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.bienvenido_primero()
            return

        # Si ya hay integrantes, se requiere votación
        votos = []
        cliente_proxy.esperando_aprobacion()
        for uri in self.equipos[equipo]["uris"]:
            try:
                with Pyro5.api.Proxy(uri) as cliente_proxy:
                    voto = cliente_proxy.aprobacion_integrante(nombre)
                    votos.append(voto)
            except Exception as e:
                print(f"No se pudo contactar con un miembro del equipo {equipo}: {e}")
                return False, f"No se pudo contactar con todos los miembros del equipo {equipo} para la aprobación."

        if all(votos):
            self.equipos[equipo]["integrantes"].append(nombre)
            self.equipos[equipo]["uris"].append(uri_cliente)
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.aprobacion_confirmada()
            return True, f"{nombre} fue aprobado por todos y se ha unido al equipo {equipo}."
        else:
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.aprobacion_denegada()
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