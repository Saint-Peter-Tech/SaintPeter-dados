import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import json

# Importando Bibliotecas Necessárias:
# pandas as pd = Estrutura e manipulação de dados (DataFrame) e exportação para CSV;
# mysql.connector = Conexão com Banco de dados para validações;
# dotenv = Criação de variaveis de ambiente
# OS = Funções para checar existência de pastas/arquivos;
# json = Criar arquivos .json para melhor manipulação no Front;

# Criando caminho da pasta RAW e do Arquivo Raw, onde estarão os dados brutos (LOCAL!!! MUDAR PARA S3)
pastaRaw = './dados_brutos'
rawArquivo = f"{pastaRaw}/raw.csv"

# Criando caminho da pasta Trusted e do Arquivo Trusted, onde ficarão os dados tratados (LOCAL!!! MUDAR PARA S3)
pastaTrusted = './trusted'
trustedArquivo = f"{pastaTrusted}/trusted.csv"

# Criando caminho da pasta Client e do Arquivo Client, onde ficarão os dados para serem consumidos no Front (LOCAL!!! MUDAR PARA S3)
pastaClient = './client'
clientArquivo = f"{pastaClient}/client.json"

# Criando as pastas caso elas não existam
os.makedirs(pastaTrusted, exist_ok=True)
os.makedirs(pastaClient, exist_ok=True)

# Arquivo de controle para saber o momento de criar o Client
controleArquivo = "./controle.txt"

# Carregando as variaveis de ambiente
load_dotenv()

# Colunas de status dos Monitores
status_cols = [
    "bpm_status", "pa_status", "spo2_status", "resp_status",
    "temperatura_status", "pic_status", "pvc_status",
    "ecg_status", "etco2_status"
]

# Conectando com MYSQL:
def conectar():
    try:
        conn = mysql.connector.connect(
                host=os.getenv("host"),
                user=os.getenv("user"),
                password=os.getenv("password"),
                database=os.getenv("database"))
        
        if conn.is_connected():
            print("Conectado ao SQL com Sucesso")
            return conn
        
    except mysql.connector.Error as e:
        print(f"Erro: {e}")

# Função para buscar os limites dos monitores
def buscar_limites(cursor, id_monitor):

    # Select para pegar os limites de acordo com o componente
    query = """
        SELECT c.nome_componente, cm.limite
        FROM componente_monitor cm
        JOIN componentes c 
            ON cm.fk_componente = c.id_componente
        WHERE cm.fk_monitor = %s
    """

    # Cursor para executar a Query
    cursor.execute(query, (id_monitor,))
    # Resultado da Query salvo
    resultado = cursor.fetchall()

    # Transformando a query em Dicionario
    limites = {}
    for nome, limite in resultado:
        limites[nome.lower()] = float(limite)

    return limites

# Função para ler o arquivo de controle
def ler_controle():
    if not os.path.exists(controleArquivo):
        return 0
    with open(controleArquivo, "r") as f:
        return int(f.read())

# Função para salvar o arquivo de controle
def salvar_controle(valor):
    with open(controleArquivo, "w") as f:
        f.write(str(valor))

# Função para preparar raw para tratamento
def preparar_raw(df):
    # Copiando dataframe para manipulação
    df = df.copy()

    # Convertendo datas
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%d-%m-%Y %H_%M_%S",
        errors="coerce"
    )

    # Limpando possiveis dados invalidos e ordenando por monitor e data em ordem cronologica
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values(["id_monitor", "timestamp"])

    return df

# Função para tratar os dados (trusted)
def trusted(df):
    # Utiliza o preparar_raw para deixar os dados prontos para tratamento
    df = preparar_raw(df)

    # Pega os ultimos 10 registros (10 minutos)
    df_last = df.tail(10)

    # Checa se tem dados
    if df_last.empty:
        print("Sem dados para trusted")
        return

    # Pega o pico de cada coisa dos ultimos 10minutos
    horario = df_last["timestamp"].max()
    idMonitor = df_last["id_monitor"].iloc[-1]

    maxCPU = df_last["cpu_percent"].max()
    maxRAM = df_last["ram_percent"].max()
    maxDISK = df_last["disk_usage_percent"].max()

    bandaLarga = round(
        (df_last["bytes_sent_per_sec"].max() +
         df_last["bytes_recv_per_sec"].max()) * 8 / 1_000_000,
        2
    )

    # Pega o ultimo registro do DF
    ultimo = df_last.iloc[-1]

    # Monta dicionario de Registros
    registro = {
        "idMonitor": idMonitor,
        "horario": horario,
        "maxCPU": maxCPU,
        "maxRAM": maxRAM,
        "maxDISK": maxDISK,
        "bandaLarga": bandaLarga
    }

    # Adiciona os Status dinamicamente com for
    for col in status_cols:
        registro[col] = ultimo[col]

    # Cria dataframe
    df_trusted = pd.DataFrame([registro])

    # Checa se o dataframe não existe para criar headers e logo em seguida coloca os dados
    if not os.path.exists(trustedArquivo):
        df_trusted.to_csv(trustedArquivo, index=False)
    else:
        df_trusted.to_csv(trustedArquivo, mode='a', header=False, index=False)

    return df_trusted

# Função para deixar os dados para o Cliente
def client(df, cursor):
    # Pega os ultimos 3 registros do trusted
    df_client = df.tail(3)

    # Garante que o Trusted tem dados suficientes
    if df_client.empty:
        print("Sem dados")
        return

    resultado = []

    # Percorrer o df_trusted
    for _, row in df_client.iterrows():
        # Pega o id do monitor da linha e transforma em int
        id_monitor = int(row["idMonitor"])

        # Busca os limites do banco com base no id do monitor e o cursor informado anteriormente
        limites = buscar_limites(cursor, id_monitor)

        # Cria as colunas que irão para o cliente
        cpu = row["maxCPU"]
        ram = row["maxRAM"]
        disk = row["maxDISK"]
        rede = row["bandaLarga"]

        # Função para definir o status do monitor
        def status(valor, limite):
            if valor <= limite:
                return "OK"
            elif valor <= limite * 1.2:
                return "Alerta"
            return "Crítico"
        
        # Procura os limites de cada componente no banco
        limite_cpu = limites.get("cpu")
        limite_ram = limites.get("ram")
        limite_disk = limites.get("disco")
        limite_rede = limites.get("rede")

        statuscpu = status(cpu, limite_cpu)
        statusram = status(ram, limite_ram)
        statusdisco = status(disk, limite_disk)
        statusrede = status(rede, limite_rede)

        # Gerá quantidade de modulos ativos e se o monitor está ativo
        qtd_modulos_ativos = sum(row[col] == "Ativo" for col in status_cols)
        monitor_ativo = qtd_modulos_ativos > 0

        # Cria status geral com base em como está cada componente
        if "Crítico" in [statuscpu, statusram, statusdisco]:
            statusgeral = "Crítico"
        elif "Alerta" in [statuscpu, statusram, statusdisco]:
            statusgeral = "Alerta"
        else:
            statusgeral = "OK"

        # Cria a base do json de resultado
        resultado.append({
            "idmonitor": id_monitor,
            "cpuporcentagem": cpu,
            "ramporcentagem": ram,
            "discoporcentagem": disk,
            "redeMBS": rede,
            "statusgeral": statusgeral,
            "statusram": statusram,
            "statuscpu": statuscpu,
            "statusdisco": statusdisco,
            "statusrede": statusrede,
            "monitorativo": monitor_ativo,
            "qtdmodulosativos": qtd_modulos_ativos
        })

        # Cria de fato o json
    with open(clientArquivo, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

    return client

def main():
    # Checando se o arquivo RAW existe, (TROCAR PARA S3!!!)
    if not os.path.exists(rawArquivo):
        print("Arquivo RAW não encontrado")
        return
    
    # Lendo arquivo raw
    df_raw = pd.read_csv(rawArquivo)

    # Alertando caso não tenha encontrado registro no arquivo
    if df_raw.empty:
        print("RAW vazio")
        return

    # Escrevendo no trusted
    trusted(df_raw)

    # Lendo o trusted
    df_trusted = pd.read_csv(trustedArquivo)

    # Validação de 3 novas linhas no trusted para 1 client novo
    total_atual = len(df_trusted)
    total_anterior = ler_controle()

    # Criando cliente caso passe na condição
    if total_atual - total_anterior >= 3:
        print("Executando client...")

        # Pegando cursor do MYSQl para poder executar queries
        conn = conectar()
        cursor = conn.cursor()

        # Chamando a função client
        client(df_trusted, cursor)
        # Salvando controle atual para executar apenas daqui 3 proximas execuções
        salvar_controle(total_atual)
    else:
        print("Aguardando mais dados...")

# Executando main()
if __name__ == "__main__":
    main()