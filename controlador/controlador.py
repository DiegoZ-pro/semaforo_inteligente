from simple_pid import PID
from configuracion import (
    TIEMPO_VERDE_BASE, TIEMPO_VERDE_MIN, TIEMPO_VERDE_MAX,
    TIEMPO_AMARILLO, PID_KP, PID_KI, PID_KD,
    SETPOINT_AUTOS, SETPOINT_PEATONES, CARRILES
)

class Controlador:
    def __init__(self):
        # PID por carril, uno para autos y otro para peatones
        self.pids = {
            carril: {
                "autos": PID(PID_KP, PID_KI, PID_KD, setpoint=SETPOINT_AUTOS),
                "peatones": PID(PID_KP, PID_KI, PID_KD, setpoint=SETPOINT_PEATONES),
            }
            for carril in CARRILES
        }

        # limite del PID a un rango permitido
        for carril in self.pids:
            for pid in self.pids[carril].values():
                pid.output_limits = (TIEMPO_VERDE_MIN - TIEMPO_VERDE_BASE,
                                     TIEMPO_VERDE_MAX - TIEMPO_VERDE_BASE)

    def calcular_tiempo_verde(self, carril, autos, peatones):
        # Ajuste del PID según el conteo 
        ajuste_autos = self.pids[carril]["autos"](autos)
        ajuste_peatones = self.pids[carril]["peatones"](peatones)

        # Definición del tiempo final 
        ajuste = max(ajuste_autos, ajuste_peatones)
        tiempo = TIEMPO_VERDE_BASE + ajuste

        return round(max(TIEMPO_VERDE_MIN, min(TIEMPO_VERDE_MAX, tiempo)))

    def decidir_orden(self, conteos):
        # Carriles de mayor a menor congestión
        return sorted(conteos, key=lambda c: conteos[c]["autos"], reverse=True)

    def ciclo(self, conteos):
        # devolucion de la lista, amarillo, verde, autos y peatones
        orden = self.decidir_orden(conteos)
        return [
            (carril,
             self.calcular_tiempo_verde(carril,
                conteos[carril]["autos"],
                conteos[carril]["peatones"]),
             TIEMPO_AMARILLO)
            for carril in orden
        ]