import Pyro5.api
import random
import threading

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, max_posiciones=100, dado_min=1, dado_max=6):
        self.max_posiciones = max_posiciones
        self.dado_min = dado_min
        self.dado_max = dado_max

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
        hilos = []

        for equipo_id, datos_equipo in self.equipos.items():
            for uri in datos_equipo["uris"]:
                def lanzar_juego(uri_actual, equipo_actual):
                    try:
                        with Pyro5.api.Proxy(uri_actual) as cliente_proxy:
                            cliente_proxy.iniciar_juego()
                            print(f"Se inició el juego al integrante con uri {uri_actual} del equipo {equipo_actual}")
                    except Exception as e:
                        print(f"No se pudo iniciar el juego para el miembro con uri {uri_actual} del equipo {equipo_actual}: {e}")

                # Lanzar hilo para cada cliente
                hilo = threading.Thread(target=lanzar_juego, args=(uri, equipo_id))
                hilo.start()
                hilos.append(hilo)

        # (Opcional) Esperar a que todos terminen, si quieres bloquear hasta que finalicen
        # for hilo in hilos:
        #     hilo.join()

        return True, "Juegos iniciados en paralelo"

    #Necesaria para ventena    
    def obtener_datos_juego(self):  
        return self.equipos, self.max_posiciones
    
    
    #Necesaria para ventana
    def lanzar_dado_servidor(self, nombre, equipo, uri_cliente):
        numero = random.randint(self.dado_min, self.dado_max)

        if equipo in self.equipos and nombre in self.equipos[equipo]["integrantes"]:
            nueva_posicion = self.equipos[equipo]["posicion"] + numero

            if nueva_posicion > self.max_posiciones:
                nueva_posicion = self.max_posiciones
                ganador = True
            else:
                ganador = False

            self.equipos[equipo]["posicion"] = nueva_posicion

            self.actualizar_tableros_clientes()

            return numero, nueva_posicion, ganador
        else:
            print(f"No se encontró el equipo {equipo} o el jugador {nombre} no pertenece a ese equipo.")
            return None, None
        
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