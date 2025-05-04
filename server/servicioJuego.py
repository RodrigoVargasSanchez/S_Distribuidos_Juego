import Pyro5.api
import random

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

        self.juego_iniciado = False

    def registrar_integrante(self, nombre, equipo, uri_cliente):
        print("Cliente conectado:", uri_cliente)

        cliente_proxy = Pyro5.api.Proxy(uri_cliente)

        # Verificar si el nombre ya existe en cualquier equipo
        for data in self.equipos.values():
            if nombre in data["integrantes"]:
                cliente_proxy.nombre_existe()
                return "Jugador ya existe en un equipo"

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
            return "Bienvenido, eres el primer integrante del equipo"
        
        return "Hay integrantes en el equipo. Esperando votación..." 


    def votacion_equipo(self, nombre, equipo, uri_cliente):
        # Si ya hay integrantes, se requiere votación

        cliente_proxy = Pyro5.api.Proxy(uri_cliente)
        votos = []
        cliente_proxy.esperando_aprobacion()
        for uri in self.equipos[equipo]["uris"]:
            try:
                with Pyro5.api.Proxy(uri) as cliente_proxy:
                    voto = cliente_proxy.aprobacion_integrante(nombre)
                    votos.append(voto)
            except Exception as e:
                print(f"No se pudo contactar con un miembro del equipo {equipo}: {e}")
                return "No se pudo conectar con un integrante del equipo"   

        if all(votos):
            self.equipos[equipo]["integrantes"].append(nombre)
            self.equipos[equipo]["uris"].append(uri_cliente)
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.aprobacion_confirmada()
            return "Has sido aceptado por el equipo"
        else:
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.aprobacion_denegada()
            return "NO has sido aceptado por el equipo"
