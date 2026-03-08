import matplotlib.pyplot as plt
import numpy as np

from configuracion          import CARRILES, VIDEOS
from deteccion.detector     import Detector
from controlador.pid_semaforo import ControladorPID
from semaforo.semaforo      import Semaforo, mostrar_resumen_ciclos


def calcular_flujo(autos, peatones):
    flujo_vehiculos = min(autos / 10.0, 1.0)
    flujo_peatones  = min(peatones / 6.0, 1.0)
    return flujo_vehiculos, flujo_peatones


def graficar_resultados(historial_errores, historial_tiempos, carriles_usados):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
    fig.suptitle("Semáforo Inteligente - Respuesta del Controlador PID", fontsize=13)

    ciclos = list(range(1, len(historial_errores) + 1))

    ax1.plot(ciclos, historial_errores, marker='o', color='tomato', linewidth=2)
    ax1.axhline(0, color='gray', linestyle='--', linewidth=1)
    ax1.set_title("Error del sistema (flujo real - setpoint)")
    ax1.set_xlabel("Ciclo")
    ax1.set_ylabel("Error")
    ax1.grid(True, alpha=0.4)

    if len(carriles_usados) == len(ciclos):
        ax1.set_xticks(ciclos)
        ax1.set_xticklabels(carriles_usados, rotation=15)

    colores_barras = ['#4CAF50' if t >= 30 else '#FF9800' for t in historial_tiempos]
    ax2.bar(ciclos, historial_tiempos, color=colores_barras, edgecolor='white')
    ax2.axhline(30, color='gray', linestyle='--', linewidth=1, label='Tiempo base (30s)')
    ax2.set_title("Tiempo verde calculado por el PID (segundos)")
    ax2.set_xlabel("Ciclo")
    ax2.set_ylabel("Tiempo verde (s)")
    ax2.legend()
    ax2.grid(True, alpha=0.4, axis='y')

    if len(carriles_usados) == len(ciclos):
        ax2.set_xticks(ciclos)
        ax2.set_xticklabels(carriles_usados, rotation=15)

    plt.tight_layout()
    plt.savefig("resultados_pid.png", dpi=150)
    print("\n  Gráfico guardado como: resultados_pid.png")
    plt.show()


def main():
    print("\n" + "="*55)
    print("   SISTEMA DE SEMÁFORO INTELIGENTE - PID + YOLO")
    print("="*55)

    detector    = Detector(ruta_modelo="yolov8n.pt")
    controlador = ControladorPID()

    historial_completo  = []
    historial_errores   = []
    historial_tiempos   = []
    carriles_procesados = []

    for nombre_carril in CARRILES:
        print(f"\n{'─'*55}")
        print(f"  Procesando carril: {nombre_carril.upper()}")
        print(f"{'─'*55}")

        ruta_video = VIDEOS[nombre_carril]

        print("  [1] Detección YOLO...")
        cantidad_autos, cantidad_peatones = detector.analizar_video(ruta_video)
        print(f"      Autos detectados:    {cantidad_autos}")
        print(f"      Peatones detectados: {cantidad_peatones}")

        flujo_vehiculos, flujo_peatones = calcular_flujo(cantidad_autos, cantidad_peatones)
        print(f"  [2] Flujo vehicular: {flujo_vehiculos:.2f}  |  Flujo peatonal: {flujo_peatones:.2f}")

        print("  [3] Calculando tiempo verde con PID...")
        tiempo_verde, error, ajuste = controlador.calcular_tiempo_verde(
            flujo_vehiculos, flujo_peatones
        )
        print(f"      Error del sistema: {error:.2f}")
        print(f"      Ajuste del PID:    {ajuste:.2f}s")
        print(f"      Tiempo verde final: {tiempo_verde}s")

        historial_errores.append(error)
        historial_tiempos.append(tiempo_verde)
        carriles_procesados.append(nombre_carril)

        print("  [4] Simulando semáforo...")
        semaforo = Semaforo(nombre_carril)
        resultado = semaforo.ejecutar_ciclo(tiempo_verde, modo_rapido=True)

        resultado["flujo_autos"]    = f"{flujo_vehiculos:.2f}"
        resultado["flujo_peatones"] = f"{flujo_peatones:.2f}"
        historial_completo.append(resultado)

        controlador.resetear()

    mostrar_resumen_ciclos(historial_completo)

    print("  Generando gráfica de resultados...")
    graficar_resultados(historial_errores, historial_tiempos, carriles_procesados)

    print("\n  Sistema finalizado correctamente.\n")


if __name__ == "__main__":
    main()