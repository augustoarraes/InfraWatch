# scanner_app.py
# Streamlit app para scan de portas simples (USO AUTORIZADO SOMENTE!)
# Executar:
#   pip install streamlit
#   streamlit run scanner_app.py

import streamlit as st
import socket
import concurrent.futures
from datetime import datetime
import pandas as pd
import time


# ---- Funções utilitárias ----
def parse_ports(ports_str):
    """
    Parseia uma string com portas e ranges como:
    "22,80,8000-8100,443" -> retorna lista ordenada de portas únicas [22,80,443,8000,...]
    Limites: 1..65535
    """
    ports = set()
    parts = [p.strip() for p in ports_str.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            try:
                start_s, end_s = part.split("-", 1)
                start = int(start_s); end = int(end_s)
                if start < 1: start = 1
                if end > 65535: end = 65535
                if start > end:
                    start, end = end, start
                # Adiciona o range (cuidado com ranges gigantes)
                ports.update(range(start, end + 1))
            except ValueError:
                # ignora segmento inválido
                continue
        else:
            if part.isdigit():
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
    return sorted(ports)

def scan_port(target, port, timeout=1.0):
    """Tenta conectar na porta TCP; retorna (port, True/False)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((target, port))
        s.close()
        return (port, True)
    except Exception:
        return (port, False)

def scan_target(target, ports, timeout=1.0, max_workers=100):
    """Escaneia todas as portas fornecidas para um único target, retornando lista de portas abertas."""
    open_ports = []
    # limitar threads para evitar estouro
    workers = min(max_workers, len(ports)) if len(ports) > 0 else 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(scan_port, target, p, timeout) for p in ports]
        for f in concurrent.futures.as_completed(futures):
            try:
                port, is_open = f.result()
                if is_open:
                    open_ports.append(port)
            except Exception:
                continue
    return sorted(open_ports)


def run():
    #st.set_page_config(page_title="Network Port Scanner", page_icon="🛡️", layout="centered")

    # ---- Cabeçalho e aviso ----
    st.title("🛡️ Network Port Scanner")

    st.markdown("## ⚠️ Aviso importante")
    st.warning(
        "**Somente execute varreduras em hosts/rede para os quais você tem AUTORIZAÇÃO EXPLÍCITA.**\n\n"
        "Scanning sem permissão pode ser considerado intrusão e é passível de sanções legais e administrativas."
    )

    with st.expander("Por que isso é importante / Boas práticas"):
        st.write(
            "- Tenha permissão escrita (escopo claro: IPs, horários, tipos de teste).\n"
            "- Prefira executar em ambiente de homologação quando possível.\n"
            "- Documente resultados e comunique o time responsável.\n"
            "- Evite scans agressivos em produção (pode causar indisponibilidade).\n"
            "- Em caso de dúvida, consulte o time de segurança da informação.\n"
        )

    # Confirmação obrigatória antes de liberar o scan
    agree = st.checkbox("Li e concordo com o aviso: tenho autorização para escanear os alvos acima (marque para habilitar)")

    st.markdown("---")

    # ---- Inputs ----
    st.subheader("Configuração do Scan")

    targets_input = st.text_area(
        "Digite os IPs ou hosts (um por linha)",
        "192.168.1.1\n192.168.1.10",
        help="Ex.: 192.168.1.1 ou host.exemplo.com"
    )

    # Default agora como range de todas as portas TCP
    default_ports = "1-65535"
    ports_input = st.text_input(
        "Portas a verificar (separadas por vírgula ou ranges, ex: 22,80,8000-8100)",
        default_ports
    )

    timeout = st.number_input("Timeout por conexão (segundos)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    max_workers_input = st.number_input(
        "Máx de threads simultâneas (concurrency)", min_value=1, max_value=500, value=100, step=1,
        help="Quantidade de threads usadas no ThreadPoolExecutor. Cuidado com valores muito altos."
    )

    st.write("Observação: este scanner realiza tentativas de conexão TCP (connect). Não executa exploits.")

    # ---- Pré-processamento das portas (para mostrar info antes de iniciar) ----
    try:
        ports = parse_ports(ports_input)
    except Exception:
        ports = []
        st.error("Erro ao parsear portas. Use formato como: 22,80,443,8000-8100")

    LARGE_SCAN_THRESHOLD = 1000  # limite para considerar "grande"

    # Se scan grande, pedir confirmação adicional antes de habilitar o botão
    confirm_large = True  # valor default para não bloquear if small scan
    if len(ports) > LARGE_SCAN_THRESHOLD:
        st.warning(f"⚠️ Você está prestes a escanear **{len(ports)}** portas por host. Isso pode demorar muito e gerar tráfego significativo.")
        confirm_large = st.checkbox("Confirmo que quero rodar o scan em todas essas portas (risco/tempo consciente)")

    # Desabilitar botão se usuário não concordou com aviso ou não confirmou scan grande
    start_disabled = not (agree and confirm_large)

    if start_disabled:
        st.info("Marque o checkbox de autorização e confirme scans grandes (se necessário) para habilitar o botão de scan.")

    # ---- Botão de ação ----
    if st.button("🔎 Iniciar Scan", disabled=start_disabled):
        # Preparar alvos e portas (revalidar)
        targets = [t.strip() for t in targets_input.splitlines() if t.strip()]
        if not targets:
            st.error("Nenhum alvo informado.")
            st.stop()
        if not ports:
            st.error("Nenhuma porta válida informada.")
            st.stop()

        # Rodar scan
        results = []
        start_time = datetime.now()
        with st.spinner("Escaneando... (cada host será verificado sequencialmente)"):
            for tgt in targets:
                try:
                    open_ports = scan_target(tgt, ports, timeout=timeout, max_workers=int(max_workers_input))
                except Exception as e:
                    open_ports = []
                    st.error(f"Erro ao escanear {tgt}: {e}")
                results.append({"Host": tgt, "Open Ports": ", ".join(map(str, open_ports)) if open_ports else "Nenhuma"})

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        st.success(f"✅ Scan finalizado em {elapsed:.2f}s — resultados abaixo.")

        # Exibir resultados (tabela)
        df = pd.DataFrame(results)
        st.subheader("Resultados")
        st.dataframe(df, use_container_width=True)

        # Salvar relatório local (append)
        try:
            filename = "scan_report.csv"
            try:
                prev = pd.read_csv(filename)
                out = pd.concat([prev, df], ignore_index=True)
            except FileNotFoundError:
                out = df
            out.to_csv(filename, index=False)
            st.info(f"Relatório salvo: `{filename}`")
        except Exception as e:
            st.warning(f"Não foi possível salvar relatório: {e}")

        # Botão para download do CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar CSV", csv, "scan_results.csv", "text/csv")

    st.markdown("---")
    st.caption("Nota: Este aplicativo realiza apenas tentativas de conexão TCP (connect). Não realiza exploração de vulnerabilidades. Use com responsabilidade e sempre obtenha autorização.")
