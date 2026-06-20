import cv2
import os
import time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

from services.clima import obtener_pronostico_la_paz
from services.llm import (
    procesar_imagen_bytes, 
    detectar_objetos, 
    generar_prompt_cognitivo, 
    consultar_gemini
)

load_dotenv()

app = FastAPI(title="Agente de Utilidad Cognitiva - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

SOLO_DETECCION = os.getenv("SOLO_DETECCION", "false").lower() == "true"

SOLO_DETECCION = False

print(SOLO_DETECCION)

@app.post("/analizar-foto/")
async def analizar_foto(
    file: UploadFile = File(...),
    nombre: str = Form(...),
    ocupacion: str = Form(...),
    destino: Optional[str] = Form(default=""),
    latitud: Optional[float] = Form(default=None),
    longitud: Optional[float] = Form(default=None)
):
    tiempo_inicio = time.perf_counter()
    contents = await file.read()
    frame = procesar_imagen_bytes(contents)
    
    if frame is None:
        return {"error": "No se pudo decodificar la imagen. Envie un archivo valido"}
        
    print(f"Imagen recibida: Tamaño {frame.shape}")
    cv2.imwrite("debug_imagen.jpg", frame)  
    print(latitud, longitud)
    
    objetos_relevantes = detectar_objetos(frame)
    
    
    if SOLO_DETECCION:
        texto_final = (
            f"PRUEBA - backend en modo de pruebas"
            f"Objetos detectados en escena: {objetos_relevantes}."
        )
    else:
        
        clima_actual = obtener_pronostico_la_paz(latitud, longitud)
        prompt_estructurado = generar_prompt_cognitivo(
            nombre, ocupacion, destino, objetos_relevantes, clima_actual
        )
        texto_final = consultar_gemini(
            prompt_estructurado, nombre, objetos_relevantes, clima_actual
        )
    
    tiempo_final = time.perf_counter()
    tiempo_total_segundos = tiempo_final - tiempo_inicio
    
    # ver
    modo_actual = "SOLO DETECCION" if SOLO_DETECCION else "COMPLETO"
    print(f"\n========================================================")
    print(f"Modo de ejecución: {modo_actual}")
    print(f"Tiempo total de procesamiento: {tiempo_total_segundos:.4f} segundos")
    print(f"========================================================\n")
    return {
        "objetos": objetos_relevantes,
        "respuesta": texto_final
    }