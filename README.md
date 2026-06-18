# Agente de Utilidad / Cognitivo

Este repositorio contiene el sistema completo del **Agente de Utilidad**, dividido en un Backend (FastAPI + Docker) y un Frontend móvil (React Native + Expo).

---

## Prerrequisitos

Antes de iniciar, asegúrate de tener instalado lo siguiente:
- [Docker y Docker Compose](https://www.docker.com/) (Para el Backend)
- [Node.js (LTS)](https://nodejs.org/) y npm (Para el Frontend)
- La aplicación **Expo Go** instalada en tu dispositivo móvil (disponible en Google Play Store y Apple App Store).

---

## 1. Clonar el Proyecto

Clona el repositorio desde tu terminal y accede a la carpeta raíz del proyecto:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

---

## 2. Levantar el Backend (Docker)

1. Ve al directorio del backend:
   ```bash
   cd backend-agente
   ```
2. Crea tu archivo de configuración ambiental a partir de la plantilla:
   ```bash
   cp .env.example .env
   ```
3. Configura tu `GEMINI_API_KEY` y demás variables necesarias en el archivo `.env`:
   ```env
   GEMINI_API_KEY=Tu_Gemini_API_Key_Aqui
   SOLO_DETECCION=True
   ```
4. Construye y levanta el entorno contenedorizado:
   ```bash
   docker compose up --build
   ```
   *El backend estará listo y escuchando en `http://localhost:8000`.*

---

## 3. Levantar el Frontend (React Native + Expo)

1. Desde la raíz del proyecto, navega a la carpeta del cliente móvil:
   ```bash
   cd emergentes_FrontEnd
   ```
2. Crea un archivo `.env` para enlazar la URL de la API del backend:
   ```bash
   nano .env
   ```
   Añade tu IP local (importante para que tu celular se conecte al backend de tu PC) con el prefijo obligatorio de Expo:
   ```env
   EXPO_PUBLIC_API_URL=http://<IP_LOCAL_DE_TU_PC>:8000/analizar-foto/
   ```
3. Instala los paquetes y dependencias del proyecto:
   ```bash
   npm install
   ```
4. Inicia el servidor de desarrollo de Expo limpiando la caché para asegurar la lectura del `.env`:
   ```bash
   npm start -- -c
   ```

---

## 4. Vincular con el Dispositivo Móvil

1. Asegúrate de que tu computadora y tu celular estén conectados a la **misma red Wi-Fi**.
2. Abre la aplicación **Expo Go** en tu dispositivo móvil.
3. Escanea el código QR que aparece en la terminal de tu computadora tras ejecutar el comando de arranque del frontend.
