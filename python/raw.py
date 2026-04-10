import psutil
import time
import pandas as pd
from datetime import datetime
import os
import boto3
import subprocess
import random
from random import randint

# Importando Bibliotecas Necessárias:
# psutil = Captura de Hardware e processos;
# time = Delay nas capturas para melhor análise e possibilidades;
# pandas as pd = Estrutura e manipulação de dados (DataFrame) e exportação para CSV;
# Datetime = Pegar a hora atual da Captura;
# OS = Funções para checar existência de pastas/arquivos;
# boto3 = Interagir com a AWS (s3);
# subprocess = Gerar processos fantasmas para simular modulos;
# random =  Utilizado da mesma forma que um rnorm para criar padrões.
# randomint = Gera um random entre intervalos


header = [
    "id_monitor",
    "timestamp",
    "cpu_percent",
    "ram_percent",
    "ram_used_gb",
    "disk_usage_percent",
    "bytes_sent_per_sec",
    "bytes_recv_per_sec",
    "bpm_status",
    "pa_status",
    "spo2_status",
    "resp_status",
    "temperatura_status",
    "pic_status",
    "pvc_status",
    "ecg_status",
    "etco2_status",
]

# Criando Header com:
# "id_monitor" = ID do monitor atual;
# "timestamp" = Data e hora da coleta dos dados;
# "cpu_percent" = Porcentagem de CPU;
# "ram_percent" = Porcentagem da memória RAM;
# "ram_used_gb" = Ram sendo utilizada já em gigabytes;
# "disk_usage_percent" = Porcentagem do disco sendo utilizado atualmente;
# "bytes_sent_per_sec" = Velocidade média de envio (upload) em bytes por segundo;
# "bytes_recv_per_sec" = Velocidade média de recebimento (download) em bytes por segundo.
# "bpm_status": indica a quantidade de batimentos cardíacos por minuto; 
# "pa_status": Pressão arterial (PA): mede a força com que o sangue é bombeado pelo coração pode ser PNI (Pressão Não Invasiva) ou PN (Pressão Invasiva); 
# "spo2_status": Saturação periférica de oxigênio (SpO₂): mensura a quantidade de oxigênio no sangue; 
# "resp_status": Frequência respiratória: analisa a quantidade de respirações por minuto; 
# "temperatura_status": Temperatura corporal: mede a temperatura do corpo; 
# "pic_status": Pressão intracraniana: mensura a pressão no crânio; 
# "pvc_status": Pressão venosa central: mede a pressão nas veias centrais; 
# "ecg_status": Eletrocardiograma (ECG): avalia a atividade elétrica do coração; 
# "etco2_status": Capnografia (EtCO₂): mede a quantidade de dióxido de carbono no ar exalado. 

modulos = {
    "bpm": ["bpm_module.py"],
    "pa": ["pa_module.py"],
    "spo2": ["spo2_module.py"],
    "resp": ["resp_module.py"],
    "temperatura": ["temp_module.py"],
    "pic": ["pic_module.py"],
    "pvc": ["pvc_module.py"],
    "ecg": ["ecg_module.py"],
    "etco2": ["etco2_module.py"],
}

# Definindo os Módulos que serão capturados:
# Cada módulo representa um "módulo físico" do monitor multiparamétrico
# Aqui estamos simulando esses módulos como processos rodando no sistema

pasta = './dados_brutos'

# Criando o caminho da pasta para salvar o CSV.

os.makedirs(pasta, exist_ok=True)


# Cria a pasta caso não exista (evita erro ao salvar arquivo).

arquivoCSV = f"{pasta}/dados_brutos.csv"
pasta_processos = "./processos_fantasmas"

# Cria a pasta para os Processos Fantasmas (modulos)
os.makedirs(pasta_processos, exist_ok=True)


# Define o caminho completo do arquivo CSV dentro da pasta criada.

if not os.path.exists(arquivoCSV):
    df_init = pd.DataFrame(columns=header)
    df_init.to_csv(arquivoCSV, index=False)

# Cria o arquivo CSV com apenas o cabeçalho caso ele ainda não exista.

def simular_processos_fantasmas():
    # Função responsável por criar processos simulados (módulos)
    # com base em probabilidades dependentes de horário e dia da semana

    agora = datetime.now()
    hora = agora.hour
    dia_semana = agora.weekday()

    probabilidades = {
        "ecg": 0.3,
        "spo2": 0.3,
        "bpm": 0.2,
        "resp": 0.2,
        "temperatura": 0.1,
        "pic": 0.05,
        "pvc": 0.05,
        "etco2": 0.1,
        "pa": 0.2
    }

    if dia_semana <= 4:

        if 6 <= hora < 8:
            probabilidades.update({
                "ecg": 0.9,
                "spo2": 0.9,
                "bpm": 0.8,
                "temperatura": 0.7,
                "etco2": 0.4
            })

        elif 8 <= hora < 12:
            probabilidades.update({
                "ecg": 0.95,
                "spo2": 0.95,
                "etco2": 0.8,
                "bpm": 0.85,
                "resp": 0.8
            })

        elif 12 <= hora < 17:
            probabilidades.update({
                "ecg": 0.95,
                "spo2": 0.95,
                "etco2": 0.85,
                "resp": 0.85,
                "temperatura": 0.7,
                "pic": 0.3,
                "pvc": 0.3
            })

        elif 17 <= hora < 20:
            probabilidades.update({
                "ecg": 0.9,
                "spo2": 0.9,
                "bpm": 0.8,
                "pic": 0.4,
                "pvc": 0.4
            })

    if 20 <= hora < 24:
        probabilidades.update({
            "ecg": 0.95,
            "spo2": 0.95,
            "etco2": 0.85,
            "pic": 0.5,
            "pvc": 0.5
        })

    elif 0 <= hora < 6:
        probabilidades.update({
            "ecg": 0.9,
            "spo2": 0.9,
            "etco2": 0.8,
            "pic": 0.6,
            "pvc": 0.6
        })

    if dia_semana >= 5 and 6 <= hora < 18:
        probabilidades.update({
            "ecg": 0.9,
            "spo2": 0.95,
            "bpm": 0.85,
            "temperatura": 0.7,
            "pic": 0.3,
            "pvc": 0.3
        })

    for modulo, arquivos in modulos.items():
        prob = probabilidades.get(modulo)

        if random.random() < prob:
            for script in arquivos:
                    subprocess.Popen(["python", script])

def verificar_modulos():
    # Função responsável por verificar se os módulos estão ativos no sistema

    status_modulos = {}

    # Captura todos os processos em execução no sistema
    processos = list(psutil.process_iter(['cmdline']))

    for nome_modulo, nomes_processos in modulos.items():

        ativo = False

        for proc in processos:
            try:
                if proc.info['cmdline']:
                    comando = " ".join(proc.info['cmdline'])

                    # Verifica se o nome do script está presente no processo
                    for nome in nomes_processos:
                        if nome in comando:
                            ativo = True
                            break

                if ativo:
                    break

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Define o status do módulo
        status_modulos[nome_modulo] = "Ativo" if ativo else "Inativo"

    return status_modulos

while True:

    # Cria os Processos Fantasmas
    simular_processos_fantasmas()

    # Pega o inicio do While
    inicio = time.time()

    # Gera um intervalo aleatorio para troca de módulos
    interval = randint(1800, 28800)

    while time.time() - inicio - interval:

        # Início do loop infinito para captura contínua dos dados do sistema:

        mem = psutil.disk_usage('/')
        # Captura informações de uso do disco (total, usado, livre e porcentagem);

        ram = psutil.virtual_memory()
        # Captura informações da memória RAM (total, disponível, usado, etc);

        cpu = psutil.cpu_percent(interval=1)
        # Captura o uso percentual da CPU (intervalo de 1 segundo para média mais precisa);

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Captura o timestamp atual da coleta formatado;

        id_monitor = 1
        # Simulando ser o Monitor X, SEMPRE MUDAR!!!;

        net = psutil.net_io_counters()
        # Captura os bytes totais enviados e recebidos até o momento;

        bytesSend1 = net.bytes_sent
        bytesRecv1 = net.bytes_recv
        # Armazena o primeiro ponto de medição da rede;

        time.sleep(5)
        # Aguarda 5 segundos para calcular a variação de tráfego de rede;

        net = psutil.net_io_counters()

        bytesSend2 = net.bytes_sent
        bytesRecv2 = net.bytes_recv
        # Segundo ponto de medição da rede;

        # Calcula a taxa média de envio e recebimento por segundo;
        bytes_sent_per_sec = (bytesSend2 - bytesSend1) / 5
        bytes_recv_per_sec = (bytesRecv2 - bytesRecv1) / 5

        # Captura o status dos módulos simulados
        modulos_status = verificar_modulos()

        # Cria uma lista com os dados coletados
        linha = [
            id_monitor,
            date,
            cpu,
            ram.percent,
            round(ram.used / (1024**3), 2),
            mem.percent,
            bytes_sent_per_sec,
            bytes_recv_per_sec,
        ]

        # Adiciona o status dos módulos na linha
        for modulo in modulos:
            linha.append(modulos_status[modulo])

        # Cria um DataFrame com uma única linha contendo os dados coletados.
        df = pd.DataFrame([linha], columns=header)

        # Salva os dados no CSV no modo append (sem sobrescrever o arquivo);
        df.to_csv(arquivoCSV, mode='a', header=False, index=False, encoding='utf-8')

        time.sleep(60)
        # Aguarda mais 60 segundos antes da próxima coleta (controle de frequência).