import psutil
import time
import pandas as pd
from datetime import datetime
import os

# Importando Bibliotecas Necessárias:
# psutil = Captura de Hardware e processos;
# time = Delay nas capturas para melhor análise e possibilidades;
# pandas as pd = Estrutura e manipulação de dados (DataFrame) e exportação para CSV;
# Datetime = Pegar a hora atual da Captura;
# OS = Funções para checar existência de pastas/arquivos.

header = [
    "id_monitor",
    "timestamp",
    "cpu_percent",
    "ram_percent",
    "ram_used_gb",
    "disk_usage_percent",
    "bytes_sent_per_sec",
    "bytes_recv_per_sec",
    "ecg_status",
    "spo2_status",
    "pressao_status",
    "temperatura_status"
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
# "ecg_status" = Status do módulo ECG (Ativo/Inativo).
# "spo2_status" = Status do módulo de oxigenação.
# "pressao_status" = Status do módulo de pressão.
# "temperatura_status" = Status do módulo de temperatura.

modulos = {
    "ecg": ["ecg_module.py"],
    "spo2": ["spo2_module.py"],
    "pressao": ["pressure_module.py"],
    "temperatura": ["temp_module.py"]
}

# Definindo os Módulos que serão capturados:
# Cada módulo representa um "módulo físico" do monitor multiparamétrico
# Aqui estamos simulando esses módulos como processos rodando no sistema

pasta = './dados_brutos'

# Criando o caminho da pasta para salvar o CSV.

os.makedirs(pasta, exist_ok=True)

# Cria a pasta caso não exista (evita erro ao salvar arquivo).

arquivoCSV = f"{pasta}/dados_brutos.csv"

# Define o caminho completo do arquivo CSV dentro da pasta criada.

if not os.path.exists(arquivoCSV):
    df_init = pd.DataFrame(columns=header)
    df_init.to_csv(arquivoCSV, index=False)

# Cria o arquivo CSV com apenas o cabeçalho caso ele ainda não exista.

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

                    print(nome)

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

    time.sleep(5)
    # Aguarda mais 5 segundos antes da próxima coleta (controle de frequência).