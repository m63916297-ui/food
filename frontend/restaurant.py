import streamlit as st
import requests

API_BASE_URL = "https://your-api-url.onrender.com/api/v1"

st.set_page_config(
    page_title="FoodDelivery - Restaurante",
    page_icon="🍽️",
    layout="wide"
)

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None


def api_request(method: str, endpoint: str, data: dict = None) -> dict:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data if data else None)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": "Invalid method"}
        
        if response.status_code == 204:
            return {"success": True}
        
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def login_page():
    st.title("🍽️ FoodDelivery - Portal Restaurante")
    
    with st.form("restaurant_login"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            result = api_request("POST", "/auth/login", {"email": email, "password": password})
            
            if "access_token" in result:
                st.session_state.token = result["access_token"]
                me_result = api_request("GET", "/auth/me")
                
                if me_result.get("role") in ["restaurant", "admin"]:
                    st.session_state.user = me_result
                    st.success("Bienvenido al portal de restaurante")
                    st.rerun()
                else:
                    st.session_state.token = None
                    st.error("No tienes acceso de restaurante")
            else:
                st.error("Credenciales inválidas")


def restaurant_dashboard():
    st.title("🍽️ Portal Restaurante")
    
    st.sidebar.title("Panel Restaurante")
    
    if st.session_state.user:
        st.sidebar.success(f"Bienvenido: {st.session_state.user.get('full_name')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.restaurant_id = None
            st.rerun()
    
    menu = st.sidebar.radio("Menú", [
        "📋 Dashboard",
        "🍽️ Mi Restaurante",
        "📦 Categorías",
        "🍕 Menú",
        "🛒 Pedidos"
    ])
    
    if menu == "📋 Dashboard":
        show_dashboard()
    elif menu == "🍽️ Mi Restaurante":
        show_my_restaurant()
    elif menu == "📦 Categorías":
        show_categories()
    elif menu == "🍕 Menú":
        show_menu()
    elif menu == "🛒 Pedidos":
        show_orders()


def show_dashboard():
    st.header("📋 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pedidos del día", "15")
    with col2:
        st.metric("Pedidos del mes", "342")
    with col3:
        st.metric("Rating promedio", "4.5 ⭐")
    with col4:
        st.metric("Ingresos del mes", "$8,450")


def show_my_restaurant():
    st.header("🍽️ Mi Restaurante")
    st.info("Gestiona la información de tu restaurante")


def show_categories():
    st.header("📦 Gestión de Categorías")
    
    st.subheader("Agregar nueva categoría")
    
    with st.form("add_category"):
        name = st.text_input("Nombre de categoría")
        description = st.text_area("Descripción")
        sort_order = st.text_input("Orden", value="0")
        
        if st.form_submit_button("Agregar"):
            st.success("Categoría agregada")


def show_menu():
    st.header("🍕 Gestión del Menú")
    
    st.subheader("Agregar nuevo plato")
    
    with st.form("add_item"):
        category = st.selectbox("Categoría", ["Entradas", "Principales", "Bebidas", "Postres"])
        name = st.text_input("Nombre del plato")
        description = st.text_area("Descripción")
        price = st.number_input("Precio", min_value=0.0, step=0.01)
        prep_time = st.text_input("Tiempo de preparación (min)", value="15")
        is_available = st.checkbox("Disponible", value=True)
        is_vegan = st.checkbox("Vegano")
        is_gluten_free = st.checkbox("Sin gluten")
        
        if st.form_submit_button("Agregar Plato"):
            st.success("Plato agregado al menú")


def show_orders():
    st.header("🛒 Pedidos")
    
    status_options = {
        "pending": "🟡 Pendiente",
        "confirmed": "🔵 Confirmado",
        "preparing": "🟠 Preparando",
        "ready_for_pickup": "🟠 Listo para recoger",
        "in_transit": "🚀 En camino",
        "delivered": "✅ Entregado",
        "cancelled": "❌ Cancelado"
    }
    
    st.subheader("Pedidos Recibidos")
    
    for status in ["pending", "confirmed", "preparing"]:
        status_label = status_options.get(status)
        
        with st.expander(f"{status_label}"):
            st.info(f"1 pedido en estado {status_label}")


def main():
    if not st.session_state.token:
        login_page()
    else:
        restaurant_dashboard()


if __name__ == "__main__":
    main()
