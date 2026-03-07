from ultralytics import YOLO

#Funcion para detectar vehiculos y personas
class YoloCarril:
    def __init__(self, ruta_modelo="yolov8n.pt"):
        self.modelo = YOLO(ruta_modelo)
        self.categorias_autos = ["car", "truck", "bus", "motorcycle"]
        self.categorias_peatones = ["person"]