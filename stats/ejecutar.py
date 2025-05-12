import subprocess
import os

# Obtener la ruta actual (directorio donde está ejecutar.py)
ruta_actual = os.path.dirname(__file__)

# Ejecutar el archivo stats.py (con ruta absoluta)
subprocess.run(['python', os.path.join(ruta_actual, 'stats.py')])

# Ejecutar el archivo ventana.py (con ruta absoluta)
subprocess.run(['python', os.path.join(ruta_actual, 'ventana.py')])
