import requests, json
import pandas as pd
import warnings
import re
import time
import ssl
import nltk
import snowballstemmer
import nlpnet
import streamlit as st
from helpers import *
import plotly.graph_objects as go
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import plotly.io as pio

# naming a layout theme for future reference
pio.templates["mycolors"] = go.layout.Template(
    layout_colorway=['#00429d', '#325da9', '#4e78b5', '#6694c1', '#80b1cc', '#9dced6', '#c0eade', '#ffffe0', '#ffdac4', '#ffb3a7', '#fb8a8c', '#eb6574', '#d5405e', '#b81b4a', '#93003a']
)

pio.templates.default = "mycolors"


vazio = True
df_final,df= pd.DataFrame(),pd.DataFrame()

def collect(tags_final):
    x, y, controle = 0,0,0
    nomes, urls, formato,descricao,nomes2,urls2,formato2, descricao2= pd.Series(),pd.Series(),pd.Series(),pd.Series(),pd.Series(),pd.Series(),pd.Series(),pd.Series()
    for palavra in tags_final:
            print(palavra)
            filtro = {'query': 'name:' + palavra}
            filtro2 = {'query': 'description:' + palavra}

            # Consumindo dados do ckan, de acordo com o termo
            api = requests.get('http://dados.gov.br/api/3/action/resource_search', params=filtro, verify=False)
            api2 = requests.get('http://dados.gov.br/api/3/action/resource_search', params=filtro2, verify=False)
            print(filtro)
            repos = json.loads(api.text)
            repos2 = json.loads(api2.text)

            # Preparando os atributos mais importantes

            # Criando 3 séries de dados: "nomes", "urls" e "formato"
            if repos['result']['count'] > 0:
                vazio = False
                for resultado in repos['result']['results']:
                    nomes.at[x] = repos['result']['results'][x]['name']
                    urls.at[x]= repos['result']['results'][x]['url']
                    formato.at[x] = repos['result']['results'][x]['format']
                    descricao.at[x]= repos['result']['results'][x]['description']
                    x = x + 1

            if repos2['result']['count'] > 0:
                vazio = False
                for resultado in repos2['result']['results']:
                    nomes2.at[y]= repos2['result']['results'][y]['name']
                    urls2.at[y]= repos2['result']['results'][y]['url']
                    formato2.at[y]= repos2['result']['results'][y]['format']
                    descricao2.at[y]= repos2['result']['results'][y]['description']
                    y = y + 1

            if not vazio:
                # Criando um único dataframe com todos os valores dos 3 atributos
                if repos['result']['count'] > 0:
                    df = pd.DataFrame({'nome': nomes, 'url': urls, 'formato': formato, 'descricao': descricao})

                    if repos2['result']['count'] > 0:
                        df = df.append(pd.DataFrame({'nome': nomes2, 'url': urls2, 'formato': formato2, 'descricao': descricao2}))

                    # Acertando os index depois de apagar linhas
                    df = df.reset_index(drop=True)
                    #df.to_csv('teste.txt')
                    # Refinando o dataframe para conter apenas os dados que realmente possuem o termo desejado (regex)
                    for index, row in df.iterrows():
                        if row["nome"]:
                            if not row["nome"].isalpha():
                                row["nome"] = row["nome"].replace(',', '')
                                row["nome"] = row["nome"].replace('.', '')
                                row["nome"] = row["nome"].replace('-', '')
                                row["nome"] = row["nome"].replace('/', '')
                                row["nome"] = row["nome"].replace('\'', '')
                                frase = re.split(r'\s', row["nome"].lower())
                        if row["nome"]:
                            if not row["descricao"].isalpha():
                                row["descricao"] = row["descricao"].replace(',', '')
                                row["descricao"] = row["descricao"].replace('.', '')
                                row["descricao"] = row["descricao"].replace('-', '')
                                row["descricao"] = row["descricao"].replace('/', '')
                                row["descricao"] = row["descricao"].replace('\'', '')
                                desc = re.split(r'\s', row["descricao"].lower())

                        if palavra not in frase:
                            if palavra not in desc:
                                df.drop(index)
                        # if row["url"]== "http://dados.al.gov.br/dataset/d8f3ac16-6441-4f45-8c69-a2fc5a4ff8a6/resource/ab2effa7-68c7-4150-adba-fefaaccef1a8/download/quilombolascopia.png":

                        if controle == 0:
                            df_final = df
                        else:
                            df_final = df_final.append(df)

                        controle = controle + 1
                        x = 0
                        y = 0
                    else:
                        controle = controle + 1
                        x = 0
                        y = 0

    return df_final

def clean(tags_final,df_final):

    df_final = df_final.drop_duplicates(subset='nome', keep='first', inplace=False)
    df_final = df_final.drop_duplicates(subset='url', keep='first', inplace=False)
    # df_final = df_final.drop_duplicates(subset='descricao', keep='first', inplace=False)
    df_final = df_final.reset_index(drop=True)
    # tupla = convert(filtered_sentence)
    #df_final["descricao"].to_csv('teste.txt')


    for index, linha in df_final.iterrows():
        lista_termos_nome = linha['nome'].split(" ")
        lista_termos_nome = list(map(str.lower, lista_termos_nome))
        tags_final = list(map(str.lower, tags_final))
        for elem in tags_final:
            if elem in lista_termos_nome:
                break
            else:
                lista_termos_desc = linha['descricao'].split(" ")
                lista_termos_desc = list(map(str.lower, lista_termos_desc))
                for elem in tags_final:
                    if elem in lista_termos_desc:
                        break
                    else:
                        df_final = df_final.drop(index)

    return df_final


def setup(example_sent):
    if example_sent:
        tagger = nlpnet.POSTagger('pos-pt', language='pt')
        tags = tagger.tag(example_sent)
        tags_final = []
        print('--------------')
        for item in convert(tags):
            for i in item:
                # print(i)
                if i[1] == 'N':
                    tags_final.append(i[0])
                    #tags_final.append(ps.stem(i[0]))
#                     if i[0].lower() not in ("brasil" or "brasileiro" or "brasileira"):
#                         if i[0].endswith('s'):
#                             print("----- tirando plural")
#                             stp = i[0][:-1]
#                             tags_final.append(stp)
#                         else:

        print('--------------')
        print(tags_final)
        print('--------------')

        # Ignorando os warnings
        warnings.filterwarnings("ignore")
        warnings.simplefilter(action='ignore', category=FutureWarning)

        inicio = time.time()
        df_final = collect(tags_final)
        #df_final.to_csv("teste.txt")
        if df_final.empty:
            st.write('Não foi possível encontrar!')
        else:
            df_final = clean(tags_final, df_final)

            fim = time.time()
            print('duracao: %f segundos' % (fim - inicio))
            df_final.to_csv('result.txt')
            #st.dataframe(df_final["nome"])
            df_final = df_final.reset_index()
            #st.table(df_final["nome"])

            for index, row in df_final.iterrows():
                print(row["url"])

            fig = go.Figure(data=go.Table(columnorder = [1,2],
                                            columnwidth = [100,400],header=dict(values=list(df_final[['index','nome']].columns),line_color='darkslategray', align='center',font=dict(size=15)),
                cells=dict(values=[df_final.index,df_final.nome], fill_color='#ffffff',line_color='darkslategray',font=dict(size=15), height=30)))

            fig.update_layout(margin=dict(l=5,r=5,b=10,t=10))
            st.write(fig)


        selectRows(df_final)

def selectRows(df):
    selected_indices = st.multiselect('Por favor, selecione o índice do conjunto de dados que você deseja visualizar:', df.index)
    if selected_indices:
        selected_rows = df.loc[selected_indices]
        if selected_rows.nome.all():
            st.markdown('<p style="font-size: 14px;">Conjunto de dados selecionado: </p>', unsafe_allow_html=True)
            st.write(selected_rows.nome)
            #submit = st.button('Avançar')
            #if submit:
            chooseColumns(selected_rows)

def chooseColumns(selected):
    url = str("".join(selected.url.values))
    
    #st.write("Confira a origem destes dados em %s" % url)
    try:
        df = pd.read_csv(url,encoding = 'latin1',delimiter=";")
    except:
        df = pd.read_csv(url,encoding = 'latin1')

    print(df.columns)

    selected_columns = st.multiselect('Por favor, selecione as colunas que você deseja visualizar:', df.columns)
    print(selected_columns)
    if selected_columns:
        column1 = selected_columns[0]
        column2 = selected_columns[1]
        arr_column1 = df[column1].values
        arr_column2 = df[column2].values
        df_filter = pd.DataFrame({column1:arr_column1, column2:arr_column2})
        print(df_filter)
        categorizeColumns(column1, column2, df_filter)


def categorizeColumns(column1, column2, df): #0 para numero, 1 para data, 2 para string, 3 para non
    fig = go.Figure()


    try:
        df[column2] =  df[column2].apply(lambda x: re.sub("R\$",'', str(x)))
        df[column2] =  df[column2].apply(lambda x: re.sub('[^\w\s\d]|_','', str(x)))
        df[column2] = df[column2].astype(float, errors = 'raise')
    except:
        result = None

    try:
        df[column1] =  df[column1].apply(lambda x: re.sub("R\$",'', str(x)))
        df[column1] =  df[column1].apply(lambda x: re.sub('[^\w\s\d]|_','', str(x)))
        df[column1] = df[column1].astype(float, errors = 'raise')
    except:
        result=None

    typeCol1 = columnType(df[column1])
    print(typeCol1)
    typeCol2 = columnType(df[column2])
    print(typeCol2)

    print(df)
    if (typeCol1==2):
        if (typeCol2==0):
            df_group = df.groupby([column1], as_index=False)[column2].sum()
            fig = build_bar_chart(df, column1,column2,'')
            fig.update_yaxes(automargin=False)
            fig.update_xaxes(automargin=True)
            fig.update_layout(height=800,width=1050)
            st.plotly_chart(fig)
    else:
        if (typeCol1==0):
            if (typeCol2==0):
                fig = build_scatter_plot(df, '', column1, column2, "")
                fig.update_yaxes(automargin=False)
                fig.update_xaxes(automargin=True)
                fig.update_layout(height=600,width=600)
                st.plotly_chart(fig)

if __name__ == "__main__":
#     st.image('./amazons.jpg', width=100)
#     st.title("Hipólita")

    col1, mid, col2 = st.columns([1,3,20])
    with col1:
        st.image('./amazons.jpg', width=100)
    with col2:
        st.markdown('<h1 style="color: black;font-family:Courier;">Hipólita</h1>',
                                    unsafe_allow_html=True)

    nltk.download('punkt')
    nltk.download('stopwords')
    example_sent = ''
    ps = snowballstemmer.stemmer("portuguese")
    st.write('Olá, cidadão!')
    example_sent = st.text_input("O que você precisa?").lower()
    setup(example_sent)


#Tratar caso de não disponibilidade