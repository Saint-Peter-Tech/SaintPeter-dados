import pandas as pd
from datetime import datetime, timedelta
import random

pasta = "Escrever pasta aqui grupo"

#Pegando arquivos CSVs gerados da captura
mc = pd.read_csv(pasta +"captura.csv")
md = pd.read_csv(pasta + "CSV - Diego Henrique.csv")
m2 = pd.read_csv(pasta + "M2 - 20-04-2026 17_55.csv")
m6 = pd.read_csv(pasta + "M6 - 20-04-2026 08_58.csv")

#Juntando arquivos
df_base = pd.concat([mc, md, m2, m6])

#pegando media e desvio do df
media_cpu = df_base["cpu_percent"].mean()
media_ram = df_base["ram_percent"].mean()
desvio_cpu = df_base["cpu_percent"].std()
desvio_ram  = df_base["ram_percent"].std()

media_disco = df_base["disk_usage_percent"].mean()
desvio_disco = df_base["disk_usage_percent"].std()

media_env = df_base["bytes_sent_per_sec"].mean()
media_rec = df_base["bytes_recv_per_sec"].mean()
desvio_env = df_base["bytes_sent_per_sec"].std()
desvio_rec = df_base["bytes_recv_per_sec"].std()

#probabilidades de cada modulo estar ativo igual no raw
prob_bpm = 0.80
prob_pa  = 0.65
prob_spo2 = 0.80
prob_resp = 0.75
prob_temp = 0.70
prob_pic  = 0.20
prob_pvc = 0.30
prob_ecg = 0.85
prob_etco2 = 0.55

prob_modulos = [prob_bpm, prob_pa, prob_spo2, prob_resp, prob_temp, prob_pic, prob_pvc, prob_ecg, prob_etco2]

#Pesos por dia e hora

peso_dia  = [17.61, 16.87, 16.10, 16.21, 19.67,  8.22,  5.32]
peso_hora = [ 4.06,  2.71,  1.70,  1.64,  1.95,  2.00,  2.52, 12.07, 6.01,  4.24,  5.44,  6.12,  5.65,  5.16,  4.37,  3.16,
               3.12,  3.39,  3.80,  3.71,  3.56,  4.14,  4.66,  4.80]

#definindo limite de peso

# Peso max possível (pico de dia + hora) para normalizar os pesos entre 0 e 1
peso_maximo = (max(peso_dia) +max(peso_hora)) / 100

inicio        = datetime(2026, 1, 1, 0, 0, 0)
qtd_maquinas  = 10
ligada        = [False] * qtd_maquinas #Todos desligados
minutos_ligada = [0] *qtd_maquinas


#Sorteando atividade (p -> probabilidade)
def AtivoOuInativo(p, peso):
    if random.random() < p * peso:
        return "Ativo"
    else:
        return "Inativo"

#Tempo de duração do csv simulado
linhas = [] #Acumulador de linhas
tempo = inicio
fim   = inicio+timedelta(days=7)

variacao_monitor = []

for i in range(qtd_maquinas):
    variacao_monitor.append(random.randint(-5, 5))

while tempo < fim:

    hora = tempo.hour
    dia = tempo.weekday()
    peso = (peso_dia[dia] + peso_hora[hora]) / 100

    ligadas_agora = 0
    for i in range(qtd_maquinas):
        if ligada[i] == True:
            ligadas_agora = ligadas_agora + 1

     # Para variação de rede, quanto mais máquinas ligadas, menos rede disponível
    var_rede  = max(0.05, 1 - (ligadas_agora * 0.2))

    rede_base = max(0, media_env - (ligadas_agora * 1200) + random.uniform(-300, 300))


    for n in range(qtd_maquinas):
        
        # Calculando a probabilidade média de uso considerando os módulos e o peso da hora/dia
        soma = 0
        for p in prob_modulos:
            soma = soma + p * (peso / peso_maximo)
        prob_maq = soma / len(prob_modulos)

        if prob_maq > 0.97:
            prob_maq = 0.97

        #Se esta ligada, a chancee de continuar é maior
        if ligada[n] == True:
            prob_maq = prob_maq * 1.15
            if prob_maq > 0.97:
                prob_maq = 0.97

        aleatorio = random.random()

        if ligada[n] == False:
            if aleatorio < prob_maq:
                ligada[n] = True
                minutos_ligada[n] = 0

        if ligada[n] == True:
            if minutos_ligada[n] >= 60:
                if aleatorio > prob_maq:
                    ligada[n] = False
                    minutos_ligada[n] = 0

        if ligada[n] == True:

            minutos_ligada[n] = minutos_ligada[n] + 1

            if hora >= 20 or hora < 4:
                prob_pic_fatal = min(prob_pic * 1.8, 1)
                prob_pvc_fatal = min(prob_pvc * 1.6, 1)
            else:
                prob_pic_fatal = prob_pic
                prob_pvc_fatal = prob_pvc

            bpm = AtivoOuInativo(prob_bpm, peso)
            pa = AtivoOuInativo(prob_pa, peso)
            spo2 = AtivoOuInativo(prob_spo2,peso)
            resp = AtivoOuInativo(prob_resp,peso)
            temp = AtivoOuInativo(prob_temp,peso)
            pic = AtivoOuInativo(prob_pic_fatal,peso)
            pvc = AtivoOuInativo(prob_pvc_fatal,peso)
            ecg = AtivoOuInativo(prob_ecg,peso)
            etco2 = AtivoOuInativo(prob_etco2,peso)

            ativos = 0
            for modulo in [bpm, pa, spo2, resp, temp, pic, pvc, ecg, etco2]:
                if modulo == "Ativo":
                    ativos = ativos + 1


            cpu_f = random.gauss(media_cpu + ativos * 3.5 + variacao_monitor[n], desvio_cpu * 0.3)
            ram_f = random.gauss(media_ram + ativos * 2.0 + variacao_monitor[n] * 0.5, desvio_ram * 0.4)

            disco_f = random.gauss(media_disco + ativos * 0.3, desvio_disco * 0.5)
   
            env_f = rede_base + random.uniform(-50, 50)
            rec_f = rede_base + random.uniform(-50, 50)

            
            if cpu_f < 5:
                cpu_f = 5

            if cpu_f > 99:
                cpu_f = 99
            cpu = round(cpu_f, 1)

         
            if ram_f < 10:
                ram_f = 10
            if ram_f > 99:
                ram_f = 99
            ram = round(ram_f)

            if disco_f < 1:
                disco_f = 1

            if disco_f > 99:
                disco_f = 99
            disco = round(disco_f, 1)


            if env_f < 0:
                env_f = 0
            env = round(env_f, 3)

            if rec_f <0:
                rec_f = 0
            rec = round(rec_f, 3)

            linhas.append({
                "id_monitor": n + 1,
                "timestamp": tempo.strftime("%d-%m-%Y %H_%M_%S"),
                "cpu_percent": cpu,
                "ram_percent":ram,
                "disk_usage_percent": disco,
                "bytes_sent_per_sec": env,
                "bytes_recv_per_sec": rec,
                "bpm_status": bpm,
                "pa_status": pa,
                "spo2_status": spo2,
                "resp_status": resp,
                "temperatura_status": temp,
                "pic_status": pic,
                "pvc_status":pvc,
                "ecg_status": ecg,
                "etco2_status": etco2,
            })

    tempo += timedelta(minutes=1)

df_simulacao = pd.DataFrame(linhas)
df_simulacao.to_csv(pasta + "simulacao.csv", index=False)