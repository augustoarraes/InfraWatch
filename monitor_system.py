# monitor_system.py
# Requer: streamlit, plotly, psutil, pandas
# Instalar: pip install streamlit plotly psutil pandas

import streamlit as st
import plotly.graph_objects as go
import psutil
import pandas as pd
import time



# ---- Função para criar gauges ----
def gauge_plot(value, titulo, max_val=100, unidade="%"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'thickness': 0.3, 'color': "royalblue"},
            'steps': [
                {'range': [0, max_val*0.6], 'color': "#e6f2ff"},
                {'range': [max_val*0.6, max_val*0.8], 'color': "#b3d9ff"},
                {'range': [max_val*0.8, max_val], 'color': "#66b3ff"},
            ],
        },
        number={'suffix': f" {unidade}"}
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
    return fig

# ---- Função para pegar top processos ----
def get_top_processes(metric="memory", top_n=5):
    processes = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            processes.append(info)
        except psutil.NoSuchProcess:
            continue

    df = pd.DataFrame(processes)

    if metric == "memory":
        df = df.sort_values("memory_percent", ascending=False).head(top_n)
        df["memory_percent"] = df["memory_percent"].round(2)
        return df[["pid", "name", "memory_percent"]].rename(columns={"memory_percent": "Mem %"})
    else:
        df = df.sort_values("cpu_percent", ascending=False).head(top_n)
        df["cpu_percent"] = df["cpu_percent"].round(2)
        return df[["pid", "name", "cpu_percent"]].rename(columns={"cpu_percent": "CPU %"})


def run():
    st.set_page_config(page_title="Monitor de CPU e RAM", layout="wide")

    st.title("🖥️ Monitor de Recursos do Sistema")

    REFRESH_INTERVAL = st.sidebar.number_input("Intervalo de atualização (segundos)", 1, 10, 2)

    # ---- Layout ----
    col1, col2 = st.columns(2)

    # ----- RAM -----
    with col1:
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        st.subheader("💾 Memória RAM")
        st.plotly_chart(gauge_plot(ram_percent, "Uso de RAM"), use_container_width=True)

        st.write("Top 5 processos que mais consomem RAM:")
        st.dataframe(get_top_processes("memory"))

    # ----- CPU -----
    with col2:
        cpu_percent = psutil.cpu_percent(interval=1)
        st.subheader("⚙️ CPU")
        st.plotly_chart(gauge_plot(cpu_percent, "Uso de CPU"), use_container_width=True)

        st.write("Top 5 processos que mais consomem CPU:")
        st.dataframe(get_top_processes("cpu"))


    # ----- Temperatura -----
    # ----- Temperatura -----
    st.subheader("🌡️ Temperatura do Processador")

    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            st.warning("⚠️ Não foi possível coletar temperatura neste sistema.")
        else:
            # Pega o primeiro sensor disponível (ex: 'coretemp')
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current:  # valor atual
                        temp_val = round(entry.current, 1)
                        st.plotly_chart(gauge_plot(temp_val, f"{name} ({entry.label or 'CPU'})", max_val=100, unidade="°C"), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao coletar temperatura: {e}")


    # ---- Atualização automática ----
    time.sleep(REFRESH_INTERVAL)
    st.rerun()
