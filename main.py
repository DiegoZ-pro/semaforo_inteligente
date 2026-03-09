
from configuracion import CARRILES, VIDEOS
from deteccion.detector import Carril


def main():
    print("\n" + "="*55)
    print("SISTEMA DE SEMÁFORO INTELIGENTE - PID + YOLO")
    print("="*55)

#Inicializo el detector con el modelo de YOLO
    detector = Carril(ruta_modelo="yolov8n.pt")

# Proceso cada carril uno por uno
    for nombre_carril in CARRILES:
        print(f"\n{'─'*55}")
        print(f" Procesando carril:{nombre_carril.upper()}")
        print(f"{'─'*55}")

        ruta_video = VIDEOS[nombre_carril]
#nYOLO
        print("YOLO")
        maximo_vehiculos, maximo_peatones = detector.analizar_video(ruta_video)

        print(f"Vehículos detectados: {maximo_vehiculos}")
        print(f"Peatones detectados:  {maximo_peatones}")
# meustra resultados
        print(f"Controlador PID: pendiente")
        print(f"Simulación semáforo: pendiente")

    print("\n  Detección finalizada.\n")

if __name__ == "__main__":
    main()