import tkinter as tk
from PIL import Image, ImageTk

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Estadísticas de la partida")
ventana.resizable(False, False)

# Ajustar el tamaño de la ventana
ventana.geometry("800x600")  # Establecer una ventana más grande y estética
ventana.config(bg='white')

# Función para redimensionar la imagen
def redimensionar_imagen(imagen_path, width, height):
    imagen = Image.open(imagen_path)
    imagen_redimensionada = imagen.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(imagen_redimensionada)

# Cargar las imágenes y redimensionarlas a un tamaño mayor
imagenes = [
    redimensionar_imagen("graficos/cantidad_equipos_partida.png", 680, 450),
    redimensionar_imagen("graficos/cantidad_jugadores_partida.png", 680, 450),
    redimensionar_imagen("graficos/curvas_puntuacion_acumulada.png", 680, 450),
    redimensionar_imagen("graficos/jugadas_por_jugador.png", 680, 450),
    redimensionar_imagen("graficos/jugadores_creados_por_equipo.png", 680, 450),
]

# Crear una etiqueta para mostrar las imágenes
label_imagen = tk.Label(ventana, image=imagenes[0])
label_imagen.pack(padx=20, pady=20)  # Añadimos más espacio alrededor de la imagen

# Variable para llevar el control de la imagen actual
indice_imagen = 0

# Función para cambiar la imagen a la siguiente
def siguiente_imagen():
    global indice_imagen
    indice_imagen = (indice_imagen + 1) % len(imagenes)  # Ciclado de imágenes
    label_imagen.config(image=imagenes[indice_imagen])

# Función para cambiar la imagen a la anterior
def anterior_imagen():
    global indice_imagen
    indice_imagen = (indice_imagen - 1) % len(imagenes)  # Ciclado de imágenes
    label_imagen.config(image=imagenes[indice_imagen])

# Crear los botones para navegar entre las imágenes
boton_siguiente = tk.Button(ventana, text="Siguiente", command=siguiente_imagen, width=15, height=2, bg='#A7C7E7')
boton_siguiente.pack(side=tk.RIGHT, padx=10, pady=20)

boton_anterior = tk.Button(ventana, text="Anterior", command=anterior_imagen, width=15, height=2, bg='#A7C7E7')
boton_anterior.pack(side=tk.LEFT, padx=10, pady=20)

# Botón Cerrar
boton_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.quit, width=15, height=2, bg='red', fg='white')
boton_cerrar.pack(side=tk.BOTTOM, pady=20)

# Ejecutar el loop principal de la ventana
ventana.mainloop()
