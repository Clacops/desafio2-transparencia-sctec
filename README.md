

# 📊 Desafio de Dados: Portal da Transparência - Governo Federal - Viagens a Serviço

Este projeto consiste de um exercício avaliativo baseado numa consultoria de dados contratada pelo governo e foi desenvolvida através da construção de um **Pipeline de ETL (Extração, Transformação e Carga)** e em uma **Análise Exploratória de Dados (EDA)** baseado nos dados dos gastos públicos com viagens a serviço publicados no portal da transparência nos  6 meses no ano de 2025.

O grande diferencial deste projeto de consultoria é a implementação da **Arquitetura Medallion (Medallion Architecture )**. Todo o fluxo de dados foi estruturado em **3 camadas lógicas: Raw, Silver e Gold** dentro de um banco de dados PostgreSQL, aplicando as melhores práticas de Engenharia de Dados para garantir rastreabilidade, qualidade e performance.
 
A partir destas etapas pode-se responder a insights de negócio, investigação e tomada de decisões com dados transformados e confiáveis.


## 📈 Principais Análises Realizadas
Considerações, insights e respostas as perguntas de negócio: 
As análises respondem as perguntas gerenciais que foram efetuadas no contexto da solicitação do projeto avaliativo na forma de desafio por tópicos com base nos dados ofertados em Drive assim tido como cópias do Portal da Transparência Pública - BR. 
As perguntas são:

1.	Os 5 órgãos com maior custo total?
Em ordem decrescente de valores (R$) obtivemos após analise: o Ministério da Justiça e Segurança Pública, o Ministério da Defesa, o Ministério da Educação, o Ministério do Meio Ambiente e Mudança do Clima e o Ministério da Previdência Social. Relevante salientar que os gastos do primeiro Ministério são três vezes superiores ao segundo elencado e mais de dez vezes maior que o último, sugerindo um olhar mais específico a estas despesas.

2.	Os 3 destinos com maior custo médio por viagem? 
A análise foi na realizada na superficialidade da questão devido a inexistência de parâmetros que definissem critérios de inclusão/exclusão de dados. A pergunta não leva em consideração o tempo de permanência e o número de dias e foi preciso ainda considerar cidades que receberam pelo menos 5 viagens para ter uma análise um pouco mais realista. Os resultados estão descritos como 3 cidades do interior dos estados do Brasil.

3.	A viagem de maior duração e seu custo total? 
Dada a amplitude da pergunta poderíamos objetivar respostas diferentes se não considerarmos dados publicados de cidades relacionadas a custo R$ 0 , o que pode ser explicado pela possível inconsistência dos dados (erros de preenchimento) ou outliers que dentro do contexto poderiam ser descartadas como valores insignificantes. Se não consideramos o custo R$ 0, obtivemos uma viagem com duração de 378 dias e custo total	de R$ 120.65,00. Ainda que este, seja um estudo experimental de desenvolvimento de aprendizado, cabe atentar para estas particularidades.

4.	Qual o tipo de pagamento com maior valor médio? 
O gráfico descreve o valor das diárias como sendo o maior valor médio se considerarmos os 3 itens e ainda a exclusão dos valores restituídos, o que caso nao ocoresse poderia inflar os resultados.

5.	Qual o meio de transporte mais usado nos trechos? 
Neste contexto utilizamos a camada gold para obter uma consulta refinada, com métricas e chaves que se cruzam e selecionadas objetivamente. Com o uso da tabela fato podemos ter acesso a dados de grande complexidade com acesso mais rápido.  
Se consideramos que as viagens podem ter mais de um meio de transporte e utilizarmos a premissa de analisar o "negócio", então o veículo oficial foi o meio de transporte de maior frequência de utilização.( n = 386.624)
Se ao invés disso, optássemos por uma auditoria, nossa abordagem seria na camada silver que garante que dados não se "perdem" pelo caminho.

6.	Qual UF de destino aparece em mais trechos? 
A UF de destino que aparece em mais trechos é 'São Paulo', com 82.722 trechos registrados, confirmando a premissa de que a capital (cidade de São Paulo) é um "hub" de  conexões de transporte aéreos e terrestres.

7.	Qual órgão pagou mais no total ? 
Diferentemente do órgão que teve mais custo (pergunta 1) o órgão que pagou mais no total foi o 'Fundo Nacional de Segurança Pública', com um gasto de R$ 278.481.047,89.

## 🏗️ As 3 Camadas da Arquitetura de Dados
O pipeline movimenta e refina os dados através das seguintes etapas:

1. **🥉 Camada Raw (Bronze):** O ponto de aterrissagem. Recebe os dados brutos importados diretamente dos arquivos originais, sem alterações, mantendo o histórico fiel da fonte.
2. **🥈 Camada Silver:** Onde a mágica acontece. Os dados são higienizados, as duplicatas são removidas, e a tipagem é corrigida (como a padronização de datas e a conversão de strings para valores monetários reais). Aqui também validamos a integridade relacional (Chaves Estrangeiras).
3. **🥇 Camada Gold:** A camada de negócio. Contém tabelas e gráficos fato gerenciais e agregadas, modeladas especificamente para responder a perguntas de negócio e alimentar as ferramentas de visualização de forma otimizada.

## 🛠️ Tecnologias Utilizadas
* **Linguagens:** Python 3.14 e SQL 
* **Banco de Dados:** PostgreSQL 17 
* **Bibliotecas de Manipulação:** Pandas, SQLAlchemy, psycopg2
* **Bibliotecas de Visualização:** Matplotlib, Seaborn
* **Ambiente e Segurança:** Jupyter Notebook, python-dotenv (ocultar senhas e credenciais)
* **Controle de Versão:** Git e GitHub

## 📁 Estrutura do Projeto
* **Dados Brutos (`.zip` / `.csv`):** Arquivos originais obtidos via Google Drive e descompactados localmente para alimentar o pipeline. (Ignorados no versionamento devido ao volume de dados).
* `0-criando_banco.sql`: Script SQL responsável por criar a estrutura física das 3 camadas (`raw`, `silver`, `gold`) e suas respectivas tabelas.
* `1_extrair.py`: Script Python responsável pela Extração (Extract) e carga inicial dos dados brutos dos arquivos `.csv` diretamente para a camada Raw (Bronze) do banco de dados.
* `2_transformar.py`: Script Python de ETL que consome a camada Raw, aplica as regras de negócio e limpeza, e carrega os dados estruturados na camada Silver.
* `3_analise.ipynb`: Jupyter Notebook consumindo a camada Gold para responder a perguntas de negócio com gráficos formatados no padrão pt-BR.
* `requirements.txt`: Lista de dependências do projeto.
* `.env`: Arquivo (ignorado no versionamento) contendo as variáveis de ambiente e credenciais do banco.


## 🚀 Como Executar o Projeto

Para reproduzir este pipeline de dados na sua máquina local, siga o passo a passo abaixo.

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
* **Python 3.10+**
* **PostgreSQL** (e uma interface como o pgAdmin)
* **Git**
* Uma IDE (recomendamos o **VS Code**)

### 2.Clonar o repositório:
Abra o terminal e faça o clone do projeto:
   ```bash
   git clone [https://github.com/Clacops/desafio2-transparencia-sctec.git]
   cd desafio2-transparencia-sctec
```
### 3. Organizar os Dados Brutos
Como os arquivos governamentais originais são muito pesados para o GitHub, você precisará adicioná-los manualmente:
1. Baixe os arquivos brutos (`.zip` ou `.csv`) fornecidos via Google Drive.
2. Descompacte-os e coloque os arquivos `.csv` dentro de uma pasta chamada `data/` na raiz do projeto.

### 4. Configurar as Variáveis de Ambiente
Para proteger suas credenciais, o projeto utiliza um arquivo `.env`. 
1. Crie um arquivo chamado exatamente `.env` na raiz do projeto.
2. Cole o conteúdo abaixo e preencha com as senhas do seu banco de dados PostgreSQL local:
```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=desafio2-transparencia-sctec
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

```
### 5.Instalar as Dependências
No terminal do VS Code, instale as bibliotecas rodando:
```powershell
pip install -r requirements.txt
```

### 6. Executar o Pipeline (Passo a Passo)
A execução deve seguir estritamente a ordem da Arquitetura Medallion:

* **Passo 6.1 - Banco de Dados:** Abra o seu pgAdmin, conecte-se ao seu servidor e rode o script `0-criando_banco.sql` para criar os schemas (Raw, Silver, Gold) e as tabelas vazias.
* **Passo 6.2 - Extração (Bronze):** No terminal do VS Code, rode o script de carga inicial:
  ```bash
  python 1_extrair.py
  ```
* **Passo 6.3 - Transformação (Silver):** Em seguida, rode o script de limpeza e regras de negócio:
  ```bash
  python 2_transformar.py
  ```
* **Passo 6.4 - Análise (Gold):** Abra o arquivo `3_analise.ipynb` no VS Code.
  * O Kernel Python deve estar selecionado no canto superior direito.
  * Clique em **"Run All" (Executar Tudo)**.
  * *Resultado:* tabelas gerenciais e gráficos finais salvos automaticamente 

