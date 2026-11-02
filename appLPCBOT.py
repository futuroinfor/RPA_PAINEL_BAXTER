# -*- coding: utf-8 -*-
import os
import time
import logging
from sys import argv
import requests
import pyautogui as pa
import threading
import mss
from PIL import Image
import cv2
import numpy as np

pa.useImageNotFoundException()

listaParametros = {}
listaPaineis = {}

CAMINHO_ABSOLUTO = os.path.abspath('')
PATH_IMAGENS = os.path.join(CAMINHO_ABSOLUTO, "img")
PATH_CONFIGS = os.path.join(CAMINHO_ABSOLUTO, "configs")
PATH_LOGS = os.path.join(CAMINHO_ABSOLUTO, "logs")

if not os.path.exists(PATH_LOGS):
    os.makedirs(PATH_LOGS)

logging.basicConfig(
    level=logging.INFO, 
    filename=f"{PATH_LOGS}\\{listaParametros.get('hostPN', 'log')}.log", 
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"
)

paineis_multiplos = False


resultado_status = [
    {'status_1': None, 'monitor_1': None}, 
    {'status_2': None, 'monitor_2': None}
]



def buscarReferenciaMonitorada(painel: str):
    imagens_monitor = {}

    if not os.path.exists(PATH_IMAGENS):
        logging.error(f"A pasta de imagens não existe no diretório: {PATH_IMAGENS}")
        return imagens_monitor

    arquivos_reais = os.listdir(PATH_IMAGENS)
    mapa_arquivos_reais = {arq.lower(): arq for arq in arquivos_reais}

    nome_base = painel.strip().lower()
    nome_esperado_com_extensao = f"{nome_base}.png"
    
    arquivo_encontrado = None

    if nome_esperado_com_extensao in mapa_arquivos_reais:
        arquivo_encontrado = mapa_arquivos_reais[nome_esperado_com_extensao]
    elif f"{nome_esperado_com_extensao}.png" in mapa_arquivos_reais:
        arquivo_encontrado = mapa_arquivos_reais[f"{nome_esperado_com_extensao}.png"]
        logging.warning(f"Aviso: Arquivo com extensão duplicada detectado e corrigido: {arquivo_encontrado}")
    elif f"{nome_base}.png" in mapa_arquivos_reais:
        arquivo_encontrado = mapa_arquivos_reais[f"{nome_base}.png"]

    if arquivo_encontrado:
        caminho_final = os.path.join(PATH_IMAGENS, arquivo_encontrado)
        imagens_monitor[painel.strip()] = os.path.normpath(caminho_final)
    else:
        print(f"\n--- [ERRO] ARQUIVO NÃO ENCONTRADO PARA O PAINEL: '{painel}' ---")
        print(f"Buscado como: '{nome_esperado_com_extensao}'")
        print(f"Arquivos que atualmente existem na pasta '{PATH_IMAGENS}':")
        print(arquivos_reais if arquivos_reais else "[Pasta img está totalmente VAZIA]")
        print("-" * 50)
        
        imagens_monitor[painel.strip()] = os.path.normpath(os.path.join(PATH_IMAGENS, nome_esperado_com_extensao))

    return imagens_monitor

try:
    config_path = os.path.join(PATH_CONFIGS, "config.txt")
    with open(config_path, "r", encoding="utf-8") as fileconf:
        for linha in fileconf:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                chave, valor = linha.split('=', 1)
                listaParametros[chave.strip().lower()] = valor.strip()

    API_URL = listaParametros.get('url', '')
    HEADERS = {'Content-Type': 'application/json'}
    atraso = int(listaParametros.get('atrasonaexecucao', 0))
    hostPN  = listaParametros.get('hostpn', 'Desconhecido')
    pavimento  = listaParametros.get('pavimento', 'Desconhecido')
    secao  = listaParametros.get('secao', 'Desconhecido')
    paineis = [p.strip() for p in listaParametros.get('paineis', '').split(',') if p.strip()]
    descricao = listaParametros.get('descricao', 'Desconhecido')
    paineis_multiplos = len(paineis) > 1
    

    imagens_monitor_1 = buscarReferenciaMonitorada(paineis[0])
    paineis_config = {
                "Monitor_1": {
                    "imagens": imagens_monitor_1,
                    "id_monitor_mss": 1  
                }
    }

    if paineis_multiplos:
        imagens_monitor_2 = buscarReferenciaMonitorada(paineis[1])
        paineis_config["Monitor_2"] = {
                "imagens": imagens_monitor_2,
                "id_monitor_mss": 2  
        }
        
except Exception as error:
    logging.error(f"Arquivo de configuração incorreto: config.txt - {error}")
    raise

parar_monitoramento = threading.Event()
tentativa = 0

def checar_status_imagem_com_zoom(caminho_imagem, id_monitor, nome_thread):
    try:
        template = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")
            
        with mss.MSS() as sct:
            monitor_info = sct.monitors[id_monitor]
            sct_img = sct.grab(monitor_info)
            
            tela_np = np.array(sct_img)
            tela_gray = cv2.cvtColor(tela_np, cv2.COLOR_BGRA2GRAY)

        escalas = np.linspace(0.5, 1.0, 50)  
        
        melhor_confianca = 0.0
        limiar_confianca = 0.9  

        for escala in escalas:
            largura = int(template.shape[1] * escala)
            altura = int(template.shape[0] * escala)
            
            if largura > tela_gray.shape[1] or altura > tela_gray.shape[0] or largura < 10 or altura < 10:
                continue
                
            template_redimensionado = cv2.resize(template, (largura, altura), interpolation=cv2.INTER_AREA)

            resultado = cv2.matchTemplate(tela_gray, template_redimensionado, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(resultado)

            if max_val > melhor_confianca:
                melhor_confianca = max_val

            if melhor_confianca >= limiar_confianca:
                return 'OK'

        return 'OK' if melhor_confianca >= limiar_confianca else 'Erro'

    except Exception as e:
        return 'Erro'
    
def monitorar_tela(nome_monitor, config_painel):
    global tentativa
    nome_thread = threading.current_thread().name
    logging.info(f'[{nome_thread}] Iniciando monitoramento: {hostPN}')

    data_login = time.strftime('%Y-%m-%d %H:%M:%S')

    imgs = config_painel["imagens"]
    

    def checaStatus(ref: dict):  
        global resultado_status    
        
        for nome_painel, caminho_real in ref.items():
            status = checar_status_imagem_com_zoom(caminho_real, 1, nome_thread)
            monitor = nome_painel if status == 'OK' else None
            
            if status == 'Erro': 
                status = checar_status_imagem_com_zoom(caminho_real, 2, nome_thread)
                monitor = nome_painel if status == 'OK' else None
            
            if nome_thread == 'Thread-Painel-1':
                resultado_status[0].update({'status_1': status, 'monitor_1': monitor}) 

            if nome_thread == 'Thread-Painel-2':
                resultado_status[1].update({'status_2': status, 'monitor_2': monitor}) 

        return resultado_status

    
    while not parar_monitoramento.is_set():
        resultado_status = checaStatus(imgs)

        if resultado_status[0]['status_1'] == 'OK' or resultado_status[1]['status_2']  == 'OK' or tentativa > 3:
            dados = {
                'hostname': hostPN,
                'status_1': resultado_status[0],
                'status_2': resultado_status[1],
                'data_login': data_login,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'pavimento': pavimento,
                'secao': secao,
                'paineis': ','.join(paineis),
                'descricao': descricao
            }
            print(f'Em execução o monitoramento...: {dados["descricao"]}')
            
            if paineis_multiplos:
                print(f'Status 1: {resultado_status[0]["status_1"]} Status 2: {resultado_status[1]["status_2"]}')
            else:
                print(f'Status 1: {resultado_status[0]["status_1"]}')
            tentativa = 0
            try:
                resposta = requests.post(API_URL, json=dados, headers=HEADERS, timeout=5) 
                resposta.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f'[{nome_thread}] Erro de conexão com a API: {e}')
        else:
            tentativa += 1 
            if paineis_multiplos:
                print(f'.... tentativa: {tentativa} Status 1: {resultado_status[0]["status_1"]} Status 2: {resultado_status[1]["status_2"]}')
            else:
                print(f'.... tentativa: {tentativa} Status 1: {resultado_status[0]["status_1"]}')
        
        parar_monitoramento.wait(timeout=10)

if __name__ == '__main__':
    pa.sleep(atraso)
    logging.info('Iniciando sistema de monitoramento...')

    t1 = threading.Thread(target=monitorar_tela, args=("Monitor_1", paineis_config["Monitor_1"]), name="Thread-Painel-1")
    t1.daemon = True
    t1.start()

    if paineis_multiplos:
        t2 = threading.Thread(target=monitorar_tela, args=("Monitor_2", paineis_config["Monitor_2"]), name="Thread-Painel-2")
        t2.daemon = True
        t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('\nFinalizando monitoramento...')
        print("\nFinalizando monitoramento...")
        parar_monitoramento.set()
        t1.join()
        if len(paineis) > 1:
            t2.join()
