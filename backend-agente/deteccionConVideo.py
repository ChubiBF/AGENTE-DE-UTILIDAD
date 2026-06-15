

from ultralytics import YOLO
import cv2
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

load_dotenv()
#  API key
genai.configure(api_key= os.getenv("GEMINI_API_KEY", ""))
model_ia = genai.GenerativeModel('gemini-2.5-flash')

# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(m.name)

BASE_DIR = os.path.dirname(__file__)
local_model_path = os.path.join(BASE_DIR, 'best.pt')
model_path = local_model_path if os.path.exists(local_model_path) else 'best.pt'

if not os.path.exists(model_path):
    raise FileNotFoundError(f"No se encontró el archivo de pesos: {model_path}")

# el modelooo
model = YOLO(model_path)

print(model.names)
print("jacket" in model.names.values())

cap = cv2.VideoCapture(1)

ultima_ejecucion = 0
objetos_de_interes = ['laptop', 'book', 'cup', 'cell phone', 'backpack', 'umbrella', 'jacket']

def generar_prompt_para_agente(objetos):
    clima = "Lluvioso" 
    return f"""
    Actúa como un Asistente de Vuelo.
    Objetos detectados: {objetos}.
    Clima actual en La Paz: {clima}.
    Razona: ¿Tiene el usuario lo necesario para salir? Si detectas laptop pero no cargador, avisa. 
    Si detectas clima lluvioso y no hay paraguas, avisa. Responde brevemente.
    """

while True:
    ret, frame = cap.read()
    if not ret: break

    results = model(frame, stream=True)
    objetos_detectados = []
    
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            nombre = model.names[cls]
            if nombre in objetos_de_interes:
                objetos_detectados.append(nombre)
            
            # Dibujar rectángulos
            cv2.rectangle(frame, (int(box.xyxy[0][0]), int(box.xyxy[0][1])), 
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (0, 255, 0), 2)
            cv2.putText(frame, nombre, (int(box.xyxy[0][0]), int(box.xyxy[0][1]-10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
    objetos_unicos = list(set(objetos_detectados))
    tiempo_actual = time.time()
    
    if len(objetos_unicos) > 0 and (tiempo_actual - ultima_ejecucion > 15):
        print("Enviando contexto al Agente:", objetos_unicos)
        prompt_final = generar_prompt_para_agente(objetos_unicos)
        
        try:
            respuesta = model_ia.generate_content(prompt_final)
            print("\n--- Respuesta del Agente ---")
            print(respuesta.text)
            print("----------------------------\n")
            ultima_ejecucion = tiempo_actual
        except Exception as e:
            print(f"Error de conexión: {e}")

    cv2.imshow('Deteccion para HU-01', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()