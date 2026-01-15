Instalación y configuración
1️. Clonar el repositorio
git clone <URL-del-repositorio>
cd FaunaDataInc

2.  Crear un entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows

3. Instalar dependencias
pip install -r requirements.txt

Ejecutar el servidor

Usa Uvicorn para levantar la API:

uvicorn app.main:app --reload


La API estará disponible en:

http://localhost:8000

Documentación automática:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc