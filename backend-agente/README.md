#  Agente de Utilidad - Backend

Backend desarrollado con FastAPI e integrado con Gemini para proporcionar funcionalidades de inteligencia artificial.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.10 o superior
- Git
- Una API Key de Google AI Studio (Gemini)

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/ChubiBF/agenteDeUtilidad.git
cd backend-agente
```

### 2. Crear y activar el entorno virtual

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto y agrega:

```env
GEMINI_API_KEY=tu_api_key_aqui
```

> Puedes obtener tu API Key desde Google AI Studio.

---

## Ejecutar el servidor

Inicia la aplicación con:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará disponible en:

```text
http://localhost:8000
```

---

## Estructura Básica

```text
backend-agente/
│
├── main.py
├── requirements.txt
├── .env
├── venv/
└── ...
```

