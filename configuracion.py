#Configuración del Semáforo Inteligente

# Tiempos base del semáforo
TIEMPO_VERDE_BASE = 30      
TIEMPO_VERDE_MIN  = 10      
TIEMPO_VERDE_MAX  = 60      
TIEMPO_AMARILLO   = 3       

# Parámetros del PID
PID_KP = 1.2
PID_KI = 0.08
PID_KD = 0.3

# Flujo vehicular "ideal"
SETPOINT_AUTOS    = 5       
SETPOINT_PEATONES = 3       

# Nombres de los carriles
CARRILES = ["norte", "sur", "este", "oeste"]

# Rutas de los videos
VIDEOS = {
    "norte": "videos/carril_norte.mp4",
    "sur":   "videos/carril_sur.mp4",
    "este":  "videos/carril_este.mp4",
    "oeste": "videos/carril_oeste.mp4",
}
