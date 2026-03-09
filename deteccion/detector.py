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

        conteos_vehiculos=[]
        conteos_peatones =[]

#Aqui analiza todo el video por frames
        print(f"Analizando video: {ruta_video}")

        while True:
            hay_frame,frame = video.read()
            if not hay_frame:
                break
            resultados = self.modelo(frame, verbose=False)

            vehiculos_en_frame    =0
            peatones_en_frame =0
            for objeto in resultados[0].boxes:
                categoria =self.modelo.names[int(objeto.cls)]

                if categoria in self.categorias_vehiculos:
                        vehiculos_en_frame +=1

                if categoria in self.categorias_peatones:
                        peatones_en_frame +=1

            conteos_vehiculos.append(vehiculos_en_frame)
            conteos_peatones.append(peatones_en_frame)

 # Se cierra el video
        video.release()

#Conteo de el maximo de autos y peatoness
        maximo_autos= max(conteos_vehiculos)
        maximo_peatones =max(conteos_peatones)       
        return maximo_autos, maximo_peatones
