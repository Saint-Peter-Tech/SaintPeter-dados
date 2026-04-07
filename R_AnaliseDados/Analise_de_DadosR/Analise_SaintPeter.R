install.packages("lubridate")
install.packages("readr")


library(readr)
library(lubridate)

df <- read_csv("../dados_brutos/dados_brutos.csv")

#Convertendo para data e hora
df$timestamp <- as.POSIXct(df$timestamp, format = "%Y-%m-%d %H:%M:%OS")

#Criando coluna hora
df$hora <- hour(df$timestamp)

summary(df)

#Pegando as médias

media_cpu <- mean(df$cpu_percent)

media_ram_gb <- mean(df$ram_used_gb)

media_bytes_send <- mean(df$bytes_sent_per_sec)

media_bytes_rec <- mean(df$bytes_recv_per_sec)


#Descobrindo intervalo de tempo 

intervalo <- mean(diff(df$timestamp))

#Função de probabilidade de estar ligado a cada periodo
#De acordo com pesquisa relacionadas a estatistica de qtd de acidentes 
#e cirurgias para cada horario
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

#Definindo tempo de registro

inicio <- max(df$timestamp) + intervalo
fim <- inicio + days(7)


