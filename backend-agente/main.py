from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from ultralytics import YOLO
import google.generativeai as genai
import google.api_core.exceptions  
from dotenv import load_dotenv
import os
from typing import Optional

from services.clima import obtener_pronostico_la_paz

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


genai.configure(api_key= os.getenv("GEMINI_API_KEY", ""))
model_ia = genai.GenerativeModel('gemini-2.5-flash')


model_base = YOLO('yolov8n.pt') 
model_custom = YOLO('best.pt') 

@app.post("/analizar-foto/")
async def analizar_foto(
    file: UploadFile = File(...),
    nombre: str = Form(...),
    ocupacion: str = Form(...),
    destino: Optional[str] = Form(default="")
    ):
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return {"error": "No se pudo decodificar la imagen. Envíe un archivo válido."}
        
    print(f"Imagen recibida: Tamaño {frame.shape}")
    cv2.imwrite("debug_imagen.jpg", frame) 

    
    interes_base = ['laptop', 'cup', 'cell phone', 'backpack', 'umbrella', 'bottle']
    interes_custom = ['pen', 'notebook', 'charger', 'canillera', 'sport_shoes', 'keys', 'wallet', 'jacket', 'cream', 'cap']
    
    
    umbrales_custom = {
        'sport_shoes': 0.80,  
        'jacket': 0.45,       
        'notebook': 0.35,
        'pen': 0.30,
        'canillera': 0.30,
        'keys': 0.12,         
        'wallet': 0.12,       
        'charger': 0.01       
    }
    
    
    results_base = model_base(frame, conf=0.25)
    objetos_base = [model_base.names[int(box.cls[0])] for r in results_base for box in r.boxes]
    detectados_base = [o for o in objetos_base if o in interes_base]
    print("Objetos modelo base:", detectados_base)
    
    
    results_custom = model_custom(frame) 
    detectados_custom = []
    
    for r in results_custom:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            nom_clase = model_custom.names[cls_id]
            conf_detectada = float(box.conf[0])
            
            
            umbral_minimo = umbrales_custom.get(nom_clase, 0.25)
            
            
            if nom_clase in interes_custom and conf_detectada >= umbral_minimo:
                detectados_custom.append(nom_clase)
                print(f" -> ACEPTADO: {nom_clase} con confianza {conf_detectada:.2f} (Mínimo requerido: {umbral_minimo})")
            else:
                if nom_clase in interes_custom:
                    print(f" -> RECHAZADO: {nom_clase} con confianza {conf_detectada:.2f} (No alcanzó el {umbral_minimo})")

    print("Objetos filtrados modelo customizado:", detectados_custom)
    
    
    objetos_relevantes = list(set(detectados_base + detectados_custom))
    print("Objetos combinados finales:", objetos_relevantes)
    
    info_destino = f"\n- Destino de salida: {destino}" if destino else ""
    clima = obtener_pronostico_la_paz()
    
    
    prompt = f"""
    Actúa como un Agente de Preparación de Viajes/Salidas Diarias. Tu objetivo es la tasa de error cero en la salida del usuario.
    1. Fase de Observación: Analiza los objetos detectados en la mesa.
    2. Fase de Contexto: Cruza los datos con el clima actual de La Paz y el destino del usuario.
    3. Fase de Razonamiento:
       - ¿El set de llaves ('keys') y la billetera ('wallet') están presentes? (Seguridad crítica).
       - ¿El hardware detectado (como 'laptop' o 'cell phone') cuenta con sus accesorios de energía ('charger')? (Continuidad).
       - ¿Hay elementos faltantes para el pronóstico climático detectado?
    4. Fase de Acción: Si faltan elementos emite una advertencia. Si está completo valida la salida con éxito.
    
    ESTA ES LA INFORMACIÓN RECOPILADA:
        Perfil del usuario:
        - Nombre: {nombre}
        - Ocupación: {ocupacion}
        {info_destino}
        
        Contexto actual:
        Objetos detectados: {objetos_relevantes}.
        Clima actual en La Paz: {clima}.
        
    Responde siempre con un tono de 'Asistente de salidas' personalizado, dirigiéndote a {nombre}, priorizando la claridad y la brevedad.
    """
    
    try:
        print(f"Invocando API de Gemini... Clima: {clima}")
        respuesta = model_ia.generate_content(prompt)
        texto_final = respuesta.text
    except google.api_core.exceptions.ResourceExhausted:
        print("Límite de cuota de Gemini alcanzado (429). Ejecutando respuesta de respaldo técnica.")
        
        texto_final = f"¡Hola {nombre}! Veo que estás listo para salir hacia tu destino. El Agente de IA se encuentra procesando múltiples solicitudes en este momento (Límite de cuota API excedido), sin embargo, tu inventario físico local se ha detectado exitosamente: {', '.join(objetos_relevantes) if objetos_relevantes else 'Ninguno'}."
    except Exception as e:
        print(f"Error inesperado en el LLM: {str(e)}")
        texto_final = f"Hola {nombre}, se generó un inconveniente al procesar tus consejos de salida. Error técnico: {str(e)}"
        
    return {
        "objetos": objetos_relevantes,
        "respuesta": texto_final
    }