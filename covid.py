import pandas as pd
import numpy as np
import matplotlib.pylab as plty
import pandas as pd
import numpy as np
import streamlit as st
import unicodedata
import re
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio



# Configurações da Page 
st.set_page_config(
page_title= "Dados Covid-19 PE",
page_icon= ":globe_with_meridians:",
layout = "centered",
initial_sidebar_state="auto",    
)

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)



## TRATAMENTO DOS DADOS ############
def load_data():
  df1= pd.read_csv('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/HIST_PAINEL_COVIDBR_2020_Parte1_26out2021.csv' ,sep=';')
  df2= pd.read_csv('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/HIST_PAINEL_COVIDBR_2020_Parte2_26out2021.csv' ,sep=';')
  df3= pd.read_csv('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/HIST_PAINEL_COVIDBR_2021_Parte1_26out2021.csv', sep=';')
  df4= pd.read_csv('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/HIST_PAINEL_COVIDBR_2021_Parte2_26out2021.csv', sep= ';')
  data1 = pd.concat([df1,df2,df3,df4], ignore_index=True)
  return data1
 

data= load_data()
data.data =pd.to_datetime(data.data)

# função criada para aplicar valores a dados faltantes
lista = ['estado']
municipio= ['municipio']

@st.cache
def missing (df, lista):
  for col in lista:
    if df[col].dtype == object:
      df[col].fillna ('Total', inplace= True)
    else:
      df[col].fillna(0, inplace= True)  

missing(data,lista) 
missing(data,municipio)


def vacinape_load():
  datas= pd.read_csv('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/doses_aplicadas_municipios-25-10.csv',sep=';' ,encoding='latin-1')
  return datas

datas = vacinape_load()
dataN= datas.drop(columns=['GERES','CÓDIGO'])
dataN.columns= dataN.iloc[0]
dataN= dataN.drop(0)
dataN.columns.to_list()

dataN= dataN.set_axis([ 'Municipio','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2',
 'DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','Reforço','DOSE1','DOSE2',
 'Reforço','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','Reforço','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2',
 'DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','DOSE1','DOSE2','zerado'], axis=1)


 # CRIANDO AS FUNÇÕES DE SOMA DE CADA VACINA APLICADA 

def soma_dose_1():
  global dataN
  uma_dose = dataN.DOSE1.astype(int)
  return uma_dose.sum(axis=1)

uma_dose= soma_dose_1()
uma_dose= pd.DataFrame(uma_dose, columns=['Primeira_Dose'])


def soma_dose_2():
  global dataN
  duas_doses = dataN.DOSE2.astype(int)
  return duas_doses.sum(axis=1)

duas_dose = soma_dose_2()
duas_dose = pd.DataFrame(duas_dose, columns=['Segunda_Dose'])



def soma_dose_extra():
  global dataN
  dose_extral = dataN.Reforço.astype(int)
  return dose_extral.sum(axis=1)

dose_extras = soma_dose_extra()
dose_extra= pd.DataFrame(dose_extras, columns=['Dose_extra'])


Mup = dataN.Municipio
municipio= pd.DataFrame(Mup)


def set_vacinados():
  set_vacinados_pe =pd.concat([municipio,uma_dose,duas_dose,dose_extra], axis=1)
  return set_vacinados_pe

set_vacinados = set_vacinados()


## dataset população PE
def populacao_load():
  popPE= pd.read_excel('/content/drive/MyDrive/HIST_PAINEL_COVID_atualizado/estimativa_pop_pe (1).xlsx')
  popPE=popPE.query('UF == "PE"')
  poppe=popPE.set_axis(['UF','Municipio', 'Populacao'], axis=1)
  poppe['Municipio'] = poppe['Municipio'].str.upper()
  poppe= poppe.loc[:, ('Municipio','Populacao')]
  return poppe
 


poppe = populacao_load()

## Tratando a retirada de acentos e caracteres especiais. 
string= []


for lista in poppe['Municipio']:

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', lista)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    palavraSemAcento= re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)
    string.append(palavraSemAcento)



poppe['Municipio']= string


# Realizando a junção dos datasets 

vacinados_pop= pd.merge(set_vacinados,poppe, how='left', on= ['Municipio'])



# ATRIBUINDO UM NOVO TIPO PARA A AXIS= 1 INTERGE
vacinados_pop.Populacao= vacinados_pop.Populacao.astype(int)


# Criando novos axis-=1 para as porcentagem de cada dose aplicada.

def pocentagem():
  porc = (vacinados_pop.Primeira_Dose/vacinados_pop.Populacao) * 100
  return round(porc,2)

def pocentagem_dose2():
  porc = (vacinados_pop.Segunda_Dose/vacinados_pop.Populacao) * 100
  return round(porc,2)


def pocentagem_dose_extra():
  porc = (vacinados_pop.Dose_extra/vacinados_pop.Populacao) * 100
  return round(porc,2)



vacinados_pop['Porcentagem_dose1']= pocentagem()
vacinados_pop['Pocentagem_dose2']= pocentagem_dose2()
vacinados_pop['pocentagem_dose_extra']= pocentagem_dose_extra()





####### Pagina principal #####################################################



config = {'displayModeBar': False}

pe = data.loc[data.estado == 'PE']
st.markdown('## O dashboard apresenta informações sobre o covid-19 no estado de **Pernambuco**.')

st.markdown("""Fonte: Ministério da Saúde. Secretaria de Vigilância em Saúde (SVS): Guia de Vigiläncia Epidemiológica do COVID-19.Secretarias Municipais e Estaduais de Saúde.') 
*População: Estimativas de 2019 utilizadas pelo TCU para determinação das cotas do FPM (sem sexo e faixa etária). Disponível em https://datasus.saude.gov.br/populacao-residente""")

st.text(' Dados atualizados em 25/10/2021')

st.sidebar.title("Painel de Controle Dinâmico")

st.sidebar.markdown('Casos e óbitos confirmados Covid-19')

ranking= st.sidebar.radio("Defina o Status de Casos ", ('Confirmados', 'Óbitos'))

if ranking == 'Confirmados':
  dados1 = pe[['municipio','casosAcumulado']]
  dados1 = dados1.drop_duplicates('municipio', keep='last')
  num= st.sidebar.slider('Ranking de casos por Município:', 4, 20)
  dados1= dados1.sort_values('casosAcumulado', ascending= False).head(num)
  
 ### PLOTANDO OS TOP 20  MUNICÍPIOS COM MAIORES CASOS  ########
 
  fig1 = px.bar(dados1, y='casosAcumulado', x='municipio', text='casosAcumulado',color='casosAcumulado',title="Ranking dos municípios com maiores números de casos confirmados de covid-19", width= 700,height=500)
  fig1.update_traces(texttemplate='%{text:.2s}' , textposition='outside')
  fig1.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
  st.plotly_chart(fig1,use_container_width=True, config=config)
  
## Serie temporal para habilitar os dados móveis.
  dados = pe[['data','casosNovos']]
  dados = dados.drop_duplicates('data')  # eliminar as data repetidas.


 # dpm= pe[['data', 'municipio','casosNovos','casosAcumulado']]
  #dpm= dpm.drop_duplicates('municipio', keep= 'last')




  ## PLOTANDO MÉDIA X CASOS NOVOS 
  media_caso = st.sidebar.button ('Média Móvel de Casos')
  mp= pe.municipio.unique().tolist()
  mp.pop(0)
  
    
  if media_caso:
    media= dados.rolling(7).mean()
    media= round(media, 0) 
    dados['media_movel'] = media
    fig= px.line(dados, x= 'data', y= ['casosNovos','media_movel'], title='Média Móvel de novos casos confirmados de covid-19', hover_data={"data": "|%B %d, %Y"})
    fig.update_xaxes( dtick="M1", tickformat="%b\n%Y")
    st.plotly_chart(fig, width=2000, height=500)

      ## Tendência de casos sobre 14 dias
    variacao = dados.tail(14)
    primeiro= variacao.media_movel[:1].values 
    ultimo = variacao.media_movel[13:].values

    with st.expander("Análise da variação de Casos confirmados"): 
      st.write(""" calcula a variação percentual das médias móveis em um intervalo de 14 dias. No qual caso o percentual for de até 15%, 
      é considerado estável. Se for acima de 15% positivos, está em crescimento. Se for mais de 15% negativos, está em queda.""")
      
      if primeiro < ultimo: 
        subs = ultimo - primeiro
        result_var = subs/primeiro * 100
        var = pd.DataFrame(result_var)
        r =round(var, 0) 
        r = int (r[0])
        if r > 15:
          st.write (" A variação apresenta tendência de alta de ",(r),"%")
        else:
          st.write (" A variação apresenta tendência de estabilidade  de ",(r),"%")



      elif primeiro > ultimo:
        subs = primeiro - ultimo
        result_var = subs/ultimo * 100
        var = pd.DataFrame(result_var)
        r =round(var, 0) 
        r = int (r[0])
        if r > 15:
          st.write (" A variação apresenta tendência de Baixa de ",(r),"%")
        else:
          st.write (" A variação apresenta tendência de estabilidade  de ",(r),"%")    



elif ranking == 'Óbitos':

  ## Serie temporal para habilitar os dados móveis.
  dados2= pe[['municipio','obitosAcumulado']]
  dados2 = dados2.drop_duplicates('municipio', keep= 'last')
  num1= st.sidebar.slider('Ranking de óbitos por município:', 4, 20)
  dados2= dados2.sort_values('obitosAcumulado', ascending=False).head(num1)
  fig2 = px.bar(dados2, y='obitosAcumulado', x='municipio', text='obitosAcumulado',color='obitosAcumulado',title='Ranking dos municípios com maiores números de óbitos confirmados de covid-19', width= 700,height=500)
  fig2.update_traces(texttemplate='%{text:.2s}', textposition='outside')
  fig2.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
  st.plotly_chart(fig2,use_container_width=True, config=config)

  dados_Obito = pe[['data','obitosNovos']]
  dados_Obito = dados_Obito.drop_duplicates('data')  # eliminar as data repetidas.

  ## PLOTANDO MÉDIA X NOVOS ÓBITOS
  media_button_obito = st.sidebar.button('Media Móvel de Óbitos')
  mpo= pe.municipio.unique().tolist()
  mpo.pop(0)


  if media_button_obito:
    media_obito = dados_Obito.rolling(7).mean()
    media_obito= round(media_obito, 0) 
    dados_Obito['Media_Móvel'] = media_obito
    fig_obito= px.line(dados_Obito, x= 'data', y= ['obitosNovos', 'Media_Móvel'], title='Média Móvel de óbitos confirmados de Covid-19', hover_data={"data": "|%B %d, %Y"})
    fig_obito.update_xaxes( dtick="M1", tickformat="%b\n%Y")
    st.plotly_chart(fig_obito,use_container_width=True, config=config)

    with st.expander("Análise da variação de óbtos"): 
      st.write(""" calcula a variação percentual das médias móveis em um intervalo de 14 dias. No qual caso o percentual for de até 15%, 
      é considerado estável. Se for acima de 15% positivos, está em crescimento. Se for mais de 15% negativos, está em queda.""")

      variacao_obito = dados_Obito.tail(14)
      primeiro_obito= variacao_obito.Media_Móvel[:1].values 
      ultimo_obito = variacao_obito.Media_Móvel[13:].values

      if primeiro_obito <= ultimo_obito: 
         subs_obito = ultimo_obito - primeiro_obito
         result_var_obito = subs_obito/ primeiro_obito * 100
         media_final_obito = pd.DataFrame(result_var_obito)
         resut_obito =round(media_final_obito, 0) 
         resut_obito = int (resut_obito[0])
         if resut_obito > 15:
            st.write(" A variação apresenta tendência de alta de ",(resut_obito),"%")
         else:
           st.write (" A variação apresenta tendência de estabilidade  de ",(resut_obito),"%")    
      

      elif primeiro_obito >= ultimo_obito:
         subs_obito = primeiro_obito - ultimo_obito
         result_var_obito = subs_obito/ultimo_obito * 100
         media_final_obito = pd.DataFrame(result_var_obito)
         resut_obito =round(media_final_obito, 0) 
         resut_obito = int (resut_obito[0])
         if resut_obito > 15:
           st.write(" A variação apresenta Tendência de Baixa de",(resut_obito),"%")
         else:
           st.write (" A variação apresenta tendência de estabilidade  de ",(resut_obito),"%")   

# FILTRANDO O MUNICÍPIO EM DESTAQUE
with st.expander('Vacinados por Município'): 
  mun_vacinados=vacinados_pop.Municipio.tolist() 
  st.markdown('Percentual de Vacinados por município')   
  vacinados_municipio = st.selectbox('Defina o Município',mun_vacinados)
  vacinados_municipio = vacinados_pop.loc[vacinados_pop.Municipio == vacinados_municipio] 
  button_vacinados = st.button("Consultar")

  if button_vacinados:
  
    n_casos = []
    tipo=pd.DataFrame(['Primeira dose', 'Segunda Dose', 'Dose Extra'], columns=['Tipo de vacina'])
    n_casos= [ vacinados_municipio.Porcentagem_dose1.values, vacinados_municipio.Pocentagem_dose2.values, vacinados_municipio.pocentagem_dose_extra.values]
    n_casos= pd.DataFrame(n_casos, columns=['Valores'])
    dado1 =  [tipo, n_casos]
    dados= pd.concat(dado1, ignore_index=False, axis= 1)


      # GRÁFICO De percetual de VACINADOS 
    fig_vacianos_municipio= px.bar(dados, y='Valores', x='Tipo de vacina', text='Valores' , color='Tipo de vacina',color_discrete_map={'Primeira dose':'Blue','Segunda Dose':'green','Dose Extra':'red'})
    fig_vacianos_municipio.update_traces(texttemplate='%{text:.2s}' + '%')
    fig_vacianos_municipio.update_layout(title_text='Percentual de Vacinados por população' , barmode='group')
    st.plotly_chart(fig_vacianos_municipio,use_container_width=True, config=config)

# tratamento dos dados de vacinados x não vacinados 

total = vacinados_pop.iloc[:, [1,2,3]]
populacao_total = vacinados_pop.iloc[:,[4]]
total = total.sum()
total=pd.DataFrame(total)
total = total.reset_index()
total1 =total.set_axis(['Tipo', 'total'], axis=1)
total_populacao_pe=populacao_total.sum().values
values= total1.total.values



# Loop para realizar a subtração entre população e vacinados de cada tipo
operacao= []
for  t in range(3):
    total_populacao_pe=populacao_total.sum().values
    operacao.append (total_populacao_pe - values[t])

operacao= pd.DataFrame(operacao)
total1['Ñ_vacinados']= operacao


pop_vacinas =total1.Ñ_vacinados
pop_vacinas= pd.DataFrame(pop_vacinas)
pop_vacinas ['Tipo'] = ['Não vaciados dose1', 'Não vacinado dose2', 'Não vaciandos dose extra']
total1 =total1.drop(columns= ['Ñ_vacinados'])
pop_vacinas.columns= ['total', 'Tipo']

# Concatenando vacinados por tipo 
juncao= pd.concat([total1,pop_vacinas], axis=0,  ignore_index=True)

# aplicado ação para plotar Gráfico Pie 

vac1 = juncao.iloc[[0,3]]
vac2 = juncao.iloc[[1,4]]
vac3= juncao.iloc[[2,5]]

pie_one_labels = vac1.Tipo.values
pie_one_values = vac1.total.values 

pie_two_labels= vac2.Tipo.values
pie_two_values= vac2.total.values

pie_three_labels= vac3.Tipo.values
pie_three_values = vac3.total.values 

# atribuindo a cada variável um valor para plotagem sobre o total da população

with st.expander('Percentual de Vacinados em Pernambuco por dose aplicada'):

  tetet = make_subplots(rows=1, cols=3, specs=[[{'type':'pie'}, {'type':'domain'},{'type':'domain'}]])

  tetet.add_trace(go.Pie(labels=pie_one_labels, values=pie_one_values, name="Primeira Dose "), 1,1)
  tetet.add_trace(go.Pie(labels=pie_two_labels, values=pie_two_values, name="Segunda Dose"), 1,2)
  tetet.add_trace(go.Pie(labels=pie_three_labels, values=pie_three_values, name= "Dose Extra"),1,3)
  tetet.update_traces(hole=.4, hoverinfo="label+percent+name")

  tetet.update_layout(
      
    #title='i <3 subplots',
   
    annotations=[dict(text='Dose1', x=0.10, y=0.5, font_size=15, showarrow=False),
                 dict(text='Dose2', x=0.50, y=0.5, font_size=15, showarrow=False),
                 dict(text='Extra', x=0.90, y=0.5, font_size=15, showarrow=False)])
  st.plotly_chart(tetet, config=config, use_container_width=True)


with st.expander('Vacinados Segunda dose Região Metropolitana'):
 cidades_metro = ('RECIFE', 'OLINDA', 'ILHA DE ITAMARACA', 'ARACOIABA', 'CAMARAGIBE','IGARASSU', 'ITAPISSUMA', 'MORENO', 'PAULISTA', 'SAO LOURENCO DA MATA', 'JABOATAO DOS GUARARAPES','IPOJUCA', 'CABO DE SANTO AGOSTINHO', 'CAMARAGIBE','ABREU E LIMA' )
 Metro_recife= vacinados_pop.loc[ vacinados_pop.Municipio.isin(cidades_metro)]
 metropolitana_dose2 = Metro_recife.sort_values('Pocentagem_dose2', ascending= True)
 fig_vacinados = px.bar(metropolitana_dose2, x= 'Pocentagem_dose2',y='Municipio', barmode='group', text='Pocentagem_dose2' ,color= 'Segunda_Dose', orientation='h', width= 700, height=500)
 fig_vacinados.update_traces(texttemplate='%{text:.2s}' + '%')
 fig_vacinados.update_layout(barmode='group')
 st.plotly_chart(fig_vacinados,use_container_width=True, config=config)
