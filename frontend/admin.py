import streamlit as st
import requests
from datetime import datetime

API_BASE_URL = "https://your-api-url.onrender.com/api/v1"

st.set_page_config(
    page_title="FoodDelivery - Admin",
    page_icon="🍔",
    layout="wide"
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
    st.title("🍔 FoodDelivery - Admin")
    
    with st.form("admin_login"):
        email = st.text_input("Email Admin")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión Admin")
        
        if submit:
            result = api_request("POST", "/auth/login", {"email": email, "password": password}, requires_auth=False)
            
            if "access_token" in result:
                st.session_state.token = result["access_token"]
                me_result = api_request("GET", "/auth/me")
                
                if me_result.get("role") == "admin":
                    st.session_state.user = me_result
                    st.success("Acceso de administrador concedido")
                    st.rerun()
                else:
                    st.session_state.token = None
                    st.error("No tienes permisos de administrador")
            else:
                st.error("Credenciales inválidas")


def admin_dashboard():
    st.title("🍔 FoodDelivery - Panel de Administración")
    
    st.sidebar.title("Panel Admin")
    
    if st.session_state.user:
        st.sidebar.success(f"Admin: {st.session_state.user.get('full_name')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    menu = st.sidebar.radio("Menú", [
        "📊 Dashboard",
        "👥 Usuarios",
        "🍽️ Restaurantes",
        "🛒 Pedidos"
    ])
    
    if menu == "📊 Dashboard":
        show_dashboard()
    elif menu == "👥 Usuarios":
        show_users()
    elif menu == "🍽️ Restaurantes":
        show_admin_restaurants()
    elif menu == "🛒 Pedidos":
        show_admin_orders()


def show_dashboard():
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Usuarios Totales", "1,234")
    with col2:
        st.metric("Restaurantes", "89")
    with col3:
        st.metric("Pedidos del Mes", "3,456")
    with col4:
        st.metric("Ingresos", "$45,678")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pedidos Recientes")
        st.info("Gráfico de pedidos últimos 7 días")
    
    with col2:
        st.subheader("Top Restaurantes")
        st.info("Ranking por ventas")


def show_users():
    st.header("👥 Gestión de Usuarios")
    
    users = api_request("GET", "/users", {"page": 1, "per_page": 100})
    
    if "items" in users:
        st.write(f"**Total:** {users.get('total', 0)} usuarios")
        
        for user in users["items"]:
            with st.expander(f"{user.get('full_name')} - {user.get('email')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {user.get('id')}")
                    st.write(f"**Nombre:** {user.get('full_name')}")
                    st.write(f"**Email:** {user.get('email')}")
                    st.write(f"**Teléfono:** {user.get('phone')}")
                
                with col2:
                    st.write(f"**Rol:** {user.get('role')}")
                    st.write(f"**Verificado:** {'✅' if user.get('is_verified') else '❌'}")
                    st.write(f"**Activo:** {'✅' if user.get('is_active') else '❌'}")
                    st.write(f"**Fecha registro:** {user.get('created_at', '')[:10]}")


def show_admin_restaurants():
    st.header("🍽️ Gestión de Restaurantes")
    
    restaurants = api_request("GET", "/restaurants", {"page": 1, "per_page": 100}, requires_auth=False)
    
    if "items" in restaurants:
        for rest in restaurants["items"]:
            status = "🟢 Activo" if rest.get('is_active') else "🔴 Inactivo"
            
            with st.expander(f"{rest.get('name')} - {status}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cocina:** {rest.get('cuisine_type')}")
                    st.write(f"**Dirección:** {rest.get('address')}")
                    st.write(f"**Rating:** ⭐ {rest.get('rating_avg', 0):.1f}")
                
                with col2:
                    st.write(f"**Envío:** ${rest.get('delivery_fee', 0):.2f}")
                    st.write(f"**Pedidos min:** ${rest.get('min_order_amount', 0):.2f}")
                    st.write(f"**Radio entrega:** {rest.get('delivery_radius_km', 0)} km")


def show_admin_orders():
    st.header("🛒 Gestión de Pedidos")
    
    orders = api_request("GET", "/orders", {"page": 1, "per_page": 100})
    
    if "items" in orders:
        st.write(f"**Total:** {orders.get('total', 0)} pedidos")
        
        status_options = {
            "pending": "🟡 Pendiente",
            "confirmed": "🔵 Confirmado",
            "preparing": "🟠 Preparando",
            "ready_for_pickup": "🟠 Listo",
            "in_transit": "🚀 En camino",
            "delivered": "✅ Entregado",
            "cancelled": "❌ Cancelado",
            "refunded": "💰 Reembolsado"
        }
        
        for order in orders["items"]:
            status = status_options.get(order.get('status'), order.get('status'))
            
            with st.expander(f"#{order.get('order_number')} - {status}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Cliente:** {order.get('user_id', 'N/A')[:8]}...")
                    st.write(f"**Restaurant:** {order.get('restaurant_name', 'N/A')}")
                
                with col2:
                    st.write(f"**Total:** ${float(order.get('total_amount', 0)):.2f}")
                    st.write(f"**Fecha:** {order.get('created_at', '')[:10]}")
                
                with col3:
                    nuevo_status = st.selectbox(
                        "Cambiar estado",
                        options=list(status_options.keys()),
                        index=list(status_options.keys()).index(order.get('status')),
                        key=f"status_{order.get('id')}"
                    )
                    
                    if st.button("Actualizar", key=f"upd_{order.get('id')}"):
                        result = api_request(
                            "PATCH",
                            f"/orders/{order.get('id')}/status",
                            {"status": nuevo_status}
                        )
                        if "id" in result:
                            st.success("Estado actualizado")
                            st.rerun()


def main():
    if not st.session_state.token or not st.session_state.user:
        login_page()
    else:
        admin_dashboard()


if __name__ == "__main__":
    main()
