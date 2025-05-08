import Pyro5.api
import random
import threading

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, max_posiciones=100, dado_min=1, dado_max=6):
        self.max_posiciones = max_posiciones
        self.dado_min = dado_min
        self.dado_max = dado_max
        self.turno_actual = 0
        self.orden_equipos = []
        self.jugador_turno_actual = None # Nuevo atributo
        self.equipo_turno_actual = None  # Nuevo

        self.equipos = {
            "1": {
                "integrantes": [],
                "uris": [],
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
        print(f"Cliente {nombre} conectado: {uri_cliente}")

        cliente_proxy = Pyro5.api.Proxy(uri_cliente)

        # Verificar si el nombre ya existe en cualquier equipo
        for data in self.equipos.values():
            if nombre in data["integrantes"]:
                cliente_proxy.nombre_existe()
                return 2, "Jugador ya existe en un equipo"

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
            
            return 0, f"¡Bienvenido! eres el primer integrante del equipo {equipo}"
        
        return 1, f"Hay integrantes en el equipo {equipo}. Esperando votación..." 


    def votacion_equipo(self, nombre, equipo, uri_cliente):
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
                return False, "No se pudo conectar con un integrante del equipo" 

        if all(votos):
            self.equipos[equipo]["integrantes"].append(nombre)
            self.equipos[equipo]["uris"].append(uri_cliente)
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.aprobacion_confirmada()
            print(f"[✓] {nombre} fue aprobado y se unió al equipo {equipo}")
            return True, f"{nombre} fue aprobado por todos y se ha unido al equipo {equipo}."
        else:
            try:
                with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                    cliente_proxy.aprobacion_denegada()
            except Exception as e:
                print(f"[!] Error al notificar rechazo a {nombre}: {e}")

            print(f"[✗] {nombre} fue rechazado por algún miembro del equipo {equipo}")
            return False, f"{nombre} no fue aprobado por todos y ha sido dado de baja del sistema."

    def desconectar(self, cliente_uri, nombre):
        equipo_encontrado = None

        # Buscar al jugador y removerlo del equipo
        for equipo_id, data in self.equipos.items():
            if nombre in data["integrantes"]:
                equipo_encontrado = equipo_id
                idx = data["integrantes"].index(nombre)
                del data["integrantes"][idx]
                del data["uris"][idx]
                print(f"[✗] {nombre} se ha desconectado.")
                break

        if equipo_encontrado is None:
            print(f"[!] No se encontró al jugador {nombre} en ningún equipo.")
            return  

    def marcar_listo(self, equipo):
        listos = []
        for uri in self.equipos[equipo]["uris"]:
            print(uri)
            try:
                with Pyro5.api.Proxy(uri) as cliente_proxy:
                    listo = cliente_proxy.get_Listo()
                    listos.append(listo)
            except Exception as e:
                print(f"No se pudo contactar con un miembro del equipo {equipo}: {e}")
                return False, "No se pudo conectar con un integrante del equipo"
            
        if all(listos):
            self.equipos[equipo]["listo"] = True
            print(f"El equipo {equipo} está listo.")

            if all(equipo_data["listo"] for equipo_data in self.equipos.values()):
                print("Todos los equipos están listos. Iniciando el juego...")
                self.iniciar_juego()
                return True, "Todos los equipos están listos. Iniciando el juego..."
            else:
                return True, f"Equipo {equipo} listo. Esperando a los otros equipos..."
        else:
            return False, f"Aún hay jugadores del equipo {equipo} que no están listos"


    def iniciar_juego(self):
        self.orden_equipos = list(self.equipos.keys())
        random.shuffle(self.orden_equipos)
        self.turno_actual = 0
        self.juego_iniciado = True
        self.indice_jugador_actual = {} # Nuevo diccionario para rastrear el jugador actual por equipo
        for equipo_id in self.orden_equipos:
            self.indice_jugador_actual[equipo_id] = 0 # Inicializar el índice del primer jugador de cada equipo

        hilos = []

        for equipo_id, datos_equipo in self.equipos.items():
            for uri in datos_equipo["uris"]:
                # Aquí se "congelan" los valores usando argumentos por defecto
                def lanzar_juego(uri_actual=uri, equipo_actual=equipo_id):
                    try:
                        with Pyro5.api.Proxy(uri_actual) as cliente_proxy:
                            cliente_proxy.iniciar_juego()
                            print(f"Se inició el juego al integrante con uri {uri_actual} del equipo {equipo_actual}")
                    except Exception as e:
                        print(f"No se pudo iniciar el juego para el miembro con uri {uri_actual} del equipo {equipo_actual}: {e}")

                hilo = threading.Thread(target=lanzar_juego)
                hilo.start()
                hilos.append(hilo)

        print("Juego iniciado. El orden de los equipos es:", self.orden_equipos)

        equipo_inicial = self.orden_equipos[0]
        # Notificar al primer jugador del primer equipo que es su turno
        primer_jugador_uri = self.equipos[equipo_inicial]["uris"][self.indice_jugador_actual[equipo_inicial]]
        try:
            with Pyro5.api.Proxy(primer_jugador_uri) as cliente_proxy:
                cliente_proxy.es_tu_turno()
        except Exception as e:
            print(f"Error al notificar inicio de turno al cliente {primer_jugador_uri} del equipo {equipo_inicial}: {e}")

        return True, f"Juego iniciado. El orden de los equipos es: {self.orden_equipos}. Comienza el equipo {self.orden_equipos[0]}, jugador {self.equipos[self.orden_equipos[0]]['integrantes'][0]}"
   
    #Necesaria para ventena    
    def obtener_datos_juego(self):  
        return self.equipos, self.max_posiciones
    
    
    #Necesaria para ventana
    def lanzar_dado_servidor(self, nombre, equipo, uri_cliente):
        if not self.juego_iniciado:
            return None, None, False, "El juego aún no ha comenzado."

        if self.orden_equipos[self.turno_actual] != equipo:
            return None, None, False, f"No es el turno del equipo {equipo}. Es el turno del equipo {self.orden_equipos[self.turno_actual]}."

        # Obtener el índice del jugador actual del equipo
        indice_actual_jugador = self.indice_jugador_actual.get(equipo, 0)

        # Verificar si el jugador que intenta lanzar es el jugador actual del equipo
        if equipo in self.equipos and self.equipos[equipo]["integrantes"] and nombre != self.equipos[equipo]["integrantes"][indice_actual_jugador]:
            jugador_actual = self.equipos[equipo]["integrantes"][indice_actual_jugador]
            return None, None, False, f"No es el turno de {nombre}. Es el turno de {jugador_actual} del equipo {equipo}."

        numero = random.randint(self.dado_min, self.dado_max)

        if equipo in self.equipos and nombre in self.equipos[equipo]["integrantes"]:
            nueva_posicion = self.equipos[equipo]["posicion"] + numero

            if nueva_posicion >= self.max_posiciones:
                nueva_posicion = self.max_posiciones
                ganador = True
            else:
                ganador = False

            self.equipos[equipo]["posicion"] = nueva_posicion
            self.actualizar_tableros_clientes()

            # Pasar al siguiente jugador del equipo
            self.indice_jugador_actual[equipo] = (self.indice_jugador_actual[equipo] + 1) % len(self.equipos[equipo]["integrantes"])

            # Pasar al siguiente equipo después de que un jugador haya lanzado
            self.turno_actual = (self.turno_actual + 1) % len(self.orden_equipos)

            siguiente_equipo = self.orden_equipos[self.turno_actual]
            indice_siguiente_jugador = self.indice_jugador_actual[siguiente_equipo]
            nombre_siguiente_jugador = self.equipos[siguiente_equipo]["integrantes"][indice_siguiente_jugador]
            uri_siguiente_jugador = self.equipos[siguiente_equipo]["uris"][indice_siguiente_jugador]

            # Notificar al siguiente jugador que es su turno
            try:
                with Pyro5.api.Proxy(uri_siguiente_jugador) as cliente_proxy:
                    cliente_proxy.es_tu_turno() # <--- Enviar notificación de turno
            except Exception as e:
                print(f"Error al notificar turno al cliente {uri_siguiente_jugador} del equipo {siguiente_equipo}, jugador {nombre_siguiente_jugador}: {e}")

            return numero, nueva_posicion, ganador, None
        else:
            print(f"No se encontró el equipo {equipo} o el jugador {nombre} no pertenece a ese equipo.")
            return None, None, False, "Error: Equipo o jugador no encontrado."
                        
    def actualizar_tableros_clientes(self):
        hilos = []

        for equipo_id, datos_equipo in self.equipos.items():
            for uri in datos_equipo["uris"]:
                def actualizar_tableros(uri_actual, equipo_actual):
                    try:
                        with Pyro5.api.Proxy(uri_actual) as cliente_proxy:
                            cliente_proxy.actualizar_tabla(self.equipos)
                    except Exception as e:
                        print(f"No se pudo actualizar la tabla al miembro con uri {uri_actual} del equipo {equipo_actual}: {e}")

                # Lanzar hilo para cada cliente
                hilo = threading.Thread(target=actualizar_tableros, args=(uri, equipo_id))
                hilo.start()
                hilos.append(hilo)

        return True, "Tablas actualizadas en paralelo"