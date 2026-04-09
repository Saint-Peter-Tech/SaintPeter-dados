import pandas as pd
import time
import os
import psutil

# Importando Bibliotecas Necessárias:
# psutil = Captura de Hardware e processos;
# time = Delay nas capturas para melhor análise e possibilidades;
# pandas as pd = Estrutura e manipulação de dados (DataFrame) e exportação para CSV;
# OS = Funções para checar existência de pastas/arquivos.

# Caminho do arquivo bruto:
arquivoCSV = './dados_brutos/dados_brutos.csv'

pasta_saida = './dados_tratados'

# Criando o caminho da pasta para salvar o CSV.

os.makedirs(pasta_saida, exist_ok=True)

# Cria a pasta caso não exista (evita erro ao salvar arquivo).

# Caminho do arquivo tratado:
arquivo_saida = f"{pasta_saida}/dados_tratados.csv"

# Estrutura do arquivo tratado
header = [
    "user",
    "timestamp_start",
    "timestamp_end",
    "cpu_peak",
    "ram_peak_percent",
    "disk_peak_percent",
    "cpu_min",
    "ram_min_percent",
    "disk_min_percent",
    "net_sent_peak_mbps",
    "net_sent_min_mbps",
    "net_recv_peak_mbps",
    "net_recv_min_mbps"
]

if not os.path.exists(arquivo_saida):
    pd.DataFrame(columns=header).to_csv(arquivo_saida, index=False)

# Cria o arquivo CSV com apenas o cabeçalho caso ele ainda não exista.

ramTotal = psutil.virtual_memory().total / (1024**3)

# Captura total de RAM da máquina.

while True:

    # Verifica se o arquivo bruto existe:
    if not os.path.exists(arquivoCSV):
        print("Erro: arquivo bruto não encontrado")
        time.sleep(5)
        continue

    # Lê o CSV bruto
    df = pd.read_csv(arquivoCSV)

    # Garante que existem pelo menos 6 registros
    if len(df) < 6:
        time.sleep(10)
        continue

    # Pega as últimas 6 linhas (último minuto)
    df_last = df.tail(6)

    # Conversões necessárias:
    df_last["timestamp"] = pd.to_datetime(df_last["timestamp"])
    df_last["ram_percent"] = (df_last["ram_used_gb"] / ramTotal) * 100
    df_last["net_send_mbps"] = df_last["bytes_sent_per_sec"] * 8 / 1_000_000
    df_last["net_recv_mbps"] = df_last["bytes_recv_per_sec"] * 8 / 1_000_000

    # Cálculo de métricas:
    cpu_peak = df_last["cpu_percent"].max()
    cpu_min = df_last["cpu_percent"].min()

    ram_peak = df_last["ram_percent"].max()
    ram_min = df_last["ram_percent"].min()

    disk_peak = df_last["disk_usage_percent"].max()
    disk_min = df_last["disk_usage_percent"].min()

    net_send_peak = df_last["net_send_mbps"].max()
    net_send_min = df_last["net_send_mbps"].min()

    net_recv_peak = df_last["net_recv_mbps"].max()
    net_recv_min = df_last["net_recv_mbps"].min()

    # Intervalo de tempo:
    timestamp_start = df_last["timestamp"].iloc[0] # Primeiro Registro do ultimo minuto;
    timestamp_end = df_last["timestamp"].iloc[-1] # Ultimo registro do ultimo minuto.

    user = df_last["user"].iloc[-1] # Pega o usuario do ultimo registro.

    # DataFrame final:
    df_saida = pd.DataFrame([[
        user,
        timestamp_start,
        timestamp_end,
        round(cpu_peak, 2),
        round(ram_peak, 2),
        round(disk_peak, 2),
        round(cpu_min, 2),
        round(ram_min, 2),
        round(disk_min, 2),
        round(net_send_peak, 2),
        round(net_send_min, 2),
        round(net_recv_peak, 2),
        round(net_recv_min, 2)
    ]], columns=header)

    # Salva no CSV tratado.
    df_saida.to_csv(arquivo_saida, mode='a', header=False, index=False)

    # Aguarda próxima execução.
    time.sleep(10)