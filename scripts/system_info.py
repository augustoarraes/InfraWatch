import streamlit as st
import platform
import socket
import psutil
import requests


def run():
    st.header("🖥️ Informações do Sistema e Rede")

    # --- 1. Informações do Sistema ---
    st.subheader("📋 Sistema Operacional")
    uname = platform.uname()
    st.write({
        "Sistema": uname.system,
        "Nó (Hostname)": uname.node,
        "Release": uname.release,
        "Versão": uname.version,
        "Máquina": uname.machine,
        "Processador": uname.processor,
        "Arquitetura": platform.architecture(),
        "CPU Cores (físicos)": psutil.cpu_count(logical=False),
        "CPU Cores (lógicos)": psutil.cpu_count(logical=True),
        "Memória Total (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
    })

    # --- 2. IP Público ---
    st.subheader("🌍 IP Público da Conexão")
    try:
        ip_public = requests.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
        st.success(f"Seu IP Público é: **{ip_public}**")
    except Exception as e:
        st.error(f"Não foi possível obter IP público: {e}")

    # --- 3. Interfaces de Rede ---
    st.subheader("🌐 Interfaces de Rede")
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    for interface, addrs in net_if_addrs.items():
        st.markdown(f"**Interface: {interface}**")
        info = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info.append(("IPv4", addr.address))
                info.append(("Máscara", addr.netmask))
            elif addr.family == socket.AF_INET6:
                info.append(("IPv6", addr.address))
            elif addr.family == psutil.AF_LINK:
                info.append(("MAC", addr.address))
        stats = net_if_stats.get(interface)
        if stats:
            info.append(("Status", "Ativa" if stats.isup else "Inativa"))
            info.append(("Velocidade (Mbps)", stats.speed))
        st.table(info)

