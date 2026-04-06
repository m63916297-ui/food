# FoodDelivery Frontend

App Streamlit para el sistema de entrega de alimentos.

## Archivos

- `app.py` - Aplicación principal para clientes
- `admin.py` - Panel de administración
- `restaurant.py` - Portal para restaurantes

## Configuración

Configura la variable `API_BASE_URL` en cada archivo con la URL de tu API:

```python
API_BASE_URL = "https://your-api-url.onrender.com/api/v1"
```

## Ejecución Local

```bash
pip install streamlit requests
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube los archivos a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio de GitHub
4. Selecciona el archivo `app.py` como archivo principal
5. Deploy

## Variables de Entorno en Streamlit Cloud

En Streamlit Cloud, puedes configurar secrets en Settings > Secrets:

```toml
API_BASE_URL = "https://your-api-url.onrender.com/api/v1"
```
