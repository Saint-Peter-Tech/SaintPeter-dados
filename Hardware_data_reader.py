import csv
from datetime import datetime
import os
import psutil
import time
from itertools import islice

arquivoCSV = 'Hardware_data.csv'
formatoData = "%Y-%m-%d %H:%M:%S"
linhas = 0
ramTotal = round(8367104000/1024**3,2)
picoRam10min = []
picoMem10min = []
picoCPU10min = []
PicoSendSpd = []
PicoRecvSpd = []
PicoTemp = []
dtTimes = []
count = 0
user = ''

def Leitura():

    with open (arquivoCSV,'r',newline="") as arq:

        leitor = csv.reader(arq)

        linhas = sum(1 for row in leitor)

    with open (arquivoCSV,"r") as arq:

        leitor = csv.reader(arq)

        return next(islice(leitor,linhas-1,linhas))

def timeFrame10s():

    count = 0

    if os.path.exists(arquivoCSV):

        while True:

            resultado = Leitura()

            user = resultado[0]
            Ram = float(resultado[3])
            Mem = float(resultado[4])
            Cpu = float(resultado[2])
            Date =  datetime.strptime(resultado[1],formatoData)
            vSend = round(((float(resultado[7])-float(resultado[6]))/5)* 8/1000000,2)
            vRecv = round(((float(resultado[9])-float(resultado[8]))/5)* 8/1000000,2)
            temp = resultado[5]

            print("Ram: ",round((Ram/ramTotal)*100,2),"%","\n","Memória: ",Mem,"%","\n","CPU: ",Cpu,"%","\n","Data: ",Date,"\n")

            if(len(PicoSendSpd) == 60):

                PicoSendSpd.pop(0)

            PicoSendSpd.append(vSend)

            if(len(PicoRecvSpd) == 60):

                PicoRecvSpd.pop(0)

            PicoRecvSpd.append(vRecv)

            if temp != "SysUnsurp":

                if(len(PicoTemp) == 60):

                    PicoTemp.pop(0)

                PicoTemp.append(temp)

            PicoRecvSpd.append(vRecv)

            if len(dtTimes) == 60:

                dtTimes.pop(0)
            
            dtTimes.append(Date)

            count = count + 1            

            if len(picoRam10min) == 60:

                picoRam10min.pop(0)
            
            picoRam10min.append(Ram)

            if len(picoCPU10min) == 60:

                 picoCPU10min.pop(0)
            
            picoCPU10min.append(Cpu)

            if len(picoMem10min) == 60:

                picoMem10min.pop(0)
            
            picoMem10min.append(Mem)

            print("Pico do uso de Ram no últimos 10 minutos: ",round((max(picoRam10min)/ramTotal)*100,2),"%\n",
                         "Pico do uso de CPU nos últimos 10 minutos: ",max(picoCPU10min),"%\n",
                         "Pico do uso de memória nos últimos 10 minutos: ",max(picoMem10min),"%\n")

            if count == 60:

                data = ["usuario","dtIni","dfFin","PicoCPU","PicoRam","PicoMem","MediaCPU","MediaRam","MediaMem","PicoVelEnvio","MedVelEnvio","PicoVelReceb","MediaVelReceb","PicoTemp","MediaTemp"]

                CSV = 'Treated_Hardware_data.csv'

                if os.path.exists(CSV) == False:

                    with open(CSV, mode = "w", newline='') as arq:

                            escritor = csv.writer(arq)
                            escritor.writerow(data)


                Pmem = f"{(max(picoMem10min))}%"
                Pram = f"{round((max(picoRam10min)/ramTotal)*100,2)}%"
                Pcpu = f"{max(picoCPU10min)}%"
                Mmem = f"{sum(picoMem10min)/len(picoMem10min)}%"
                Mram = f"{round(((sum(picoRam10min)/(ramTotal*len(picoRam10min)))/len(picoRam10min))*100,2)}%"
                Mcpu = f"{round(sum(picoCPU10min)/len(picoCPU10min),2)}%"
                PVSend = f"{round(max(PicoSendSpd),2)}Mbps"
                PVRecv = f"{round(max(PicoRecvSpd),2)}Mbps"
                MVSend = f"{round(sum(PicoSendSpd)/len(PicoSendSpd),2)}Mbps"
                MVRecv = f"{round(sum(PicoRecvSpd)/len(PicoRecvSpd),2)}Mbps"
                dtIni = dtTimes[0]
                dtFin = dtTimes[len(dtTimes)-1]

                if len(PicoTemp) == 0:

                    PTemp = "SysUnsurpC"
                    MTemp = "SysUnsurpC"

                else:

                    PTemp = f"{max(PicoTemp)}C"
                    MTemp = f"{sum(PicoTemp)/len(PicoTemp)}C"

                data = [user,dtIni,dtFin,Pcpu,Pram,Pmem,Mcpu,Mram,Mmem,PVSend,MVSend,PVRecv,MVRecv,PTemp,MTemp]

                with open(CSV, mode = "a", newline='') as arq:

                    escritor = csv.writer(arq)
                    escritor.writerow(data)

                count = 0
            
            time.sleep(10)

    else:
    
        print('Erro: o csv não existe')

timeFrame10s()