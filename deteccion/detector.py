from ultralytics import YOLO
import cv2

class Carril:
    def __init__(self, ruta_modelo="yolov8n.pt"):
        self.modelo = YOLO(ruta_modelo)
        self.categorias_vehiculos = ["car", "truck", "bus", "motorcycle"]
        self.categorias_peatones = ["person"]

    def analizar_video(self, ruta_video):
        video = cv2.VideoCapture(ruta_video)

        conteos_vehiculos = []
        conteos_peatones  = []

        print(f"Analizando video: {ruta_video}")

        while True:
            hay_frame, frame = video.read()
            if not hay_frame:
                break

            resultados = self.modelo(frame, verbose=False)

            vehiculos_en_frame = 0
            peatones_en_frame  = 0

            for objeto in resultados[0].boxes:
                categoria = self.modelo.names[int(objeto.cls)]

                if categoria in self.categorias_vehiculos:
                    vehiculos_en_frame += 1
                if categoria in self.categorias_peatones:
                    peatones_en_frame += 1

                x1, y1, x2, y2 = map(int, objeto.xyxy[0])
                color = (0, 255, 0) if categoria in self.categorias_vehiculos else (255, 0, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, categoria, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            cv2.putText(frame, f"Autos: {vehiculos_en_frame}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Peatones: {peatones_en_frame}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow("Semaforo Inteligente", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            conteos_vehiculos.append(vehiculos_en_frame)
            conteos_peatones.append(peatones_en_frame)

        video.release()
        cv2.destroyAllWindows()

        if len(conteos_vehiculos) == 0:
            return 0, 0

        return max(conteos_vehiculos), max(conteos_peatones)