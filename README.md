# FoodDelivery API 🍔

Sistema completo de entrega de alimentos (food delivery) construido con FastAPI, PostgreSQL y Streamlit.

## Arquitectura

```
food/
├── app/                    # Backend FastAPI
│   ├── api/v1/            # Endpoints de la API
│   ├── core/              # Configuración, seguridad, base de datos
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/            # Esquemas Pydantic (DTOs)
│   ├── repositories/      # Capa de acceso a datos
│   ├── services/          # Lógica de negocio
│   ├── middleware/        # Logging, CORS, etc.
│   └── utils/             # Utilidades
├── frontend/              # Aplicaciones Streamlit
├── docker/                # Dockerfiles
├── alembic/               # Migraciones de BD
└── tests/                 # Tests
```

## Stack Tecnológico

- **Backend:** FastAPI 0.110+, Python 3.11+
- **Base de Datos:** PostgreSQL 15+ con SQLAlchemy 2.0 async
- **Cache:** Redis 7+
- **Autenticación:** JWT con python-jose
- **Frontend:** Streamlit Cloud
- **Containerización:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

## Instalación Local

### 1. Clonar y configurar

```bash
cd food
cp .env.example .env
# Editar .env con tus configuración
```

### 2. Crear ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -e ".[dev]"
```

### 4. Ejecutar con Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up
```

### 5. O ejecutar localmente

```bash
# Terminal 1: PostgreSQL y Redis
docker-compose -f docker/docker-compose.yml up db redis

# Terminal 2: API
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Endpoints Principales

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Inicio de sesión
- `POST /api/v1/auth/refresh` - Renovar token
- `GET /api/v1/auth/me` - Usuario actual

### Restaurantes
- `GET /api/v1/restaurants/` - Listar restaurantes
- `POST /api/v1/restaurants/` - Crear restaurante
- `GET /api/v1/restaurants/{id}/menu` - Ver menú

### Pedidos
- `POST /api/v1/orders/` - Crear pedido
- `GET /api/v1/orders/` - Listar pedidos
- `PATCH /api/v1/orders/{id}/status` - Actualizar estado

## Roles de Usuario

- `admin` - Acceso completo
- `restaurant` - Gestionar restaurante propio
- `rider` - Realizar entregas
- `client` - Realizar pedidos

## Testing

```bash
pytest tests/ -v
```

## Despliegue

### Render (Backend)

1. Crear nuevo Web Service en Render
2. Conectar repositorio GitHub
3. Configurar:
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Añadir variables de entorno en Render Dashboard

### Streamlit Cloud (Frontend)

1. Subir archivos `frontend/` a GitHub
2. Crear nueva app en [share.streamlit.io](https://share.streamlit.io)
3. Conectar repositorio
4. Configurar: `app.py` como archivo principal
5. Añadir secrets: `API_BASE_URL`

## Documentación

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Licencia

MIT
