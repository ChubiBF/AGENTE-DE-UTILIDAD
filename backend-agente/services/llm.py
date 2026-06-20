import os
import cv2
import numpy as np
from ultralytics import YOLO
import google.generativeai as genai
import google.api_core.exceptions

model_base = YOLO('yolov8n.pt') 
model_custom = YOLO('best.pt') 

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
model_ia = genai.GenerativeModel('gemini-2.5-flash')

INTERES_BASE = ['laptop', 'mouse', 'cup', 'backpack', 'umbrella', 'bottle', 'sports ball', 'tennis racket', 'book']
INTERES_CUSTOM = ['pen', 'notebook', 'charger', 'canillera', 'sport_shoes', 'keys', 'wallet', 'jacket', 'cream', 'cap', 'Shorts', 'hat']

UMBRALES_CUSTOM = {
    'notebook': 0.60,
    'keys': 0.35,
    'sport_shoes': 0.78,
    'wallet': 0.40,
    'cap': 0.40,
    'cream': 0.69,
    'charger': 0.25,
    'Shorts': 0.30,
    'hat': 0.40,
    'canillera': 0.35,
    'jacket': 0.35,
    'pen': 0.25,
    'book': 0.30
}

def procesar_imagen_bytes(contents: bytes) -> np.ndarray:
    """Convierte los bytes recibidos de la API en un frame compatible con OpenCV."""
    nparr = np.frombuffer(contents, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def detectar_objetos(frame: np.ndarray) -> list:
    """Ejecuta las detecciones con el modelo base y personalizado aplicando los umbrales."""
    
    results_base = model_base(frame, conf=0.25)
    objetos_base = [model_base.names[int(box.cls[0])] for r in results_base for box in r.boxes]
    detectados_base = [o for o in objetos_base if o in INTERES_BASE]
    print("Objetos modelo base:", detectados_base)
    
    
    results_custom = model_custom(frame) 
    detectados_custom = []
    
    for r in results_custom:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            nom_clase = model_custom.names[cls_id]
            conf_detectada = float(box.conf[0])
            
            umbral_minimo = UMBRALES_CUSTOM.get(nom_clase, 0.25)
            
            if nom_clase in INTERES_CUSTOM and conf_detectada >= umbral_minimo:
                detectados_custom.append(nom_clase)
                print(f" -> ACEPTADO: {nom_clase} con confianza {conf_detectada:.2f} (Mínimo: {umbral_minimo})")
            elif nom_clase in INTERES_CUSTOM:
                print(f" -> RECHAZADO: {nom_clase} con confianza {conf_detectada:.2f} (No alcanzó {umbral_minimo})")

    print("Objetos filtrados modelo customizado:", detectados_custom)
    
    
    return list(set(detectados_base + detectados_custom))

def generar_prompt_cognitivo(nombre: str, ocupacion: str, destino: str, objetos: list, clima: str) -> str:
    return f"""
    [ROL Y CONTEXTO DEL SISTEMA]
    Actúas como un Agente de Autonomía y Utilidad Real especializado en la preparación de salidas urbanas operativas. Tu objetivo fundamental es garantizar una tasa de error cero antes de que el usuario abandone su hogar, mitigando su carga cognitiva, previniendo incidentes de seguridad y optimizando su continuidad laboral y académica.

    [INFORMACIÓN INYECTADA EN TIEMPO REAL]
    - Nombre del Usuario: {nombre}
    - Perfil Profesional/Académico: {ocupacion}
    - Destino Declarado: {destino if destino else "No especificado por el usuario"}
    - Inventario Físico Detectado por YOLOv8: {objetos}
    - Estado Meteorológico Actual en su ciudad: {clima}

    [MARCO OPERATIVO: CAPACIDADES Y REGLAS DE LAS SKILLS]
    Debes estructurar tu evaluación lógica basándote estrictamente en las siguientes tres dimensiones operativas:

    1. SKILL_01 (Equipamiento y Continuidad):
       - Seguridad Crítica: Verifica obligatoriamente la presencia de 'keys' (llaves) y 'wallet' (billetera). Si falta alguno, activa un estado de advertencia prioritario.
       - Dependencia Física de Hardware: Si se detecta 'laptop' o 'cell phone', inspecciona la mesa en busca de 'charger' (cargador). Si el cargador está ausente, infiere un riesgo inminente de interrupción de productividad académica/laboral.
       - Herramientas de Estudio: Evalúa si para un '{ocupacion}' es pertinente contar con 'notebook' (cuaderno) y 'pen' (bolígrafo), u otros objetos importantes si es que aplica, por ejemplo laptop para estudiantes de carreras como informatica.

    2. SKILL_02 (Entorno y Climatología Adaptativa para su ciudad):
       - Analiza el estado meteorológico enviado ('{clima}').
       - Si el reporte indica lluvias, tormentas o cielos nublados, exige la presencia de 'umbrella' (paraguas) o 'jacket' (chamarra/abrigo).
       - Si el reporte indica días soleados, despejados o alta radiación, valida la pertinencia de protectores como 'cream' (bloqueador solar) o 'cap' (gorra/bicornio). Si no están presentes y el sol es intenso, emite una sugerencia preventiva de salud.

    3. SKILL_03 (Bienestar y Contexto Deportivo/Especializado):
       - Evalúa si se detectan elementos de indumentaria como 'sport_shoes' o 'canillera'. Si están presentes, asume automáticamente que el usuario asistirá a una actividad deportiva, ajustando las recomendaciones de hidratación o equipamiento de cambio.
       - De la misma forma detecta la dependencia de objetos fisicos o posibles objetos que podria necesitar para su salida.
       - Si el inventario está completo y óptimo para su perfil de '{ocupacion}', concluye validando la salida de forma exitosa.
       - Siempre recomienda llevar una botella de agua.

    [OBJETOS QUE SON DETECTABLES POR EL MODELO DE VISION]
    - {INTERES_BASE, INTERES_CUSTOM}
    
    [RESTRICCIONES TÉCNICAS REQUISITO PARA EXCELENCIA]
    - NUNCA alucines ni menciones objetos físicos que NO estén explitamente listados en el vector de 'Inventario Físico Detectado'. Si un objeto no fue detectado, asume que está AUSENTE.
    - Dirígete al usuario siempre en tercera persona de cortesía o de manera directa y empática llamándolo por su nombre ('{nombre}').
    - No te limites a solo los objetos detectables por el modelo, puedes darle otras recomendaciones como otros objetos que puede llevar si es que aplica.
    - Mantén un tono profesional, ejecutivo, predictivo y sumamente conciso. Evita introducciones genéricas largas. Ve directo a la acción.

    [PROTOCOLO DE RESPUESTA]
    Genera un informe breve estructurado de la siguiente forma:
    - Saludo personalizado breve analizando el destino.
    - Estado del Inventario (Alertas críticas si faltan llaves, billetera o protección climática).
    - Conclusión Operativa (Si se autoriza la salida o se mantiene en retención preventiva).
    - Traduce los objetos, no respondas con los objetos detectados o recomendados en ingles ya que asi estan etiquetadas la mayoria de los objetos.
    POR ULTIMO Recuerda responder siempre con un tono de 'Asistente de salidas' personalizado, dirigiéndote a {nombre}, priorizando la claridad y la BREVEDAD que es la mas importante.
    """

def consultar_gemini(prompt: str, nombre: str, objetos: list, clima: str) -> str:
    try:
        print(f"Invocando API de Gemini... Clima: {clima}")
        respuesta = model_ia.generate_content(prompt)
        return respuesta.text
    except google.api_core.exceptions.ResourceExhausted:
        print("Límite de cuota de Gemini alcanzado.")
        return f"¡Hola {nombre}! Veo que estás listo para salir hacia tu destino. El Agente de IA se encuentra procesando múltiples solicitudes en este momento (Límite de cuota API excedido), sin embargo, tu inventario físico local se ha detectado exitosamente: {', '.join(objetos) if objetos else 'Ninguno'}."
    except Exception as e:
        print(f"Error inesperado en el LLM: {str(e)}")
        return f"Hola {nombre}, se generó un inconveniente al procesar tus consejos de salida. Error: {str(e)}"