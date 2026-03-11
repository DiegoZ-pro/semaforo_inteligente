import cv2
import time
import numpy as np
from ultralytics import YOLO

from configuracion import CARRILES, VIDEOS, TIEMPO_AMARILLO
from controlador.pid import Controlador

# BGR porque opencv no usa RGB normal >:(
VRD = (0, 255, 0)       # verde
AMR = (0, 255, 255)     # amarillo
RJO = (0, 0, 255)       # rojo
OFF = (50, 50, 50)      # luz apagada

# estos son los autos y motos que queremos detectar
# los camiones tambien cuentan porque ocupan mas espacio
AUTOS = ["car", "truck", "bus", "motorcycle"]

class Semaforo:

    def __init__(self):
        # cargamos el modelo pequeño porque el grande es muy lento en mi pc
        self.modelo = YOLO("yolov8n.pt")
        self.pid = Controlador()

        # todos empiezan en rojo hasta que el sistema calcule los tiempos
        self.estado = {
            "norte": "rojo",
            "sur":"rojo",
            "este":"rojo",
            "oeste": "rojo"
        }

        # aqui guardamos cuantos autos/peatones hay en cada carril
        # esto lo usa el PID para calcular el tiempo verde
        self.cnt = {
            "norte": {"vehiculos": 0, "peatones": 0},
            "sur":{"vehiculos": 0, "peatones": 0},
            "este":{"vehiculos": 0, "peatones": 0},
            "oeste":{"vehiculos": 0, "peatones": 0}
        }

        # abrimos los 4 videos al mismo tiempo
        self.caps = {
            "norte": cv2.VideoCapture(VIDEOS["norte"]),
            "sur":cv2.VideoCapture(VIDEOS["sur"]),
            "este":cv2.VideoCapture(VIDEOS["este"]),
            "oeste": cv2.VideoCapture(VIDEOS["oeste"])
        }

        # cuanto tiempo queda en el semaforo actual
        self.t_restante = {c: 0 for c in CARRILES}

    def detectar_objetos(self, carril, frm):
        res = self.modelo(frm, verbose=False)
        n_autos = 0
        n_personas = 0

        for obj in res[0].boxes:
            cls = self.modelo.names[int(obj.cls)]
            x1, y1, x2, y2 = map(int, obj.xyxy[0])

            if cls in AUTOS:
                n_autos += 1
                # cuadro verde para autos
                cv2.rectangle(frm, (x1,y1), (x2,y2), VRD, 2)
                cv2.putText(frm, cls, (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, VRD, 1)

            elif cls == "person":
                n_personas += 1
                # azul para personas porque sino se confunde con los autos
                cv2.rectangle(frm, (x1,y1), (x2,y2), (255,0,0), 2)
                cv2.putText(frm, "persona", (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,0,0), 1)

        # guardamos el conteo para que el PID lo use despues
        self.cnt[carril]["vehiculos"] = n_autos
        self.cnt[carril]["peatones"]= n_personas
        return frm

    def poner_semaforo(self, frm, carril):
        est = self.estado[carril]

        # dibujamos el semaforo en la esquina derecha
        # rojo arriba, amarillo en medio, verde abajo (igual que en la vida real)
        cv2.circle(frm, (590, 35),  14, RJO if est=="rojo" else OFF, -1)
        cv2.circle(frm, (590, 70),  14, AMR if est=="amarillo" else OFF, -1)
        cv2.circle(frm, (590, 105), 14, VRD if est=="verde"else OFF, -1)

        cv2.putText(frm, carril.upper(), (8, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
        cv2.putText(frm, f"autos:{self.cnt[carril]['vehiculos']}", (8, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, VRD, 2)
        cv2.putText(frm, f"personas:{self.cnt[carril]['peatones']}", (8, 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,100,0), 2)
        cv2.putText(frm, f"tiempo:{self.t_restante[carril]}s", (8, 101),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, AMR, 2)
        return frm

    def get_frames(self):
        fms = {}
        for carril in CARRILES:
            if self.estado[carril] == "rojo":
# congelamos el frame — los autos no avanzan en rojo
                if hasattr(self, '_ultimo_frame') and carril in self._ultimo_frame:
                    frm = self._ultimo_frame[carril].copy()
                else:
                    _, frm = self.caps[carril].read()
            else:
# verde o amarillo — avanzamos el video
                ok, frm = self.caps[carril].read()
                if not ok:
                    self.caps[carril].set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frm = self.caps[carril].read()
                if not hasattr(self, '_ultimo_frame'):
                    self._ultimo_frame = {}
                self._ultimo_frame[carril] = frm.copy()

            frm = self.detectar_objetos(carril, frm) 
            frm = self.poner_semaforo(frm, carril)
            frm = cv2.resize(frm, (640, 360))
            fms[carril] = frm
        return fms

    def mostrar(self, fms):
        # ponemos norte y sur arriba, este y oeste abajo
        arriba = np.hstack([fms["norte"], fms["sur"]])
        abajo  = np.hstack([fms["este"], fms["oeste"]])
        cv2.imshow("Semaforo Inteligente", np.vstack([arriba, abajo]))

    def ejecutar(self):
        print("iniciando sistema...")

        while True:
            # el PID nos dice cuanto verde le toca a cada par segun los conteos
            fases = self.pid.ciclo(self.cnt)

            for fase in fases:
                par = fase["par"]
                tv = fase["tiempo_verde"]
                c_vrd = fase["carriles"]       # carriles que se ponen en verde
                c_rjo= ["este","oeste"] if par == "par_ns" else ["norte","sur"]

                print(f"verde: {c_vrd} | rojo: {c_rjo} | {tv}s")

                for c in c_vrd: self.estado[c]= "verde"
                for c in c_rjo: self.estado[c] ="rojo"

                # fase verde: mostramos video hasta que se acabe el tiempo
                t0 = time.time()
                while time.time() - t0 < tv:
                    seg_left = int(tv - (time.time() - t0))
                    for c in c_vrd: self.t_restante[c] = seg_left
                    for c in c_rjo: self.t_restante[c] = 0

                    self.mostrar(self.get_frames())
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        self.cerrar()
                        return

                # fase amarillo: avisamos que va a cambiar
                for c in c_vrd: self.estado[c] = "amarillo"

                t1 = time.time()
                while time.time() - t1 < TIEMPO_AMARILLO:
                    seg_left = int(TIEMPO_AMARILLO - (time.time() - t1))
                    for c in c_vrd: self.t_restante[c] = seg_left

                    self.mostrar(self.get_frames())
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        self.cerrar()
                        return

    def cerrar(self):
        for cap in self.caps.values():
            cap.release()
        cv2.destroyAllWindows()
        print("sistema cerrado")