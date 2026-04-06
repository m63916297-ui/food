import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

API_BASE_URL = "https://your-api-url.onrender.com/api/v1"

st.set_page_config(
    page_title="FoodDelivery - Pedidos de Comida",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def api_request(method: str, endpoint: str, data: dict = None, requires_auth: bool = True) -> dict:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if requires_auth and st.session_state.token:
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
    st.title("🍔 FoodDelivery")
    st.subheader("Iniciar Sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Correo electrónico", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                if email and password:
                    result = api_request("POST", "/auth/login", {"email": email, "password": password}, requires_auth=False)
                    
                    if "access_token" in result:
                        st.session_state.token = result["access_token"]
                        me_result = api_request("GET", "/auth/me")
                        st.session_state.user = me_result
                        st.success("¡Sesión iniciada!")
                        st.rerun()
                    else:
                        st.error(result.get("detail", "Error al iniciar sesión"))
                else:
                    st.warning("Por favor complete todos los campos")
        
        st.markdown("---")
        st.markdown("¿No tienes cuenta? Regístrate")
        
        with st.form("register_form"):
            st.subheader("Registro")
            reg_email = st.text_input("Correo electrónico", key="reg_email")
            reg_name = st.text_input("Nombre completo", key="reg_name")
            reg_phone = st.text_input("Teléfono", key="reg_phone")
            reg_password = st.text_input("Contraseña", type="password", key="reg_password")
            reg_submit = st.form_submit_button("Registrarse", use_container_width=True)
            
            if reg_submit:
                if all([reg_email, reg_name, reg_phone, reg_password]):
                    result = api_request(
                        "POST", 
                        "/auth/register", 
                        {
                            "email": reg_email,
                            "full_name": reg_name,
                            "phone": reg_phone,
                            "password": reg_password,
                            "role": "client"
                        },
                        requires_auth=False
                    )
                    
                    if "id" in result:
                        st.success("¡Registro exitoso! Ahora puedes iniciar sesión")
                    else:
                        st.error(result.get("detail", "Error al registrarse"))
                else:
                    st.warning("Por favor complete todos los campos")


def home_page():
    st.title("🍔 FoodDelivery")
    
    st.sidebar.title("Menú")
    menu_options = ["🏠 Inicio", "🍽️ Restaurantes", "🛒 Mis Pedidos", "📍 Mis Direcciones", "👤 Mi Perfil"]
    
    if st.session_state.user:
        st.sidebar.success(f"Conectado: {st.session_state.user.get('full_name', 'User')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    page = st.sidebar.radio("Navegación", menu_options)
    
    if page == "🏠 Inicio":
        show_home()
    elif page == "🍽️ Restaurantes":
        show_restaurants()
    elif page == "🛒 Mis Pedidos":
        show_orders()
    elif page == "📍 Mis Direcciones":
        show_addresses()
    elif page == "👤 Mi Perfil":
        show_profile()


def show_home():
    st.header("Bienvenido a FoodDelivery")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 ¿Qué quieres comer hoy?
        
        Encuentra los mejores restaurantes cerca de ti y disfruta de comida deliciosa 
        delivered directly to your door.
        
        **Características:**
        - 🍽️ Variedad de restaurantes y cocinas
        - 🚀 Entregas rápidas
        - ⭐ Reseñas de otros usuarios
        - 💳 Pagos seguros
        """)
    
    with col2:
        st.markdown("### 📊 Estadísticas")
        st.metric("Pedidos realizados", "25")
        st.metric("Gastado total", "$450.00")
    
    st.markdown("---")
    
    st.subheader("🔥 Restaurantes Populares")
    restaurants = api_request("GET", "/restaurants", {"page": 1, "per_page": 6}, requires_auth=False)
    
    if "items" in restaurants:
        cols = st.columns(3)
        for i, rest in enumerate(restaurants["items"][:6]):
            with cols[i % 3]:
                st.markdown(f"""
                **{rest.get('name', 'Restaurant')}**
                
                - 🍳 {rest.get('cuisine_type', 'Food')}
                - ⭐ {rest.get('rating_avg', 0):.1f}
                - 🚚 Envío: ${rest.get('delivery_fee', 0):.2f}
                """)
                if st.button(f"Ver menú", key=f"rest_{rest.get('id')}"):
                    st.session_state.selected_restaurant = rest.get('id')
                    st.rerun()


def show_restaurants():
    st.header("🍽️ Restaurantes")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("Buscar restaurantes o tipos de cocina...")
    with col2:
        cuisine_filter = st.selectbox("Filtrar por cocina", ["Todos", "Mexicana", "Italiana", "China", "Americana", "Japonesa"])
    
    params = {"page": 1, "per_page": 20}
    if cuisine_filter != "Todos":
        params["cuisine_type"] = cuisine_filter
    
    restaurants = api_request("GET", "/restaurants", params, requires_auth=False)
    
    if "items" in restaurants:
        st.write(f"**{restaurants.get('total', 0)}** restaurantes encontrados")
        
        for rest in restaurants["items"]:
            with st.expander(f"🍽️ {rest.get('name')} - ⭐ {rest.get('rating_avg', 0):.1f}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    **{rest.get('name')}**
                    
                    - 🍳 Cocina: {rest.get('cuisine_type')}
                    - ⭐ Rating: {rest.get('rating_avg', 0):.1f}/5
                    - 🚚 Envío: ${rest.get('delivery_fee', 0):.2f}
                    - 📍 {rest.get('address', 'N/A')}
                    """)
                
                with col2:
                    if st.button("Ver Menú y Ordenar", key=f"order_{rest.get('id')}"):
                        st.session_state.selected_restaurant = rest.get('id')
                        st.rerun()


def show_orders():
    st.header("🛒 Mis Pedidos")
    
    orders = api_request("GET", "/orders", {"page": 1, "per_page": 50})
    
    if "items" in orders:
        if not orders["items"]:
            st.info("No tienes pedidos aún. ¡Empieza a ordenar!")
            return
        
        for order in orders["items"]:
            status_color = {
                "pending": "🟡",
                "confirmed": "🔵",
                "preparing": "🟠",
                "ready_for_pickup": "🟠",
                "in_transit": "🚀",
                "delivered": "✅",
                "cancelled": "❌",
                "refunded": "💰"
            }
            
            emoji = status_color.get(order.get('status', 'pending'), "⚪")
            
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Pedido #{order.get('order_number', 'N/A')}**")
                    st.markdown(f"📍 {order.get('delivery_address', 'N/A')}")
                    st.markdown(f"🏪 {order.get('restaurant_name', 'Restaurant')}")
                
                with col2:
                    st.markdown(f"**Total:** ${float(order.get('total_amount', 0)):.2f}")
                    st.markdown(f"**Fecha:** {order.get('created_at', '')[:10]}")
                
                with col3:
                    st.markdown(f"**Estado:** {emoji} {order.get('status', 'N/A')}")
                    
                    if st.button("Ver Detalles", key=f"view_{order.get('id')}"):
                        st.session_state.selected_order = order.get('id')
                        st.rerun()
                
                st.markdown("---")
    else:
        st.error("Error al cargar pedidos")


def show_addresses():
    st.header("📍 Mis Direcciones")
    
    addresses = api_request("GET", "/users/me/addresses")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Direcciones guardadas")
        
        if isinstance(addresses, list):
            for addr in addresses:
                with st.container():
                    col_a, col_b = st.columns([4, 1])
                    
                    with col_a:
                        label = addr.get('label', 'Dirección')
                        default = "⭐ Principal" if addr.get('is_default') else ""
                        st.markdown(f"**{label}** {default}")
                        st.markdown(f"{addr.get('street', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip_code', '')}")
                    
                    with col_b:
                        if st.button("Eliminar", key=f"del_addr_{addr.get('id')}"):
                            api_request("DELETE", f"/users/me/addresses/{addr.get('id')}")
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No tienes direcciones guardadas")
    
    with col2:
        st.subheader("Agregar nueva dirección")
        
        with st.form("add_address"):
            label = st.text_input("Etiqueta (casa, trabajo, etc.)")
            street = st.text_input("Calle y número")
            city = st.text_input("Ciudad")
            state = st.text_input("Estado")
            zip_code = st.text_input("Código postal")
            is_default = st.checkbox("Dirección principal")
            
            if st.form_submit_button("Guardar Dirección"):
                result = api_request(
                    "POST",
                    "/users/me/addresses",
                    {
                        "label": label,
                        "street": street,
                        "city": city,
                        "state": state,
                        "zip_code": zip_code,
                        "is_default": is_default
                    }
                )
                
                if "id" in result:
                    st.success("Dirección guardada")
                    st.rerun()
                else:
                    st.error("Error al guardar dirección")


def show_profile():
    st.header("👤 Mi Perfil")
    
    if st.session_state.user:
        user = st.session_state.user
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Avatar")
            st.markdown("👤")
        
        with col2:
            st.markdown(f"**Nombre:** {user.get('full_name', 'N/A')}")
            st.markdown(f"**Email:** {user.get('email', 'N/A')}")
            st.markdown(f"**Teléfono:** {user.get('phone', 'N/A')}")
            st.markdown(f"**Rol:** {user.get('role', 'N/A')}")
            st.markdown(f"**Cuenta verificada:** {'✅' if user.get('is_verified') else '❌'}")
            st.markdown(f"**Cuenta activa:** {'✅' if user.get('is_active') else '❌'}")


def main():
    if not st.session_state.token:
        login_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
