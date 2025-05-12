# Juego Distribuido - Sistemas Distribuidos

Este proyecto implementa un **juego de tablero distribuido** en Python utilizando **Pyro5** para comunicación remota entre procesos y **Tkinter** para la interfaz gráfica de los clientes. Incluye además un sistema de **logging distribuido**, análisis posterior del juego y visualización de estadísticas.

---
### Lenguaje

- **Python 3** 

### Frameworks y Bibliotecas

- [Pyro5](https://pyro5.readthedocs.io/) - Comunicación RPC entre procesos distribuidos.
- `Tkinter` - Interfaz gráfica local de cada cliente (incluido por defecto en Python).
- `threading` - Gestión de hilos en cliente y servidor.
- `subprocess` - Para lanzar procesos secundarios desde el servidor.
- `pandas`, `matplotlib` - Análisis y visualización de estadísticas (en `stats/`).
- `logging` - Registro estructurado de eventos para auditoría, debugging y trazabilidad del sistema distribuido.
- `dotenv` - Carga de variables de entorno desde archivos `.env`, para configurar rutas, puertos o claves sin exponerlas en el código.

## Despliegue del servidor y ejecución

Clonar el repositorio con el siguiente comando: 

```bash
git clone https://github.com/RodrigoVargasSanchez/S_Distribuidos_Juego.git
cd S_Distribuidos_Juego
```

Pasos a seguir para el despliegue:

  Primero necesitaremos tener previamente minimo **5 terminales** abierto, con diferentes funcionalidades.
  * 1. Iniciar el Name Server de Pyro5

  Debe estar activo antes de iniciar el servidor. Para hacer esto ejecute en una de las terminales el siguiente comando:
  
```bash
cd server
python -m Pyro5.nameserver
```
  * 2. Ejecutar el servidorRMI (En otra terminal)
  
```bash
cd server
python servidorRMI.py
```

  * 3. Ejecutar el servidor (En otra terminal)
  
```bash
cd server
python servidor.py
```

  * 4. Ejecutar clientes (En uno o más equipos o terminales distintos:

```bash
cd client
python main.py
```

Cada cliente visualizará su interfaz de juego.


# Explicación archivo `.env`

## `.env` del Server

### Variables del juego

```bash
DADO_MIN = 1
```
Es el valor mínimo que se puede obtener cuando un jugador lanza el dado. En este caso, representa el número más bajo posible: 1.

```bash
DADO_MAX = 6
```
Representa el valor máximo que se puede obtener al lanzar el dado.

### Configuración del tablero
```bash
NUM_POSICIONES = 100
```
Indica cuántas posiciones hay en el tablero. Un equipo gana la partida si alguno de sus jugadores alcanza (o supera) esta cantidad de casillas.

### Configuración de los jugadores
```bash
NUM_JUGADORES = 3
```
Define cuántos jugadores componen cada equipo.

```bash
NUM_EQUIPOS = 7
```
Cantidad de equipos que pueden participar en la partida.

Archivos y logs: 

```bash
PATH_LOGS = '../stats/logs_centralizados.log'
```
Ruta donde se guardan los logs centralizados del juego. Esta ruta es relativa al directorio desde donde se ejecuta el servidor.

***Todas estas variables son modificables por el usuario a gusto.***

Luego, estos logs pueden ser procesados por "stats/ejecutar.py".

## `.env` del Cliente

### Ruta proxy

```bash
HOST_SERVER_RMI=PYRONAME:servidor.logs@localhost:9090
```

Esta es la URI que permite al clienteRMI conectarse al objeto remoto del servidorRMI usando Pyro5. Funciona de la siguiente forma:

  `PYRONAME:` indica que se usará el Name Server para resolver el objeto remoto.

  `servidor.logs` es el nombre lógico registrado en el Name Server por el servidor RMI.

  `@localhost:9090` especifica la dirección y puerto donde se está ejecutando el Name Server.
