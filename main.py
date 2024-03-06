import pickle
import random
from PySimpleGUI import Window, Button, Column, Image, Text, popup_auto_close
from PIL import Image as PILImage, UnidentifiedImageError
from io import BytesIO
from scraping import obter_caminhos_imagens
from time import sleep as sl

def enviar_estado_jogo_para_todos(jogada, pontuacao_servidor, pontuacao_cliente, imagem_selecionada, codigoBotao1, codigoBotao2, botaoAcertos, event_jogo, clientes_conectados):
    mensagem = pickle.dumps((jogada, pontuacao_servidor, pontuacao_cliente, imagem_selecionada, codigoBotao1, codigoBotao2, botaoAcertos, event_jogo))
    for cliente_socket in clientes_conectados:
        try:
            cliente_socket.sendall(mensagem)
        except Exception as e:
            print(f"Erro ao enviar mensagem para o cliente: {e}")
    print("Estado do jogo enviado para todos os clientes.")

def envia_dados_jogo(clientes_conectados, dados): # para enviar dados secundarios
    mensagem = pickle.dumps(str(dados))
    for cliente_socket in clientes_conectados:
        try:
            cliente_socket.sendall(mensagem)
        except Exception as e:
            print(f"Erro ao enviar mensagem para o cliente: {e}")
    print("Dados do jogo enviado pro cliente.")

def recebe_mensagem(cliente_socket): # para receber mensagens secundarias
    return pickle.loads(cliente_socket.recv(4096))

def verificar_fim_do_jogo(botaoAcertos):
    return len(botaoAcertos) == 16

def limpar_tela(window):
    global codigoBotao1, codigoBotao2, imagem_selecionada, botaoAcertos
    window['-IMAGEM1-'].update(data=b'')
    window['-IMAGEM2-'].update(data=b'')
    for codigo in range(1, 17):
        if codigo not in botaoAcertos:
            window[str(codigo)].update(disabled=False)
    codigoBotao1 = -1
    codigoBotao2 = -1
    imagem_selecionada = None

def exibir_espera_download():
    print("O Scraper está INICIANDO... AGUARDE")

def criar_cenario(jgdr):
    layout_grid = [
        [Button(f'{i * 4 + j}', key=f'{i * 4 + j}', size=(4, 2), image_filename='', image_size=(100, 100), pad=(5, 5)) for j in range(1, 5)]
        for i in range(4)
    ]
    layout_imagens = [
        [Image(filename='', key='-IMAGEM1-', size=(100, 100)), Image(filename='', key='-IMAGEM2-', size=(100, 100))]
    ]
    layout_servidor_cliente = [
        [   # colocado nome do jogador
            Text(f'Jogador 1: {"você" if jgdr == 1 else "servidor"}'),
            # pontos do jogador
            Text('', key='-JOGADOR1-'),
        ],
        [   # colocado nome do jogador
            Text(f'Jogador 2: {"você" if jgdr == 2 else "cliente"}'),
            # pontos do jogador
            Text('', key='-JOGADOR2-'),
        ],
        [Button('Resetar', key='reset')],
        # vez do jogador
        [Text('vez: '), Text('', key='-JOGADA-')],
    ]
    return [
        [
            Column(layout_servidor_cliente),
            Column(layout_grid),
            Column(layout_imagens),
        ]
    ]

def main_jogo(conn, jgdr):
    global codigoBotao1, codigoBotao2, imagem_selecionada, botaoAcertos
    
    if jgdr == 1: # if o jogador for o servidor
        
        image_paths = obter_caminhos_imagens()
        random.shuffle(image_paths)
        image_paths = image_paths[:8] * 2
        random.shuffle(image_paths)
        if not image_paths:
            print("Erro: Não foi possível carregar os caminhos das imagens.")
            return
        layout_jogo = criar_cenario(jgdr)
        window_jogo = Window('Sua Memória é Boa?', layout=layout_jogo, resizable=True)
        envia_dados_jogo([conn,], {'image_paths': image_paths})
        sl(1)
        
    if jgdr == 2: # if o jogador for o cliente
        
        print('esperando dados do servidor')
        dados = eval(recebe_mensagem(conn))
        
        image_paths = dados['image_paths']
        if not image_paths:
            print("Erro: Não foi possível carregar os caminhos das imagens.")
            return
        layout_jogo = criar_cenario(jgdr)
        window_jogo = Window('Sua Memória é Boa?', layout=layout_jogo, resizable=True)
        
    janela_aberta = True
    imagem_selecionada = None
    imagem1_key = '-IMAGEM1-'
    imagem2_key = '-IMAGEM2-'
    codigoBotao1 = -1
    codigoBotao2 = -1
    pontuacao_cliente = 0
    pontuacao_servidor = 0
    jogada = 1
    botaoAcertos = []
    clientes_conectados = [conn,]
    jogada_prox = None
        
    try:
        window_jogo.read(timeout=0) # atualizar e mostrar a tela 
        
        # Inicia o jogo
        while janela_aberta:
            window_jogo['-JOGADA-'].update(str(jogada))
            window_jogo['-JOGADOR1-'].update(str(pontuacao_servidor))
            window_jogo['-JOGADOR2-'].update(str(pontuacao_cliente))
            window_jogo.read(timeout=0) # mostra informações dos jogadores e jogada
            
            if jogada != jgdr and jogada_prox != None and jogada_prox != jogada:
                jogada = jogada_prox # recebe jogada
                window_jogo.TKroot.after(1000, lambda: limpar_tela(window_jogo)) # limpa
                print('mudou vez de jogar, agora é', jogada) 
                jogada_prox = None # coloca como None para não mudar de forma atrasada a jogada
                                
            if jogada != jgdr: # se caso não for a vez de jogar

                print('esperando', 'cliente' if jgdr == 1 else 'servidor', 'jogar')
                
                dado = recebe_mensagem(conn) # espera o outro jogar
                if dado == 'RESET': # se caso o outro jogador tiver escolhido reset
                    return 'reset'
                elif dado == 'PERDEU': # se caso o outro jogador tiver ganhado
                    popup_auto_close('que pena, você perdeu')
                    break
                print('dado recebido', dado)
                print('jogador que deve jogar', jogada)
                # jogada_prox, pontuacao_servidor, pontuacao_cliente, imagem_selecionada, codigoBotao1, codigoBotao2, botaoAcertos, event_jogo = dado
                jogada_prox = dado[0]
                event_jogo = dado[-1]
                
            else: # se caso for a vez do jogador de jogar
                print('esperando input do usuario')
                event_jogo, values_jogo = window_jogo.read()
                
            if event_jogo in (None, 'EXIT'): # debug her !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                break
            
            elif event_jogo == 'reset': # se jogador tiver escolhido reset
                envia_dados_jogo(clientes_conectados, 'RESET')
                return 'reset'
            
            event_jogo = int(event_jogo) # event jogo tem que ser inteiro
            
            if event_jogo in range(1, 17):
                if codigoBotao1 == -1:
                    codigoBotao1 = event_jogo
                    window_jogo[str(event_jogo)].update(disabled=True)
                else:
                    codigoBotao2 = event_jogo
                    window_jogo[str(event_jogo)].update(disabled=True)
                if imagem_selecionada is None:
                    imagem_selecionada = event_jogo
                    imagem_path = image_paths[event_jogo - 1]
                    try:
                        with open(imagem_path, 'rb') as img_file:
                            PILImage.open(img_file).verify()
                        image_data = BytesIO()
                        PILImage.open(imagem_path).resize((100, 100)).save(image_data, format="PNG")
                        window_jogo[imagem1_key].update(data=image_data.getvalue())
                    except (UnidentifiedImageError, IOError) as e:
                        print(f"Erro ao abrir a imagem {imagem_path}: {e}")
                else:
                    for codigo in range(1, 17):
                        window_jogo[str(codigo)].update(disabled=True)
                    imagem_path = image_paths[event_jogo - 1]  # debug her !!!!!!!!!!!!!!!
                    try:
                        with open(imagem_path, 'rb') as img_file:
                            PILImage.open(img_file).verify()
                        image_data = BytesIO()
                        PILImage.open(imagem_path).resize((100, 100)).save(image_data, format="PNG")
                        window_jogo[imagem2_key].update(data=image_data.getvalue())
                    except (UnidentifiedImageError, IOError) as e:
                        print(f"Erro ao abrir a imagem {imagem_path}: {e}")
                    if imagem_selecionada is not None and image_paths[event_jogo - 1] == image_paths[imagem_selecionada - 1]:
                        
                        if jogada == 1:
                            pontuacao_servidor += 1
                        else:
                            pontuacao_cliente += 1
                        
                        print(f"\nPontuação: Cliente {pontuacao_cliente} - {pontuacao_servidor} Servidor")
                        botaoAcertos.append(codigoBotao1)
                        botaoAcertos.append(codigoBotao2)

                        window_jogo.read(timeout=0)
                        window_jogo.TKroot.after(1000, lambda: limpar_tela(window_jogo))
                        
            if verificar_fim_do_jogo(botaoAcertos):
                popup_auto_close('parabens, você ganhou') # mostra o popup caso ganhado
                envia_dados_jogo(clientes_conectados, 'PERDEU') # envia pro outro o resultado
                break
            
            if jogada == jgdr: # se caso for a vez do jogador
                print('usuario escolheu')
                if not (imagem_selecionada is not None and image_paths[event_jogo - 1] == image_paths[imagem_selecionada - 1]): # se caso tiver passado a vez
                    
                    print("Errou! As imagens não são iguais.")
                    if jogada == 1:
                        print("Servidor jogou, vez do cliente")
                        jogada = 2
                        print('mudando jogada para 2')
                    else:
                        print("Cliente jogou, vez do servidor")
                        jogada = 1
                        print('mudando jogada para 1')
                        
                    window_jogo.read(timeout=0)
                    window_jogo.TKroot.after(1000, lambda: limpar_tela(window_jogo))
                    print('limpando')
                    
                enviar_estado_jogo_para_todos(jogada, pontuacao_servidor, pontuacao_cliente, imagem_selecionada, codigoBotao1, codigoBotao2, botaoAcertos, event_jogo, clientes_conectados) # envia informações do jogo
                print('enviou mensagens pra outro jogador')
                window_jogo.read(timeout=0)
                sl(2)
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        window_jogo.close()
