import streamlit as st
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
import requests
import re


def get_geo(ip):
    """Consulta API ip-api.com para pegar dados de geolocalização"""
    try:
        if (
            ip == "*"
            or ip.startswith("10.")
            or ip.startswith("192.168")
            or ip.startswith("172.16")
            or ip.startswith("127.")
        ):
            return None
        url = f"http://ip-api.com/json/{ip}"
        r = requests.get(url, timeout=3)
        data = r.json()
        if data["status"] == "success":
            return {
                "country": data.get("country"),
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp"),
            }
    except Exception:
        return None


def run():
    #st.set_page_config(page_title="Traceroute Visual", layout="wide")

    st.title("🌐 Traceroute com Visualização Geográfica")

    st.info("Digite um host/destino e clique em **Rodar Traceroute**. "
            "⚠️ Necessário que o container/host tenha `traceroute` instalado.")

    target = st.text_input("Destino (ex: google.com)", "8.8.8.8")

    if st.button("Rodar Traceroute"):
        try:
            result = subprocess.run(
                ["traceroute", "-n", target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode != 0:
                st.error(f"Erro ao executar traceroute:\n{result.stderr}")
            else:
                # Parseando saída
                lines = result.stdout.strip().split("\n")
                hops = []
                for line in lines[1:]:
                    parts = re.split(r"\s+", line.strip())
                    if len(parts) < 2:
                        continue
                    hop = int(parts[0])
                    ip = parts[1]
                    rtts = [
                        float(p.replace("ms", ""))
                        for p in parts[2:]
                        if "ms" in p and p.replace("ms", "").replace(".", "").isdigit()
                    ]
                    avg_rtt = sum(rtts) / len(rtts) if rtts else None
                    geo = get_geo(ip)
                    hops.append(
                        {
                            "hop": hop,
                            "ip": ip,
                            "avg_rtt": avg_rtt,
                            "country": geo["country"] if geo else None,
                            "city": geo["city"] if geo else None,
                            "isp": geo["isp"] if geo else None,
                            "lat": geo["lat"] if geo else None,
                            "lon": geo["lon"] if geo else None,
                        }
                    )

                df = pd.DataFrame(hops)

                st.subheader("📋 Tabela de Hops")
                st.dataframe(df)

                # --- Gráfico de linhas
                st.subheader("📈 Latência média por hop")
                fig, ax = plt.subplots()
                ax.plot(df["hop"], df["avg_rtt"], marker="o")
                ax.set_xlabel("Hop")
                ax.set_ylabel("RTT médio (ms)")
                ax.set_title("Evolução da latência ao longo do caminho")
                st.pyplot(fig)

                # --- Mapa de rede (networkx)
                st.subheader("🗺️ Mapa lógico de hops")
                G = nx.DiGraph()
                for i in range(len(df) - 1):
                    G.add_edge(
                        df.iloc[i]["ip"],
                        df.iloc[i + 1]["ip"],
                        weight=df.iloc[i + 1]["avg_rtt"] or 0,
                    )
                pos = nx.spring_layout(G, seed=42)
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                nx.draw(
                    G,
                    pos,
                    with_labels=True,
                    node_size=1200,
                    node_color="lightblue",
                    font_size=8,
                    ax=ax2,
                )
                st.pyplot(fig2)

                # --- Mapa geográfico (plotly)
                st.subheader("🌍 Mapa geográfico dos hops")
                geo_df = df.dropna(subset=["lat", "lon"])
                if not geo_df.empty:
                    fig_geo = go.Figure()

                    fig_geo.add_trace(
                        go.Scattergeo(
                            lon=geo_df["lon"],
                            lat=geo_df["lat"],
                            text=geo_df.apply(
                                lambda row: f"Hop {row['hop']} - {row['ip']}<br>"
                                f"{row['city']}, {row['country']}<br>"
                                f"ISP: {row['isp']}<br>"
                                f"RTT médio: {row['avg_rtt']} ms",
                                axis=1,
                            ),
                            mode="markers+lines",
                            marker=dict(size=8, color="blue"),
                            line=dict(width=2, color="red"),
                        )
                    )

                    fig_geo.update_layout(
                        geo=dict(
                            projection_type="natural earth",
                            showland=True,
                            landcolor="lightgray",
                            countrycolor="white",
                        ),
                        height=600,
                        margin={"r":0,"t":0,"l":0,"b":0},
                    )

                    st.plotly_chart(fig_geo, use_container_width=True)
                else:
                    st.warning("Nenhum hop retornou dados de geolocalização.")

                # --- Velocímetro (opcional)
                #if st.checkbox("📊 Mostrar velocímetros de atraso por hop"):
                st.subheader("⏱️ Velocímetros de atraso (RTT por hop)")
                for _, row in df.iterrows():
                    if row["avg_rtt"] is None:
                        continue
                    gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=row["avg_rtt"],
                            title={"text": f"Hop {row['hop']} ({row['ip']})"},
                            gauge={
                                "axis": {
                                    "range": [0, max(df["avg_rtt"].dropna()) * 1.2]
                                },
                                "bar": {"color": "blue"},
                                "steps": [
                                    {
                                        "range": [
                                            0,
                                            max(df["avg_rtt"].dropna()) * 0.5,
                                        ],
                                        "color": "lightgreen",
                                    },
                                    {
                                        "range": [
                                            max(df["avg_rtt"].dropna()) * 0.5,
                                            max(df["avg_rtt"].dropna()),
                                        ],
                                        "color": "orange",
                                    },
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": max(df["avg_rtt"].dropna()),
                                },
                            },
                        )
                    )
                    st.plotly_chart(gauge, use_container_width=True)

        except FileNotFoundError:
            st.error("O comando `traceroute` não está disponível no sistema/container.")
