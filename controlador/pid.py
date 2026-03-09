import control as ct
import numpy as np

from configuracion import (
    TIEMPO_VERDE_BASE, TIEMPO_VERDE_MIN, TIEMPO_VERDE_MAX,
    TIEMPO_AMARILLO, PID_KP, PID_KI, PID_KD,
    VEHICULOS_IDEAL,PEATONES_IDEAL, CARRILES
)

#Aqui ponemos un filtro para que los cambios respecto al "error" no sean tan duros (el estandar en 10 xd)
FILTRO_N = 10

class Controlador:

    def __init__(self):
        # Creamos la funcion de transferencia del PID
        # Formula: Kp + Ki/s + Kd*N*s/(s+N)
        self.pid = ct.TransferFunction(
            [PID_KD * FILTRO_N + PID_KP,
             PID_KP * FILTRO_N +PID_KI,
             PID_KI *FILTRO_N],
            [1, FILTRO_N, 0]
        )
        print(f"Funcion de transferencia: {self.pid}")
#Calcula el tiempo que se aumentara al verde

    def calcular_tiempo_verde(self, vehiculos, peatones):
# Se calcula un tiempo bueno para el verde
        error_vehiculos=vehiculos - VEHICULOS_IDEAL
        error_peatones =peatones - PEATONES_IDEAL

    
        error = max(error_vehiculos, error_peatones)

#Simulamos la respuesta del PID durante 5 segundos
        t = np.linspace(0, 5, 100)
        entrada = np.ones_like(t) * error

        t_out, y_out = ct.forced_response(self.pid, t, entrada)

#Tomamos el ajuste final que calculo el PID
        ajuste = y_out[-1]

# Calculamos el tiempo verde final
        tiempo = TIEMPO_VERDE_BASE + ajuste

# Nos aseguramos de no salir de los limites
        tiempo = max(TIEMPO_VERDE_MIN, min(TIEMPO_VERDE_MAX, tiempo))

        return round(tiempo)

    def decidir_orden(self, conteos):
        # Ordenamos de mayor a menor congestion
        # sumando vehiculos y peatones de cada carril
        return sorted(
            conteos,
            key=lambda c: conteos[c]["vehiculos"] + conteos[c]["peatones"],
            reverse=True
        )

    def ciclo(self, conteos):
        # Devuelve la lista de carriles con su tiempo verde y amarillo
        orden = self.decidir_orden(conteos)
        return [
            (
                carril,
                self.calcular_tiempo_verde(
                    conteos[carril]["vehiculos"],
                    conteos[carril]["peatones"]
                ),
                TIEMPO_AMARILLO
            )
            for carril in orden
        ]


# Prueba rapida
if __name__ == "__main__":
    from configuracion import VIDEOS
    from deteccion.detector import Carril  
    detector    = Carril()                 
    controlador = Controlador()

    # Analizamos los 4 videos con YOLO
    conteos = {}
    for carril, ruta in VIDEOS.items():
        vehiculos, peatones = detector.analizar_video(ruta)
        conteos[carril] = {
            "vehiculos": vehiculos,
            "peatones":  peatones
        }
        print(f"Carril {carril}: {vehiculos} vehiculos, {peatones} peatones")

    print("─────────────────────────")
    print("Orden segun congestion:")
    orden = controlador.decidir_orden(conteos)
    print(f"  {orden}")

    print("─────────────────────────")
    print("Tiempos calculados:")
    ciclo = controlador.ciclo(conteos)
    for carril, verde, amarillo in ciclo:
        print(f"  Carril {carril}: {verde} seg verde, {amarillo} seg amarillo")
    print("─────────────────────────")