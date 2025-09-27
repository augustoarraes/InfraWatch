import streamlit as st
import subprocess
import os

from scripts import monitor_system, internetspeed_gauge, endpointmeter, scan_tcp, traceroute, system_info, ping, local_network

# === CONFIGURAÇÃO DO LAYOUT ===
st.set_page_config(page_title="Painel de Ferramentas", page_icon="🛠️", layout="wide")

# === MENU LATERAL ===
st.sidebar.title("📌 Ferramentas")

scripts = {
    "📄 Informações do Sistema": system_info,
    "🔥 Monitorar Sistema": monitor_system,
    "🌐 Testar Velocidade Internet": internetspeed_gauge,
    "🌐 Ping": ping,
    "🌐 Rede local": local_network,
    "📊 Endpoint REST Meter": endpointmeter,
    "📝 Scan": scan_tcp,
    "🌐 Traceroute": traceroute
}

escolha = st.sidebar.radio("Selecione uma opção:", list(scripts.keys()))

# === ÁREA PRINCIPAL ===
st.title("🛠️ Painel de Ferramentas")

if escolha == "🏠 Início":
    st.markdown("### 👋 Bem-vindo ao painel")
    st.info("Use o menu lateral para escolher uma ferramenta e executá-la.")

else:
    modulo = scripts[escolha]
    if hasattr(modulo, "run"):
        modulo.run()  # roda dentro do Streamlit
    else:
        st.error(f"O módulo {modulo} não tem função run() definida.")
