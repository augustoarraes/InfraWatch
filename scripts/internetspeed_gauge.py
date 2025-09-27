# speedtest_gauge.py
import speedtest
import streamlit as st
import plotly.graph_objects as go


def run():
    #st.set_page_config(page_title="Teste de Velocidade", layout="centered")

    st.title("📶 Medidor de Velocidade de Internet")
    st.write("Teste sua velocidade de **Download** e **Upload** com velocímetro.")

    if st.button("Iniciar Teste"):
        st.info("⏳ Testando, aguarde...")

        stt = speedtest.Speedtest()
        stt.get_best_server()

        # Faz o teste
        download = stt.download() / 1_000_000  # Mbps
        upload = stt.upload() / 1_000_000      # Mbps
        ping = stt.results.ping

        st.success("✅ Teste concluído!")

        # Velocímetro de Download
        fig_download = go.Figure(go.Indicator(
            mode="gauge+number",
            value=download,
            title={'text': "📥 Download (Mbps)"},
            gauge={
                'axis': {'range': [0, max(100, download * 1.5)]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 20], 'color': "lightcoral"},
                    {'range': [20, 50], 'color': "gold"},
                    {'range': [50, 100], 'color': "lightgreen"},
                ],
            }
        ))

        # Velocímetro de Upload
        fig_upload = go.Figure(go.Indicator(
            mode="gauge+number",
            value=upload,
            title={'text': "📤 Upload (Mbps)"},
            gauge={
                'axis': {'range': [0, max(100, upload * 1.5)]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightcoral"},
                    {'range': [10, 30], 'color': "gold"},
                    {'range': [30, 100], 'color': "lightblue"},
                ],
            }
        ))

        st.plotly_chart(fig_download, use_container_width=True)
        st.plotly_chart(fig_upload, use_container_width=True)

        st.write(f"🏓 **Ping:** {ping:.2f} ms")
