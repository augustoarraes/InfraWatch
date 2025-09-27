import streamlit as st
import requests
import time
import concurrent.futures
import statistics
import matplotlib.pyplot as plt


def run():
    #st.set_page_config(page_title="Teste de Carga REST", layout="centered")

    st.title("🔗 Teste de Carga em Endpoint REST")

    url = st.text_input("Digite a URL do endpoint:", "https://jsonplaceholder.typicode.com/posts")
    num_requests = st.number_input("Número total de requisições:", min_value=1, value=50, step=1)
    concurrency = st.number_input("Nível de concorrência:", min_value=1, value=5, step=1)
    method = st.selectbox("Método HTTP", ["GET", "POST"])
    payload = st.text_area("Payload (JSON para POST):", "{}" if method == "POST" else "", height=100)

    if st.button("🚀 Iniciar Teste"):
        st.write("Executando...")

        times = []

        def make_request(_):
            try:
                start = time.time()
                if method == "GET":
                    resp = requests.get(url)
                else:
                    resp = requests.post(url, json=eval(payload))
                elapsed = time.time() - start
                return resp.status_code, elapsed
            except Exception as e:
                return "ERR", None

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            results = list(executor.map(make_request, range(num_requests)))

        # Filtrar resultados válidos
        status_codes = [r[0] for r in results]
        response_times = [r[1] for r in results if r[1] is not None]

        if response_times:
            avg_time = statistics.mean(response_times)
            p95 = statistics.quantiles(response_times, n=100)[94]  # 95º percentil
            throughput = num_requests / sum(response_times)

            st.subheader("📊 Resultados")
            st.write(f"✅ Requisições bem sucedidas: {status_codes.count(200)}")
            st.write(f"❌ Erros: {status_codes.count('ERR')}")
            st.write(f"⏱️ Tempo médio de resposta: {avg_time:.3f} s")
            st.write(f"⚡ Percentil 95: {p95:.3f} s")
            st.write(f"📡 Throughput: {throughput:.2f} req/s")

            # Gráfico
            fig, ax = plt.subplots()
            ax.plot(response_times, marker="o")
            ax.set_title("Tempo de resposta por requisição")
            ax.set_xlabel("Requisição #")
            ax.set_ylabel("Segundos")
            st.pyplot(fig)
        else:
            st.error("Nenhuma resposta válida obtida.")
