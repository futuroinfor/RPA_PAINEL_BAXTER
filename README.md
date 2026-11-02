# Monitoramento de Painéis
Essa automação faz parte de outra aplicação que juntas funciona como um centralizados de paineis da empresa,  
a funcionalidade desta Automação em Python é para informar para a API "a central" que os paineis esta Online ou Offline, 
Exemplo: Clínicos, Baxter (Monitoramento de Camas Hospitalares), Painel de Chamada, Totens, Grafana, etc.

## O que ela resolve
Antes: Quando tinha algum problema com o painel ou quando o computador reiniciava por motivos diversos a TI só ficava ciente do problema através de chamado ou ronda Técnica.
Depois: A automação em questão, gera uma requisição para outra aplicação API que tem um Dashboard com todos os paineis exibidos na sala da TI centralizado, avisando que tal painel esta offline.

## Funcionalidades
- Monitora e gera requisição para API informando que esta Online ou Offline

## Tecnologias
- Python 3.9.12
- PyAutoGUI
- PyGetWindow
- PyScreeze
- requests
- opencv
- numpy


## Como rodar
### 1. Clone o repositório
```bash
git clone https://github.com/futuroinfor/automacoes-rpa_painel.git
cd automacoes-rpa_painel
```
### 2. Crie e ative um ambiente virtual
Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
### 4. Execute
```bash
python appLPCBOT.py
```
## Estrutura do projeto
```
.
├── configs/
├── imgs/
├── appLPCBOT.py
├── requirements.txt
```
## Autor
Romilson J Tenorio
- LinkedIn: [seu-perfil](https://linkedin.com/in/romilsontenorio)
- E-mail: seu-email@exemplo.com
## Licença
Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
