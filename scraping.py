import os  # Importa o módulo os para manipulação de funcionalidades dependentes do sistema operacional.
import requests  # Importa o módulo requests para fazer requisições HTTP.
from bs4 import BeautifulSoup  # Importa a classe BeautifulSoup do módulo bs4 para fazer parsing de HTML.
from urllib.parse import urljoin  # Importa a função urljoin do módulo urllib.parse para manipulação de URLs.
import pickle  # Importa o módulo pickle para serialização e desserialização de objetos Python.
from concurrent.futures import ThreadPoolExecutor  # Importa a classe ThreadPoolExecutor do módulo concurrent.futures para execução concorrente.

def baixar_imagens():  # Define a função baixar_imagens.
    # Crie um diretório para salvar as imagens
    if not os.path.exists('pokemons_img'):  # Verifica se o diretório 'pokemons_img' não existe.
        os.makedirs('pokemons_img')  # Cria o diretório 'pokemons_img'.

        url = 'https://pokemondb.net/pokedex/shiny'  # URL do site contendo as imagens dos Pokémon shiny.
        headers = {  # Define os cabeçalhos HTTP para simular um navegador.
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }

        try:  # Inicia um bloco try-except para tratamento de exceções.
            resposta = requests.get(url, headers=headers)  # Envia uma requisição GET para a URL especificada.
            resposta.raise_for_status()  # Verifica se houve um erro na requisição HTTP.

            bs = BeautifulSoup(resposta.text, 'html.parser')  # Cria um objeto BeautifulSoup para fazer parsing do conteúdo HTML.

            # Encontrar todos os links <img> com a classe "shinydex-sprite-shiny"
            imagens = bs.find_all('img', class_='shinydex-sprite-shiny')  # Encontra todas as tags <img> com a classe especificada.

            # Lista para armazenar os caminhos das imagens
            image_paths = []  # Inicializa uma lista vazia para armazenar os caminhos das imagens baixadas.

            # Função para baixar uma imagem e adicionar à lista
            def baixar_e_adicionar(img_tag):  # Define a função local baixar_e_adicionar.
                caminho = img_tag['src']  # Obtém o atributo 'src' da tag <img>, que contém o URL da imagem.
                img_url = urljoin(url, caminho)  # Combina o URL base com o caminho relativo da imagem para obter o URL completo.
                local_path = os.path.join('pokemons_img', os.path.basename(img_url))  # Gera o caminho local onde a imagem será salva.

                with open(local_path, 'wb') as img_file:  # Abre o arquivo para escrita em modo binário.
                    img_data = requests.get(img_url).content  # Faz o download dos dados da imagem.
                    img_file.write(img_data)  # Escreve os dados da imagem no arquivo.

                # Adicionar o caminho da imagem à lista
                image_paths.append(local_path)  # Adiciona o caminho da imagem à lista image_paths.

            # Usar ThreadPoolExecutor para baixar imagens de forma concorrente
            with ThreadPoolExecutor() as executor:  # Cria um ThreadPoolExecutor.
                executor.map(baixar_e_adicionar, imagens)  # Mapeia a função baixar_e_adicionar para cada imagem na lista imagens e executa em paralelo.

            # Verificar se foram baixadas imagens
            if not image_paths:  # Se a lista image_paths estiver vazia.
                print("Erro: Não foi possível encontrar imagens de Pokémons.")
                return None  # Retorna None indicando falha.

            # Criar o diretório 'pokemons' se não existir
            if not os.path.exists('pokemons'):  # Verifica se o diretório 'pokemons' não existe.
                os.makedirs('pokemons')  # Cria o diretório 'pokemons'.

            # Salvar os caminhos das imagens em um arquivo pickle
            with open(os.path.join('pokemons', 'image_paths.pkl'), 'wb') as file:  # Abre o arquivo para escrita em modo binário.
                pickle.dump(image_paths, file)  # Serializa a lista image_paths e salva no arquivo.

            return image_paths  # Retorna a lista de caminhos das imagens.

        except requests.exceptions.RequestException as e:  # Captura exceções relacionadas a requisições HTTP.
            print(f"Erro ao acessar o site: {e}")  # Exibe a mensagem de erro.
            return None  # Retorna None indicando falha.

def obter_caminhos_imagens():  # Define a função obter_caminhos_imagens.
    image_paths_file = os.path.join('pokemons', 'image_paths.pkl')  # Define o caminho do arquivo que contém os caminhos das imagens.

    if os.path.exists(image_paths_file):  # Verifica se o arquivo existe.
        with open(image_paths_file, 'rb') as file:  # Abre o arquivo para leitura em modo binário.
            image_paths = pickle.load(file)  # Desserializa os dados do arquivo e carrega na lista image_paths.
            return image_paths  # Retorna a lista de caminhos das imagens.

    return None  # Retorna None se o arquivo não existir.

def realizar_scraping_e_baixar_imagens():  # Define a função realizar_scraping_e_baixar_imagens.
    image_paths = baixar_imagens()  # Chama a função baixar_imagens para fazer o scraping e baixar as imagens.
    return image_paths  # Retorna a lista de caminhos das imagens.

if __name__ == "__main__":  # Verifica se o script está sendo executado diretamente.
    image_paths = realizar_scraping_e_baixar_imagens()  # Chama a função principal realizar_scraping_e_baixar_imagens.
