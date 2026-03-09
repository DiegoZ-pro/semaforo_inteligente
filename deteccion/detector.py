from ultralytics import YOLO
import cv2
#Funcion para detectar vehiculos y personas
class Carril:
    def __init__(self,ruta_modelo="yolov8n.pt"):
        self.modelo = YOLO(ruta_modelo)
        self.categorias_vehiculos = ["car", "truck", "bus", "motorcycle"]
        self.categorias_peatones = ["person"]
        
    #Funcion para que YOLO analice el video
    def analizar_video(self, ruta_video):
        video = cv2.VideoCapture(ruta_video)

        conteos_vehiculos= []
        conteos_peatones = []
        numero_frame =0

        print(f"Analizando video: {ruta_video}")

        while True:
            hay_frame, frame = video.read()
            if not hay_frame:
                break

            resultados = self.modelo(frame, verbose=False)

            vehiculos_en_frame= 0
            peatones_en_frame =0

            for objeto in resultados[0].boxes:
                categoria = self.modelo.names[int(objeto.cls)]

                # Contamos los objetos
                if categoria in self.categorias_vehiculos:
                    vehiculos_en_frame += 1
                if categoria in self.categorias_peatones:
                    peatones_en_frame += 1

                # Dibujamos el cuadro alrededor del objeto
                x1, y1, x2, y2 = map(int, objeto.xyxy[0])

                # Verde para autos y azul para peatones
                if categoria in self.categorias_vehiculos:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Etiqueta con el nombre del objeto
                cv2.putText(frame, categoria, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Contador de auto y personas
            cv2.putText(frame, f"Autos: {vehiculos_en_frame}",(10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),2)
            cv2.putText(frame, f"Peatones:{peatones_en_frame}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0),2)

            # Lo mostramos en pantalla
            cv2.imshow("Semaforo Inteligente", frame)

            # Q para salir
            if cv2.waitKey(1) & 0xFF ==ord("q"):
                break

            conteos_vehiculos.append(vehiculos_en_frame)
            conteos_peatones.append(peatones_en_frame)

            numero_frame += 1

        video.release()
        cv2.destroyAllWindows()

        if len(conteos_vehiculos)== 0:
            return 0, 0

        maximo_vehiculos = max(conteos_vehiculos)
        maximo_peatones = max(conteos_peatones)

        return maximo_vehiculos, maximo_peatones

# IMPORTANTE
# ELIMINAR DE ACA PARA ABAJO CUANDO SE AGREGUE EL ARCHIVO "main.py"

if __name__ == "__main__":

    # Simulamos lo que hará main.py con los 4 carriles
    detector = Carril()

    resultados_carriles = {}

    videos = {
        "norte": "videos/carril_norte.mp4",
        "sur":   "videos/carril_sur.mp4",
        "este":  "videos/carril_este.mp4",
        "oeste": "videos/carril_oeste.mp4",
    }

    for carril, ruta in videos.items():
        print(f"\n── Carril {carril.upper()} ──")
        autos, peatones = detector.analizar_video(ruta)
        resultados_carriles[carril] = {
            "autos": autos,
            "peatones": peatones
        }

    # Mostramos el resumen final como lo verá main.py
    print("\n═══════════════════════════")
    print("     RESUMEN FINAL")
    print("═══════════════════════════")
    for carril, datos in resultados_carriles.items():
        print(f"Carril {carril.upper()}: {datos['autos']} autos, {datos['peatones']} peatones")
    print("═══════════════════════════")