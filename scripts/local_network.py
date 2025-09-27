import streamlit as st
import socket
import ipaddress
import subprocess
import platform
import psutil

def get_local_ip():
    """Descobre o IP local usado para sair para a Internet"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # não envia pacotes, só descobre o IP da interface usada
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def ping_host(ip):
    """Executa ping em um IP e retorna True se responder"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, "1", ip]
    if platform.system().lower() != "windows":
        cmd.insert(3, "-W")
        cmd.insert(4, "1")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        st.error("⚠️ O comando 'ping' não está disponível no container/host.")
        return False

def run():
    st.header("🔍 Descoberta de Dispositivos na Rede")

    # --- IP local ---
    local_ip = get_local_ip()
    st.info(f"💻 Seu IP local: **{local_ip}**")

    # --- Detectar sub-rede ---
    network = None
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == local_ip:
                mask = addr.netmask
                try:
                    network = ipaddress.IPv4Network(f"{local_ip}/{mask}", strict=False)
                except Exception as e:
                    st.error(f"Erro ao calcular sub-rede: {e}")
                break

    if not network:
        st.error("❌ Não foi possível identificar a sub-rede.")
        return

    st.write(f"🌐 Sub-rede detectada: **{network}**")

    # --- Descoberta de dispositivos ---
    if st.button("Iniciar varredura"):
        all_hosts = list(network.hosts())

        # Proteção: limitar varredura a /24 (até 254 hosts) para não travar
        if len(all_hosts) > 256:
            st.warning(
                f"A sub-rede {network} tem {len(all_hosts)} endereços. "
                f"A varredura foi limitada ao primeiro /24."
            )
            base = str(all_hosts[0]).rsplit(".", 1)[0]
            all_hosts = [ipaddress.IPv4Address(f"{base}.{i}") for i in range(1, 255)]

        st.write(f"⏳ Varredura em andamento ({len(all_hosts)} hosts)...")
        progress = st.progress(0)
        results = []

        for i, ip in enumerate(all_hosts):
            ip_str = str(ip)
            if ping_host(ip_str):
                results.append({"IP": ip_str})
                st.write(f"✅ Ativo: {ip_str}")
            progress.progress((i + 1) / len(all_hosts))

        if results:
            st.success(f"🎯 Dispositivos ativos encontrados: {len(results)}")
            st.table(results)
        else:
            st.warning("Nenhum dispositivo ativo encontrado na rede.")
