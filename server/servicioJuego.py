import Pyro5.api
import random
import threading

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, dado_min, dado_max, num_posiciones, num_jugadores, num_equipos):
        self.dado_min = dado_min
        self.dado_max = dado_max
        self.num_posiciones = num_posiciones
        self.num_jugadores = num_jugadores
        self.num_equipos = num_equipos

        self.orden_equipos = []
        self.turno_equipo_actual = None

        self.equipos = {
            "1": {
                "integrantes": [],
                "uris": [],
                "recibidos": {},
                "posicion": 0,
                "listo": False
            },
            "2": {
                "integrantes": [],
                "uris": [],
                "recibidos": {},
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

        # Si el equipo no existe, intentar crearlo
        if equipo not in self.equipos:
            if len(self.equipos) < int(self.num_equipos):
                self.equipos[equipo] = {
                    "integrantes": [],
                    "uris": [],
                    "recibidos": {},
                    "posicion": 0,
                    "listo": False            
                }
            else:
                return 3, "¡El número máximo de equipos ha sido alcanzado!"

        # Verificar si el equipo está lleno
        if len(self.equipos[equipo]["integrantes"]) == int(self.num_jugadores):
            return 3, f"¡El equipo {equipo} está completo!"

        # Si es el primer integrante, se acepta automáticamente
        if len(self.equipos[equipo]["integrantes"]) == 0:
            self.equipos[equipo]["integrantes"].append(nombre)
            self.equipos[equipo]["uris"].append(uri_cliente)
            with Pyro5.api.Proxy(uri_cliente) as cliente_proxy:
                cliente_proxy.bienvenido_primero()
            return 0, f"¡Bienvenido! eres el primer integrante del equipo {equipo}"

        # Si hay otros integrantes, se requiere votación
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
                cliente_proxy.aprobacion_confirmada(self.juego_iniciado)
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

                if not data["integrantes"]:
                    data["listo"] = False
                    data["posicion"] = 0
                    print(f"[~] El equipo {equipo_id} quedó vacío. Reiniciando estados")
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
        # Obtener el orden de los equipos
        self.orden_equipos = list(self.equipos.keys())
        random.shuffle(self.orden_equipos)

        # self.turno_actual = 0
        self.juego_iniciado = True
        self.turno_equipo_actual = 0
        # self.indice_jugador_actual = {} # Nuevo diccionario para rastrear el jugador actual por equipo

        # for equipo_id in self.orden_equipos:
        #     self.indice_jugador_actual[equipo_id] = 0 # Inicializar el índice del primer jugador de cada equipo

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

        # self.actualizar_tableros_clientes()
        titulo = "¡El juego ha comenzado!"
        mensaje = f"El orden de los equipos es: {self.orden_equipos}. Comienza el equipo {self.orden_equipos[self.turno_equipo_actual]}."
        self.jugar(titulo, mensaje)

    def jugar(self, titulo, mensaje):
        if not self.juego_iniciado:
            return
        
        self.actualizar_tableros_clientes(titulo, mensaje, self.orden_equipos[self.turno_equipo_actual])

        equipo_actual = self.orden_equipos[self.turno_equipo_actual]
        print(f"Es el turno del equipo {equipo_actual}")

        self.habilitar_lanzamiento_equipo(equipo_actual)

    
    def habilitar_lanzamiento_equipo(self, equipo):
        hilos = []

        for uri in self.equipos[equipo]["uris"]:
            # Aquí se "congelan" los valores usando argumentos por defecto
            def habilitar():
                try:
                    with Pyro5.api.Proxy(uri) as cliente_proxy:
                        cliente_proxy.habilitar_lanzar()
                except Exception as e:
                    print(f"Error con {uri}: {e}")

            hilo = threading.Thread(target=habilitar)
            hilo.start()
            hilos.append(hilo)

    def lanzar(self, equipo, uri):
        puntaje = random.randint(int(self.dado_min), int(self.dado_max))
        recibidos = self.equipos[equipo]["recibidos"]
        recibidos[uri] = puntaje

        # Verificar si todos los jugadores ya lanzaron
        if len(recibidos) == len(self.equipos[equipo]["uris"]):
            puntos_avance = sum(recibidos.values())

            # Limpiar para el próximo turno
            self.equipos[equipo]["recibidos"] = {}

            # Finalizar turno (continúa el juego)
            self.finalizar_turno(equipo, puntos_avance)

    def finalizar_turno(self, equipo, puntos_avance):
        # Actualizar posición
        self.equipos[equipo]["posicion"] += puntos_avance

        # Verificar si ganó
        if int(self.equipos[equipo]["posicion"]) >= int(self.num_posiciones):
            hilos = []

            for equipo_id, datos_equipo in self.equipos.items():
                for uri in datos_equipo["uris"]:
                    # Aquí se "congelan" los valores usando argumentos por defecto
                    def lanzar_victoria(uri_actual=uri, equipo_actual=equipo_id):
                        try:
                            with Pyro5.api.Proxy(uri_actual) as cliente_proxy:
                                cliente_proxy.lanzar_victoria(equipo)
                        except Exception as e:
                            print(f"No se pudo mostrar ganadorar para jugador con {uri_actual} del equipo {equipo_actual}: {e}")

                    hilo = threading.Thread(target=lanzar_victoria)
                    hilo.start()
                    hilos.append(hilo)
            self.juego_iniciado = False
            return

        # Pasar al siguiente equipo y continuar el juego
        self.turno_equipo_actual = (self.turno_equipo_actual + 1) % len(self.orden_equipos)
        # titulo = "Juego"
        # mensaje = f"El equipo {equipo} ha lanzado y avanza {str(puntos_avance)} posiciones."
        titulo = "Juego"
        mensaje = f"El equipo {equipo} a lanzado avanzando {str(puntos_avance)} posiciones."

        self.jugar(titulo, mensaje)

                        
    def actualizar_tableros_clientes(self, titulo, mensaje, equipo):
        hilos = []

        for equipo_id, datos_equipo in self.equipos.items():
            for uri in datos_equipo["uris"]:
                def actualizar_tableros(uri_actual, equipo_actual):
                    try:
                        with Pyro5.api.Proxy(uri_actual) as cliente_proxy:
                            cliente_proxy.actualizar_tabla(self.equipos, titulo, mensaje, equipo)
                    except Exception as e:
                        print(f"No se pudo actualizar la tabla al miembro con uri {uri_actual} del equipo {equipo_actual}: {e}")

                # Lanzar hilo para cada cliente
                hilo = threading.Thread(target=actualizar_tableros, args=(uri, equipo_id))
                hilo.start()
                hilos.append(hilo)

        return True, "Tablas actualizadas en paralelo"
    
    #Necesaria para ventena    
    def obtener_datos_juego(self):  
        return self.equipos, self.num_posiciones
    
    def get_equipo_jugando(self):
        return self.orden_equipos[self.turno_equipo_actual]
    
    def get_num_equipos(self):
        if self.juego_iniciado:
            return len(self.equipos)
        else:
            return self.num_equipos