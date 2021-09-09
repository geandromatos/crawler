#bibliotecas necessárias para rodar o crawler
from selenium import webdriver
import urllib3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pathlib
import time


#cabeçalho para parecer humano
session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_9_5)'
           'AppleWebkit 537.36 (KHTML, like Gecko) Chrome',
           'Accept': 'text/html,applocation/xhtml+xml,application/xml;'
           'q=0.9,image/webp,*/*;q=0.8'}

url_cabecalho = 'https://www.whatismybrowser.com/'\
    'developers/what-http-headers-is-my-browser-sending'
req = session.get(url_cabecalho, headers = headers)


#função para remover tags
def tag(codigoJS):
    #"counter_simb" é inicializado em 0 e possui a função de verificar 
    #qual é o indíce do 1º elemento que aparece na linha de código corrente, caso ela seja um caso onde : "           a = b"
    counter_simb = 0 
    #"counter_tag" é inicializado em 0 e possui a função de verificar 
    #em que momento o símbolo ">" aparece na linha de código corrente
    counter_tag = 0
    #Se o código corrente for diferente de "\n", então a execução continua normalmente
    if codigoJS != '\n':
        #Se o primeiro elemento do código corrente for igual a "\n", " " e "\t",
        #então procura-se o primeiro elemento válido do código
        if codigoJS[0] == '\n' or codigoJS[0] == ' ' or codigoJS[0] == '\t':
            #Um laço percorre o código a procura do primeiro elemento válido
            for simbolo in codigoJS:
                if simbolo != '\n' or simbolo != ' ' or codigoJS[0] != '\t':
                    #Caso um elemento válido seja encontrado então a variável "counter_simb" é incrementada
                    #e o laço é interrompido
                    counter_simb += 1
                    break
                #"counter_simb" é incrementada e representa o índice do elemento corrente 
                counter_simb += 1
        #Se o elemento corrente for igual a "<", então procura-se pelo símbolo ">"    
        if codigoJS[counter_simb] == '<':
            #Um laço percorre o código em busca do símbolo ">"    
            for i in codigoJS:
                #Se o elemento corrente for igual a ">" retira-se todos os elementos que existem entre "<" e ">", 
                #Incluindo os próprios símbolos
                if i == '>':
                    counter_tag += 1
                    codigoJS = codigoJS.replace(codigoJS[0:counter_tag], '')
                    #Agora a execução busca tirar a tag localizada no final do código
                    if len(codigoJS) != 0:
                        #"c" recebe o comprimento do código -1, devido ao fato da contagem de elementos iniciar sempre em 0
                        c = len(codigoJS) - 1
                    else:
                        #Caso o comprimento do código seja igual a 0, c recebe apenas o comprimento, sem a 
                        #operação: comprimento -1
                        c = len(codigoJS) 
                    if codigoJS[c] == '>':
                        #"a" recebe "c" e possui como função controlar o laço que anda do final ao início do código
                        a = c
                        #Um laço percorre o código do fim ao início
                        while a > 0:
                            #Se o elemento corrente for igual a "<" então retira-se todos os elementos que existem
                            #entre "<" e ">", incluindo os próprios símbolos
                            if codigoJS[a] == '<': 
                                c +=1
                                codigoJS = codigoJS.replace(codigoJS[a:c], '') + '\n'
                                #Retiram-se também os símbolos "<!--" e "-->" do código
                                codigoJS = re.sub('<!--', '', str(codigoJS))
                                codigoJS = re.sub('-->', '', str(codigoJS))
                                #O código sem tags é retornado
                                return codigoJS
                            #O contador "a" é decrementado até que se encontre o símbolo "<"
                            a -= 1 
                #"counter_tag" é incrementada até o símbolo ">" ser encontrado
                counter_tag += 1
        else:
            #Se o 1º elemento encontrado no código não for igual a "<", então o código é retornado
            return codigoJS
    else:
        #Se o código não for diferente de "\n", então o código é retornado
        return codigoJS


#função que recebe a URL da página inicial a ser investigada
#e o nível de profundidade que será alcançado por meio dos links encontrados
def crawl(urls, profundidade, contadorURLs):
    #conjunto que armazena as URLs dos links das páginas que não permitem a entrada do crawler
    codigos_bloqueados = set()
    caminho_url_erro = '/crawler/urls_que_deram_erro/' + 'urls_erros' + '.txt' 
    contador_nome_site = 0
    with open(caminho_url_erro, 'w') as file_object:
        file_object.write("URLS que deram erro\n\n" + str(codigos_bloqueados) + "\n\n" )

    for site in urls:
        #conjunto que armazena as URLs dos códigos javascript externos encontrados
        codigos_javascript = set()
        #conjunto que armazena as URLs dos links das páginas a serem percorridas
        novas_paginas = set()
        #conjunto que armazena as URLs bloqueadas
        codigos_bloqueados = set()
        paginas = []
        paginas.append(site)
        #código para desativar os avisos warnings  
        nome_url = paginas[0]
        nome_url = nome_url.split('//')[1]           
        dir = '/crawler/ofuscados/' + str(nome_url)
        os.mkdir(dir)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #para usar o selenium ->browser = webdriver.Firefox()
        contador_nome_site_2 = 0
        #laço que controla a profundidade alcançada pelo crawler
        for _ in range(profundidade):
            http = urllib3.PoolManager()
            #laço que percorre as páginas encontradas por meio da busca de links href
            for pagina in paginas:
                #por meio da biblioteca urllib3, obtemos o conteúdo da página
                try:
                    #se nenhum erro ocorrer, o conteúdo é requisitado com sucesso
                    dados_pagina = http.request('GET', pagina)
                    #para usar o selenium ->browser.get(pagina)
                    #time.sleep(3)
                except:
                    #se não, a execução avança para a próxima url:
                    if pagina == listapaginas[0]:
                        continue
                    else:
                        codigos_bloqueados.add(pagina)
                        continue

                #o contador para a quantidade de códigos javascript externos é inicializado
                contador = 0
                textJS = ''
                #por meio da biblioteca BeautifulSoup, o conteúdo da página é analisado pelo parser lxml
                sopa = BeautifulSoup(dados_pagina.data, 'lxml')
                #para usar o selenium -> sopa = BeautifulSoup(browser.page_source, 'lxml')
                #são extraído todos os códigos com a tag "script"
                links_srcript = sopa.find_all("script")
                script_in_line = sopa.find_all(type="text/javascript")
                #Caso o crawler seja bloqueado
                if links_srcript == [] and script_in_line == []:
                    print('Nenhum código javascript encontrado no link: ' + str(pagina) + '\n')
                    codigos_bloqueados.add(pagina)

                #são removidas as tags "script"
                for i in script_in_line:
                    i = str(i.string) + '\n'
                    i = re.sub(r"N"r"o"r"n"r"e", '', str(i))
                    i = re.sub('<!--', '', str(i))
                    i = re.sub('-->', '', str(i))
                    textJS += str(i)

                #são extraído todos os códigos com a tag "a"
                links_href = sopa.find_all('a')
                #o nome do arquivo é salvo a partir do nome da página,
                #que é tratada caso comece com http
                if pagina[0:4] == 'http':
                    contador_nome_site+=1
                    pagina_nome = ''
                    if contador_nome_site_2 == 0:
                        pagina_nome += 'main_' + str(contador_nome_site)
                    else:
                        pagina_nome += 'dependencies_' + str(contador_nome_site)
                    contador_nome_site_2 += 1
            
            
                #o arquivo é salvo com extensão .js   
                filename = dir + '/' + str(pagina_nome) + '.js' 

                #o arquivo onde os dados serão salvos é criado, 
                #inicialmente salvando o códigos javascript in-line
                try:
                    with open(filename, 'w' ,encoding='utf-8', errors='ignore') as file_object:
                        file_object.write("//site:" + str(pagina) + "\n\n" + "//Tipo: javascript in-line\n\n" + str(textJS) + "\n\n" + "//Tipo: javascript externo\n\n")
                except:
                    codigos_bloqueados.add(pagina)
                    continue
                #laço que percorre os links srcripts encontrados                       
                for link_src in links_srcript:
                
                    #se a tag "src" existir nos atributos do link, 
                    #então a URL contida na tag "src" é extraída
                    if('src' in link_src.attrs): 
                        #caso alguma URL esteja incompleta, ela passa por um tratamento
                        #para se tornar completa
                        url_src  =  urljoin(pagina, str(link_src.get('src')))                    
                        url_src2 = urljoin(pagina, link_src.get('src'))
                        #se existir "'" na URL extraída, ela é considerada inválida
                        if url_src.find("'") != -1:
                            continue

                        #tratamento para evitar links internos da própria página
                        url_src = url_src.split('#')[0]
                        url_src2 = url_src2.split('#')[0]

                        #se a URL iniciar com "http"
                        if url_src[0:4] == 'http':
                            #se nenhum erro ocorrer ao carregar a
                            #página endereçada pela URL:
                            try:
                                #se for possível ter o conteúdo da página, então 
                                #a URL é adicionada ao conjunto dos codigos_javascript
                                if requests.get(url_src2):
                                    codigos_javascript.add(url_src)
                                    #o conteúdo da página é salvo na variável textoJs2,
                                    #incrementa-se o contador links de javascripts externos
                                    if url_src2 in codigos_javascript:
                                        url_src2 = requests.get(url_src2)
                                        textoJs2 = url_src2.text
                                        textoJs2 = tag(textoJs2)
                                        textoJs2 = re.sub(r"N"r"o"r"n"r"e", '', str(textoJs2))
                                        contador = contador + 1
                                        #print(contador)
                                        #print(url_src)
                                        #faz-se a indexização do conteúdo no arquivo.js, salvando os códigos javascript externos 
                                        with open(filename, 'a') as file_object:
                                            file_object.write(str(textoJs2) + "\n\n")

                            #caso algum erro aconteça, a URL é ignorada
                            except:
                                codigos_bloqueados.add(url_src)
                                continue
                    
                #após serem rastrados os links "src", 
                #os links para outras páginas são buscados 
                for link_href in links_href:
                    if('href' in link_href.attrs):
                        #intervalo de 3 segundos no carregamentos de páginas
                        #time.sleep(3)
                    
                        #caso alguma URL esteja incompleta, ela passa por um tratamento
                        #para se tornar completa
                        url_href = urljoin(pagina, str(link_href.get('href')))

                        #se existir "'" na URL extraída, ela é considerada inválida
                        if url_href.find("'") != -1:
                            continue 

                        #tratamento para evitar links internos da própria página
                        url_href = url_href.split('#')[0]

                        #se a URL iniciar com "http"
                        if url_href[0:4] == 'http':
                            #o processo pausa quando a quantidade de páginas encontradas for 100.000
                            if len(novas_paginas) >= 100.000:
                                break
                            try:
                                novas_paginas.add(url_href)
                            except:
                                continue
                                
                #as novas páginas encontradas substituem as páginas percorridas anteriormente,
                #dando continuidade ao laço
                paginas = novas_paginas
                contadorURLs += 1

        print('quantidade de páginas que não foi possível obter o conteúdo:' + str(len(codigos_bloqueados)))
        print('você pode vizualizar as páginas que não foram possível obter o conteúdo na pasta: urls_que_deram_erro')
        with open(caminho_url_erro, 'a') as file_object:
            file_object.write("\n\n" + str(codigos_bloqueados) + "\n\n" )

    return contadorURLs


#inserção da primeira URL a ser investigada
#Apenas uma URL deve ser inserida
URL = ''

listapaginas = []
while len(listapaginas) == 0:
    print('---------------------------------------')
    URL = input('Digite uma URL: ') 
    if URL[0:4] != 'http':
        print('\nEntrada inválida :(\n')
    else:
        print("\nA profundidade para o crawler deve ser sempre maior que 1:\n")
        print("Profundidade = 2 --> 396 links")
        print("Profundidade = 3 --> 20.000 links")
        print("Profundidade = 4 --> 1.000.000 links\n")
        profundidade = input('Digite a profundidade que deseja: ') 
        profundidade = int(profundidade)
        if profundidade == 1 or profundidade  == 2 or profundidade  == 3 or profundidade  == 4 or profundidade == 5 or profundidade  == 6 or profundidade  == 7 or profundidade  == 8 or profundidade == 9:
            print('\nObrigado! Agora o crawler está trabalhando...\n')
            listapaginas.append(URL)
        else:
            print('\nEntrada inválida :(\n')

#chama a função responsável pela investigação da página
#Profundidade sempre deverá ser maior que 1!!!!
#-------------------------------------------------
#Profundidade = 2 --> 396 links
#Profundidade = 3 --> 20.000 links
#Profundidade = 4 --> 1.000.000 links
contadorURLs = 0
verificador = crawl(listapaginas, profundidade, contadorURLs)
if verificador != 0:
    print('Crawlagem finalizada!! Agora pode desofuscar :)')