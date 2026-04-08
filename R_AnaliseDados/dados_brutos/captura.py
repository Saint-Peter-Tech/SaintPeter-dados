import psutil
import time
import getpass
import pandas as pd
from datetime import datetime
import os

# Importando Bibliotecas Necessárias:
# psutil = Captura de Hardware e processos;
# time = Delay nas capturas para melhor análise e possibilidades;
# getpass = Biblioteca mais funcional para conseguir o usuario atual;
# pandas as pd = Estrutura e manipulação de dados (DataFrame) e exportação para CSV;
# Datetime = Pegar a hora atual da Captura;
# OS = Funções para checar existência de pastas/arquivos.

header = [
    "user",
    "timestamp",
    "cpu_percent",
    "ram_percent",
    "ram_used_gb",
    "disk_usage_percent",
    "bytes_sent_per_sec",
    "bytes_recv_per_sec",
]

# Criando Header com:
# "user" = Usuario atual;
# "timestamp" = Data e hora da coleta dos dados;
# "cpu_percent" = Porcentagem de CPU;
# "ram_used_gb" = Ram sendo utilizada já em gigabytes;
# "disk_usage_percent" = Porcentagem do disco sendo utilizado atualmente;
# "bytes_sent_per_sec" = Velocidade média de envio (upload) em bytes por segundo;
# "bytes_recv_per_sec" = Velocidade média de recebimento (download) em bytes por segundo.

pasta_script = os.path.dirname(os.path.abspath(__file__))
arquivoCSV = os.path.join(pasta_script, "dados_brutos.csv")

# Define o caminho completo do arquivo CSV dentro da pasta criada.

if not os.path.exists(arquivoCSV):
     df_init = pd.DataFrame(columns=header)
     df_init.to_csv(arquivoCSV, index=False)

# Cria o arquivo CSV com apenas o cabeçalho caso ele ainda não exista.

while True:

    # Início do loop infinito para captura contínua dos dados do sistema:

    mem = psutil.disk_usage('/')  
    # Captura informações de uso do disco (total, usado, livre e porcentagem);

    ram = psutil.virtual_memory()
    # Captura informações da memória RAM (total, disponível, usado, etc);

    cpu = psutil.cpu_percent(interval=1)
    # Captura o uso percentual da CPU (intervalo de 1 segundo para média mais precisa);

    date = datetime.now()
    # Captura o timestamp atual da coleta;

    usuario = getpass.getuser()
    # Obtém o usuário atual do sistema operacional;

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

    # Cria um DataFrame com uma única linha contendo os dados coletados.
    df = pd.DataFrame([[
        usuario,
        date,
        cpu,
        ram.percent,
        round(ram.used/(1024**3), 2),
        mem.percent,
        bytes_sent_per_sec,
        bytes_recv_per_sec,
    ]], columns=header)

    # Salva os dados no CSV no modo append (sem sobrescrever o arquivo);
    df.to_csv(arquivoCSV, mode='a', header=False, index=False, encoding='utf-8')
    print("teste")

    time.sleep(5)
    # Aguarda mais 5 segundos antes da próxima coleta (controle de frequência).