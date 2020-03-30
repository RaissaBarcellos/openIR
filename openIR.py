import requests, json
import pandas as pd
import warnings
import re
import time
import ssl
from nltk.stem.snowball import SnowballStemmer
import nltk
import nlpnet
import streamlit as st

def convert(list):
    return tuple(i for i in list)

nltk.download('punkt')
nltk.download('stopwords')
example_sent = ''

ps = SnowballStemmer("portuguese")

st.write('Olá, cidadão!')

#example_sent = input("O que voce precisa?").lower()
example_sent = st.text_input("O que voce precisa?")
if example_sent:
    tagger = nlpnet.POSTagger('pos-pt', language='pt')

    tags = tagger.tag(example_sent)
    tags_final = []
    print('--------------')
    for item in convert(tags):
        for i in item:
            # print(i)
            if i[1] == 'N':
                #tags_final.append(ps.stem(i[0]))
                if i[0].lower() not in ("brasil" or "brasileiro" or "brasileira"):
                    if i[0].endswith('s'):
                        print("----- tirando plural")
                        stp = i[0][:-1]
                        tags_final.append(stp)
                    else:
                        tags_final.append(i[0])
    print('--------------')
    print(tags_final)
    print('--------------')

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Ignorando os warnings
    warnings.filterwarnings("ignore")
    warnings.simplefilter(action='ignore', category=FutureWarning)

    inicio = time.time()
    x = 0
    y = 0
    nomes = pd.Series()
    urls = pd.Series()
    formato = pd.Series()
    descricao = pd.Series()
    nomes2 = pd.Series()
    urls2 = pd.Series()
    formato2 = pd.Series()
    descricao2 = pd.Series()
    controle = 0
    vazio = True
    none = "None"
    df_final = pd.DataFrame()
    result = False
    result2=False

    for palavra in tags_final:
        print(palavra)
        filtro = {'query': 'name:' + palavra}
        filtro2 = {'query': 'description:' + palavra}

        # Consumindo dados do ckan, de acordo com o termo
        api = requests.get('http://dados.gov.br/api/3/action/resource_search', params=filtro)
        api2 = requests.get('http://dados.gov.br/api/3/action/resource_search', params=filtro2)
        print(filtro)
        repos = json.loads(api.text)
        repos2 = json.loads(api2.text)

        # Preparando os atributos mais importantes

        # Criando 3 séries de dados: "nomes", "urls" e "formato"
        if repos['result']['count'] > 0:
            vazio = False
            for resultado in repos['result']['results']:
                nomes = nomes.set_value(x, repos['result']['results'][x]['name'])
                urls = urls.set_value(x, repos['result']['results'][x]['url'])
                formato = formato.set_value(x, repos['result']['results'][x]['format'])
                descricao = descricao.set_value(x, repos['result']['results'][x]['description'])
                x = x + 1

        if repos2['result']['count'] > 0:
            vazio = False
            for resultado in repos2['result']['results']:
                nomes2 = nomes2.set_value(y, repos2['result']['results'][y]['name'])
                urls2 = urls2.set_value(y, repos2['result']['results'][y]['url'])
                formato2 = formato2.set_value(y, repos2['result']['results'][y]['format'])
                descricao2 = descricao2.set_value(y, repos2['result']['results'][y]['description'])
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
                            df = df.drop(index)
                    # if row["url"]== "http://dados.al.gov.br/dataset/d8f3ac16-6441-4f45-8c69-a2fc5a4ff8a6/resource/ab2effa7-68c7-4150-adba-fefaaccef1a8/download/quilombolascopia.png":
                    # print("aqui")
                    # Filtrando os dados com formato csv
                    # for index, row in df.iterrows():
                    # if row["formato"].lower() != "csv":
                    # df = df.drop(index)

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

    #df_final.to_csv("teste.txt")
    if df_final.empty:
        st.write('Não foi possível encontrar!')
    else:
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

        fim = time.time()

        print(controle)
        print('duracao: %f segundos' % (fim - inicio))


        df_final.to_csv('teste.txt')
        #st.dataframe(df_final["nome"])
        df_final = df_final.reset_index()
        st.table(df_final["nome"])