import streamlit as st
import subprocess
import platform


def run():
    st.header("📡 Ferramenta de Ping")

    # Entrada do usuário
    host = st.text_input("Digite o endereço (IP ou domínio):", "8.8.8.8")
    count = st.number_input("Quantidade de pacotes:", min_value=1, max_value=20, value=4)

    if st.button("Iniciar Ping"):
        st.write(f"🔍 Rodando ping em **{host}** com {count} pacotes...")

        # Monta comando de acordo com o SO
        param = "-n" if platform.system().lower() == "windows" else "-c"
        cmd = ["ping", param, str(count), host]

        try:
            # Executa comando e captura saída
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            output_area = st.empty()
            logs = ""

            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                logs += line
                output_area.text(logs)

            process.stdout.close()
            process.wait()

            st.success("✅ Ping finalizado.")

        except Exception as e:
            st.error(f"Erro ao rodar ping: {e}")
