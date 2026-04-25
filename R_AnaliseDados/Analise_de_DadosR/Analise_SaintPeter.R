
library(ggplot2)
library(dplyr)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++
#Data e hora de cirurgias eletivas e de emergencia:
#+++++++++++++++++++++++++++++++++++++++++++++++++++++



#Fontes:

#[Ref1] Amy S. Nowacki, “Surgery Timing Dataset”, TSHS Resources Portal (2016)

#[Ref2] Redação Mobilidade, "Sexta-feira e sábado são os dias em que
#ocorrem mais acidentes de trânsito"

#[Ref3] Segunda, "sexta e sábado são os dias da semana
#com mais acidentes no trânsito. Entenda", segs (2024)

#[Ref4] 
#Meschino MT, Giles AE, Rice TJ, Saddik M, Doumouras AG, Nenshi R, Allen L,
#Vogt K, Engels PT.
#Operative timing is associated with increased morbidity and mortality in
#patients undergoing emergency general surgery: a multisite study of emergency
#general services in a single academic network. 
#Can J Surg. 2020 Jul 9;63(4):E321-E328. doi: 10.1503/cjs.012919. PMID: 32644317;
#PMCID: PMC7458678.



#-------------Data e Hora de Cirurgias eletivas [Ref1]------------------------

#Carregar arquivo Ref1
load(file.choose())

#Dias de cirurgias eletivas

contagem_dia <- table(stata_data$dow)

df_eletiva_semana <- data.frame(
  dia_semana = names(contagem_dia),
  pacientes  = as.numeric(contagem_dia)
)

converter_dias <- c(
  "Mon" = "Segunda",
  "Tue" = "Terça",
  "Wed" = "Quarta",
  "Thu" = "Quinta",
  "Fri" = "Sexta",
  "Sat" = "Sabado",
  "Sun" = "Domingo"
)

df_eletiva_semana$dia_semana <- converter_dias[df_eletiva_semana$dia_semana]




df_eletiva_semana$dia_semana <- factor(
  df_eletiva_semana$dia_semana,
  levels = c("Segunda", "Terça", "Quarta", "Quinta", "Sexta")
)

df_eletiva_semana$porcentagem <- round(
  df_eletiva_semana$pacientes / sum(df_eletiva_semana$pacientes) * 100, 2
)


df_eletiva_semana$tipo <- "Eletiva"

print(df_eletiva_semana)

#Horarios de cirurgias eletivas

stata_data$hora_inteira <- floor(stata_data$hour)

contagem_hora <- table(stata_data$hora_inteira)

df_eletiva_hora <- data.frame(
  hora      = names(contagem_hora),
  pacientes = as.numeric(contagem_hora)
)

df_eletiva_hora$hora <- as.numeric(df_eletiva_hora$hora)

df_eletiva_hora$porcentagem <- round(
  df_eletiva_hora$pacientes / sum(df_eletiva_hora$pacientes) * 100, 2
)

df_eletiva_hora$faixa_horaria <- ifelse(df_eletiva_hora$hora < 6, "00-06",
                                        ifelse(df_eletiva_hora$hora < 12,
                                               "06-12",
                                               ifelse(df_eletiva_hora$hora < 18, 
                                                      "12-18","18-24")))

df_eletiva_hora$faixa_horaria <- factor(df_eletiva_hora$faixa_horaria,
                                        levels = c("00-06","06-12",
                                                   "12-18","18-24"))


df_eletiva_hora$tipo <- "Eletiva"

print(df_eletiva_hora)


#----------------Data e Hora de Cirurgias de emergencia --------------

#Não existem dados estrururados, então tudo é uma estimativa
#da realidade nessa parte. [Ref2], [Ref3], {Ref$}

dias <- c("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo")

pesos <- c(0.14, 0.13, 0.13, 0.14, 0.18, 0.17, 0.11)

df_emerg_semana<- data.frame(
  dia_semana = dias,
  porcentagem = pesos *100
)

df_emerg_semana$dia_semana <- factor(
  df_emerg_semana$dia_semana,
  levels = c("Segunda","Terça", "Quarta", "Quinta", "Sexta", "Sabado","Domingo")
)

df_emerg_semana$tipo <- "Emergencia"

df_emerg_semana 

#Cirurgias de emergência por  hora

horas <- 0:23

pesos_hora <- c(
  12,8,5,5,6,6,
  
  6,6,7,8,9,10,
  
  9,8,7,6,7,9,
  
  11,11.5,10.5,12,14,14
)

variacao_hora <- runif(24, 0.9, 1.1)

valores_hora <- pesos_hora * variacao_hora

porcentagem <- round(valores_hora / sum(valores_hora) * 100, 2)

df_emergencia_hora <- data.frame(
  hora = horas,
  porcentagem = porcentagem
)

df_emergencia_hora$faixa_horaria <- ifelse(df_emergencia_hora$hora < 6, "00-06",
                                    ifelse(df_emergencia_hora$hora < 12, "06-12",
                                    ifelse(df_emergencia_hora$hora < 18, "12-18",
                                           "18-24")))

df_emergencia_hora$faixa_horaria <- factor(df_emergencia_hora$faixa_horaria,
                                           levels = c("00-06","06-12",
                                                      "12-18","18-24"))

#--------------Unificando Data Frames--------------------------

df_eletiva_junto <- data.frame(
  hora = df_eletiva_hora$hora,
  valor = df_eletiva_hora$porcentagem,
  tipo = "Eletiva"
)

df_emergencia_junto <- data.frame(
  hora = df_emergencia_hora$hora,
  valor = df_emergencia_hora$porcentagem,
  tipo = "Emergência"
)

df_total <- rbind(df_eletiva_junto, df_emergencia_junto)

df_eletiva_semana_junto <- data.frame(
  dia_semana = df_eletiva_semana$dia_semana,
  valor = df_eletiva_semana$porcentagem,
  tipo = "Eletiva"
)

df_emerg_semana_junto <- data.frame(
  dia_semana = df_emerg_semana$dia_semana,
  valor = df_emerg_semana$porcentagem,
  tipo = "Emergência"
)

df_semana_total <- rbind(df_eletiva_semana_junto, df_emerg_semana_junto)

#----------------Gráficos Cirurgias------------------


ggplot(df_total, aes(x = hora, y = valor, color = tipo)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  annotate("rect", xmin = 20, xmax = 24, ymin = -Inf, ymax = Inf,
           fill = "red", alpha = 0.06) +
  annotate("rect", xmin = 0, xmax = 4, ymin = -Inf, ymax = Inf,
           fill = "red", alpha = 0.06) +
  annotate("text", x = 22, y = max(df_total$valor),
           label = "Período com maior fatalidade", color = "red", size = 4) +
  geom_vline(xintercept = 20, color = "red", linetype = "dashed") +
  geom_vline(xintercept = 4, color = "red", linetype = "dashed") +
  labs(
    title = "Eletivas vs Emergência por Hora",
    x = "Hora",
    y = "Porcentagem %"
  ) +
  theme_minimal() +
  scale_x_continuous(breaks = 0:23)

ggplot(df_semana_total, aes(x = dia_semana, y = valor, color = tipo, group = tipo)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  labs(
    title = "Cirurgias Eletivas vs Emergência por Dia da Semana",
    x = "Dia",
    y = "Porcentagem %"
  ) +
  theme_minimal()


#----------Gerando pesos para arq de captura python-----------------

proporcao_eletiva    <- 0.55
proporcao_emergencia <- 0.45

todos_dias <- c("Segunda","Terça","Quarta","Quinta","Sexta","Sabado","Domingo")

df_eletiva_semana_completo <- data.frame(
  dia_semana  = todos_dias,
  porcentagem = 0
)

for (i in df_eletiva_semana$dia_semana) {
  df_eletiva_semana_completo$porcentagem[
    df_eletiva_semana_completo$dia_semana == i
  ] <- df_eletiva_semana$porcentagem[df_eletiva_semana$dia_semana == i]
}

df_peso_dia <- data.frame(
  dia_semana         = todos_dias,
  pct_eletiva        = df_eletiva_semana_completo$porcentagem,
  pct_emergencia     = df_emerg_semana$porcentagem
)

df_peso_dia$peso_combinado <- round(
  proporcao_eletiva    * df_peso_dia$pct_eletiva +
    proporcao_emergencia * df_peso_dia$pct_emergencia,
  2
)

df_peso_dia$peso_final <- round(
  df_peso_dia$peso_combinado/sum(df_peso_dia$peso_combinado) * 100,
  2
)

df_peso_dia$dia_semana <- factor(df_peso_dia$dia_semana, levels = todos_dias)

print(df_peso_dia)
print(df_peso_dia$peso_final)
print(df_peso_dia$dia_semana)


# --------------------- Pesos por hora ----------------------------------------

todas_horas <- 0:23

df_eletiva_hora_completo <- data.frame(
  hora        = todas_horas,
  porcentagem = 0
)

for (i in df_eletiva_hora$hora) {
  df_eletiva_hora_completo$porcentagem[
    df_eletiva_hora_completo$hora == i
  ] <- df_eletiva_hora$porcentagem[df_eletiva_hora$hora == i]
}

df_peso_hora <- data.frame(
  hora           = todas_horas,
  pct_eletiva    = df_eletiva_hora_completo$porcentagem,
  pct_emergencia = df_emergencia_hora$porcentagem
)

df_peso_hora$peso_combinado <- round(
  proporcao_eletiva    * df_peso_hora$pct_eletiva +
    proporcao_emergencia * df_peso_hora$pct_emergencia,
  2
)

df_peso_hora$peso_final <- round(
  df_peso_hora$peso_combinado / sum(df_peso_hora$peso_combinado) * 100,
  2
)

print(df_peso_hora$peso_final)


#--- gráfico de pesos ----

ggplot(df_peso_dia, aes(x = dia_semana, y = peso_final)) +
  geom_bar(stat = "identity", fill = "blue") +
  labs(title = "Cirurgias por Dia",
       x = "Dia", y = "Porcentagem de Cirurgias Hora") +
  theme_minimal()

ggplot(df_peso_hora, aes(x = hora, y = peso_final)) +
  geom_line(linewidth = 1, color = "blue") +
  geom_point(size = 2, color = "blue") +
  labs(title = "Cirurgias por Hora",
       x = "Hora", y = "Porcentagem de Cirurgias Hora") +
  theme_minimal() +
  scale_x_continuous(breaks = 0:23)


#------------------------------------------------------------
#----------------Analise de Simulação----------------------
#------------------------------------------------------------

#------------Rede  x Qtd de maq ----------------------------------

df_simulacao <- read.csv("C:/Users/gusta/Desktop/saint_peter/SaintPeter-dados/R_AnaliseDados/Analise_de_DadosR/simulacao.csv")

df_simulacao$timestamp <- as.POSIXct(df_simulacao$timestamp, format="%d-%m-%Y %H_%M_%S")

df_simulacao$ligada <- ifelse(df_simulacao$cpu_percent > 0, 1, 0)

df_simulacao$uso_rede <- df_simulacao$bytes_sent_per_sec +
  df_simulacao$bytes_recv_per_sec


maq_ligadas <- aggregate(ligada ~ timestamp, df_simulacao, sum)


rede_media <- aggregate(uso_rede ~ timestamp, df_simulacao, mean)


df_rede <- merge(maq_ligadas, rede_media, by="timestamp")


correlacao <- cor(df_rede$ligada, df_rede$uso_rede)


plot(df_rede$ligada, df_rede$uso_rede,
     pch=16,
     col="pink",
     xlab="Máquinas Ligadas",
     ylab="Uso médio de rede",
     main=paste("Rede X Máquinas (correlação =", round(correlacao,2),")"))

abline(lm(uso_rede ~ ligada, data=df_rede),
       col="red", lwd=2)

#----------------Módulos X CPU -------------------

df_simulacao$modulos_ativos<- 
  (df_simulacao$bpm_status == "Ativo")+
  (df_simulacao$pa_status == "Ativo") +
  (df_simulacao$spo2_status == "Ativo") +
  (df_simulacao$resp_status == "Ativo")+
  (df_simulacao$temperatura_status == "Ativo") +
  (df_simulacao$pic_status == "Ativo") +
  (df_simulacao$pvc_status == "Ativo") +
  (df_simulacao$ecg_status == "Ativo") +
  (df_simulacao$etco2_status == "Ativo")


correlacao_cpu_mod <- cor(df_simulacao$modulos_ativos,
                  df_simulacao$cpu_percent)

modelo <- lm(cpu_percent ~ modulos_ativos,
             data = df_simulacao)


plot(df_simulacao$modulos_ativos, df_simulacao$cpu_percent,
     pch=16,
     col="blue",
     xlab="Quantidade de módulos ativos",
     ylab="CPU %",
     main=paste("CPU x Módulos (correlação =",round(correlacao_cpu_mod,2),")"))
abline(modelo, col="red", lwd=2)

#----------Módulos X RAM ---------------------------------------

correlacao_ram_mod <- cor(df_simulacao$modulos_ativos, df_simulacao$ram_percent)

modelo_ram <- lm(ram_percent ~ modulos_ativos, data = df_simulacao)

plot(df_simulacao$modulos_ativos, df_simulacao$ram_percent,
     col="darkgreen",
     xlab="Quantidade de módulos ativos",
     ylab="RAM %",
     main=paste("RAM X Módulos (correlação =", round(correlacao_ram_mod, 2), ")"))
abline(modelo_ram, col="red", lwd=2)

