library(readr)
library(lubridate)

set.seed(123) # para reproduzir os resultados

#===================== Data Frame de Refência =================================

#Importando csvs de base
captura_monitor1 <- read_csv("../dados_brutos/dados_brutos_gustavo.csv")

captura_monitor2 <- read_csv("../dados_brutos/dados_brutos_diego.csv")

captura_monitor3 <- read_csv("../dados_brutos/dados_brutos_pedro.csv")

captura_monitor4 <- read_csv("../dados_brutos/dados_brutos_maria.csv")

#Criando df de base de referência
df_base <- rbind(captura_monitor1, captura_monitor2, captura_monitor3,
                 captura_monitor4)

#Criando IDs

df_base$id <- 1:nrow(df_base)

#Convertendo para data e hora
df_base$timestamp <- as.POSIXct(df_base$timestamp, format = "%Y-%m-%d %H:%M:%OS")



#Criando coluna hora
df_base$hora <- hour(df_base$timestamp)

summary(df_base)

#Pegando as médias

media_cpu <- mean(df_base$cpu_percent)

media_ram <- mean(df_base$ram_percent )

media_bytes_send <- mean(df_base$bytes_sent_per_sec)

media_bytes_rec <- mean(df_base$bytes_recv_per_sec)

#Pegando medianas

mediana_cpu <- median(df_base$cpu_percent)

mediana_ram <- median(df_base$ram_percent)

mediana_bytes_send <- median(df_base$bytes_sent_per_sec)

mediana_bytes_rec <- median(df_base$bytes_recv_per_sec)

#Pegando desvio padrão

desvio_cpu <- sd(df_base$cpu_percent)

desvio_ram <- sd(df_base$ram_percent)

desvio_bytes_send <- sd(df_base$bytes_sent_per_sec)

desvio_bytes_rec <- sd(df_base$bytes_recv_per_sec)

# Ordenando por user e tempo
df_base <- df_base[order(df_base$user, df_base$timestamp), ]


#Descobrindo intervalo de tempo 

intervalo_geral <- mean(c(
  mean(as.numeric(diff(df_base$timestamp[df_base$user == "gusta"]))),
  mean(as.numeric(diff(df_base$timestamp[df_base$user == "diegohenrique"]))),
  mean(as.numeric(diff(df_base$timestamp[df_base$user == "maria-maia"]))),
  mean(as.numeric(diff(df_base$timestamp[df_base$user == "Pedro Sousa"])))
))

intervalo_geral <- round(intervalo_geral)

#Intervalo de captura é 11
intervalo_geral




#==================== SIMULAÇÃO ====================


#Função de probabilidade de estar ligado a cada periodo,
#De acordo com pesquisa relacionadas a estatisticas de qtd de acidentes 
#e cirurgias a cada horario

prob_ligado <- function(hora) {
  if (hora >= 7 & hora < 12) {
    return(0.80)  
  } else if (hora >= 12 & hora < 15) {
    return(0.70)  
  } else if (hora >= 15 & hora < 16) {
    return(0.20)  
  } else if (hora >= 16 & hora < 20) {
    return(0.60)  
  } else if (hora >= 20 & hora < 23) {
    return(0.90) 
  } else if (hora >= 0 & hora < 6) {
    return(0.90)  
  } else {
    return(0.30)  
  }
}

#Horario de inicio da simulação

hora_atual <- 21 

prob <- prob_ligado(hora_atual)

#Função para gerar users

gerar_usuarios <- function(nome_usuario, inicio, fim) {
  
  registros <- list()
  
  #Probabilidade aleatoria de picos por hora
  
  prob_pico_hora <- runif(1, min = 0.001, max = 0.04)
  
  #Probabilidade de picos por leitura (uma hora = 3600 seg)
  
  prob_pico_leitura <- prob_spike_hora / (3600 / intervalo_geral)
  
  fim_do_spike <- as.POSIXct("1901-01-01") #Data antiga so para garantir
  
  while (inicio > fim) {
    
    hora <- hour(inicio) #Horario "atual"
    
    #Verificando se o monitor esta ligado
    
    if (runif(1) < prob_ligado(hora)){
      
    }
    
    
  }
  
}










