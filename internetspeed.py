# speedtest_app.py
import speedtest
import streamlit as st
import time
import pandas as pd
import matplotlib.pyplot as plt

st.title("📶 Medidor de Velocidade de Internet")

st.write("Este app mede a velocidade de download e upload da sua internet.")

# Botão para iniciar teste
if st.button("Iniciar Teste de Velocidade"):
    st.info("⏳ Testando, aguarde...")

    stt = speedtest.Speedtest()
    stt.get_best_server()

    results = []

    # Fazendo 5 medições consecutivas
    for i in range(5):
        download = stt.download() / 1_000_000  # Convertendo para Mbps
        upload = stt.upload() / 1_000_000      # Convertendo para Mbps
        ping = stt.results.ping

        results.append({"Medição": i + 1, "Download (Mbps)": download, "Upload (Mbps)": upload, "Ping (ms)": ping})

        st.write(f"📥 Download: {download:.2f} Mbps | 📤 Upload: {upload:.2f} Mbps | 🏓 Ping: {ping:.2f} ms")
        time.sleep(2)  # pequena pausa entre testes

    # Transformar em DataFrame
    df = pd.DataFrame(results)

    # Gráfico com Matplotlib
    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(x="Medição", y=["Download (Mbps)", "Upload (Mbps)"], marker="o", ax=ax)
    plt.title("Velocidade da Internet")
    plt.ylabel("Mbps")
    plt.grid(True)

    # Mostrar gráfico no Streamlit
    st.pyplot(fig)

    # Mostrar tabela final
    st.dataframe(df)
