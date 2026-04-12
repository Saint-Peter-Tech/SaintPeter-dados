


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

df_eletiva_semana$porcentagem <- round(df_eletiva_semana$pacientes
                                       / 32001 * 100, 2)
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

df_eletiva_hora$faixa_horaria <- ifelse(df_eletiva_hora$hora < 6, "00-06",
                                        ifelse(df_eletiva_hora$hora < 12,
                                               "06-12",
                                               ifelse(df_eletiva_hora$hora < 18, 
                                                      "12-18","18-24")))

df_eletiva_hora$porcentagem <- round(df_eletiva_hora$pacientes 
                                     / 32001 * 100, 2)
df_eletiva_hora$tipo <- "Eletiva"

print(df_eletiva_hora)


#----------------Data e Hora de Cirurgias de emergencia --------------

#Não existem dados estrururados, então tudo é uma estimativa
#da realidade nessa parte. [Ref2], [Ref3], {Ref$}

dias <- c("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo")

pesos <- c(0.14, 0.13, 0.13, 0.14, 0.18, 0.17, 0.11)

df_emergencia_semana$tipo <- "Emergencia"

df_emergencia_semana$dia_semana <- factor(
  df_emergencia_semana$dia_semana,
  levels = c("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo")
)

df_emergencia_semana 

#Cirurgias de emergencia por  hora

horas <- 0:23

pesos_hora <- c(
  3,3,2,2,2,2,  
  4,5,6,7,8,9,      
  10,11,12,13,14,15,
  17,18,19,18,16,14 
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



