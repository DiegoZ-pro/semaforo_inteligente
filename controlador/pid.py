import control as ct
import numpy as np

from configuracion import (
    TIEMPO_VERDE_BASE, TIEMPO_VERDE_MIN, TIEMPO_VERDE_MAX,
    TIEMPO_AMARILLO, PID_KP, PID_KI, PID_KD,
    VEHICULOS_IDEAL,PEATONES_IDEAL, CARRILES
)

#Aqui ponemos un filtro para que los cambios respecto al "error" no sean tan duros (el estandar en 10 xd)
FILTRO_N = 10

# Pares sincronizados: verde simultáneo dentro de cada par de semaforos xd
PARES_SINCRONIZADOS = {
    "par_ns": ["norte", "sur"],
    "par_eo": ["este",  "oeste"],
}
class Controlador:

    def __init__(self):
        # Creamos la funcion de transferencia del PID
        # Formula: Kp + Ki/s + Kd*N*s/(s+N)
        self.pid = ct.TransferFunction(
            [PID_KD * FILTRO_N + PID_KP,
             PID_KP * FILTRO_N +PID_KI,
             PID_KI *FILTRO_N],
            [1, FILTRO_N,0]
        )
        print(f"Funcion de transferencia: {self.pid}")
#Calcula el tiempo que se aumentara al verde

    def _calcular_tiempo_par(self, carriles_par, conteos):
# Tomamos el peor caso dentro del par
        max_vehiculos = max(conteos[c]["vehiculos"] for c in carriles_par)
        max_peatones  = max(conteos[c]["peatones"]  for c in carriles_par)

    
        error_vehiculos = max_vehiculos - VEHICULOS_IDEAL
        error_peatones  = max_peatones  - PEATONES_IDEAL
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

#Aqui decide que par de semaforos arranca primero

    def _ordenar_pares(self, conteos):
        def congestion_par(nombre_par):
            carriles =PARES_SINCRONIZADOS[nombre_par]
            return sum(
                conteos[c]["vehiculos"] + conteos[c]["peatones"]
                for c in carriles
            )
        return sorted(PARES_SINCRONIZADOS.keys(),
                      key= congestion_par,
                      reverse=True)
    def ciclo(self, conteos):
        # Devuelve la lista de carriles con su tiempo verde y amarillo
        orden_pares =self._ordenar_pares(conteos)
        fases = []
        for nombre_par in orden_pares:
            carriles_par = PARES_SINCRONIZADOS[nombre_par]
            tiempo_verde = self._calcular_tiempo_par(carriles_par, conteos)
#ambis verdes estaran juntos (pares)
            fases.append({
                "par":          nombre_par,
                "carriles":     carriles_par,          
                "tiempo_verde": tiempo_verde,
                "tiempo_amarillo": TIEMPO_AMARILLO,
            })

            print(
                f"  [{nombre_par.upper()}] "
                f"Carriles {carriles_par} → "
                f"Verde: {tiempo_verde}s | Amarillo: {TIEMPO_AMARILLO}s"
            )

        return fases
