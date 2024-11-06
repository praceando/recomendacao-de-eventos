# Praceando - IA de Recomendação de Eventos

## Descrição

Este projeto implementa uma **IA de Recomendação de Eventos** para o aplicativo **Praceando**. O objetivo é sugerir eventos personalizados aos usuários com base em seus interesses e histórico de participação. Cada usuário recebe sugestões de eventos que podem ser do seu interesse, melhorando sua experiência no aplicativo.

## Funcionalidades

- **Sugestões Personalizadas**: Recomendação de eventos baseada nos favoritos e histórico de participação do usuário.
- **Preferências de Tags**: O usuário pode escolher tags de eventos (como “música” ou “meio ambiente”) para receber recomendações alinhadas aos seus interesses.
- **Aprendizado Contínuo**: Com o tempo, o sistema melhora as recomendações de acordo com as interações do usuário.

## Tecnologias Usadas

- **Python** para desenvolvimento do modelo
- **Flask** para a criação da API de recomendação
- **PostgreSQL** como banco de dados para armazenar dados de eventos e usuários
- **scikit-learn** com o algoritmo k-NN para encontrar eventos semelhantes

## Como Funciona

O sistema usa o histórico de participação e as preferências de tags do usuário para recomendar novos eventos. Com base no **algoritmo k-NN**, ele identifica eventos semelhantes e sugere os mais relevantes para o usuário.

## Como Executar

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/praceando/praceando-recommendation.git
   cd praceando-recommendation
   ```

2. **Configuração do Banco de Dados**: Configure o link de conexão no arquivo `.env`.

3. **Instale as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a Aplicação**:
   ```bash
   python app.py
   ```

5. **Obter Recomendações**:
   Acesse o endpoint `/recomendation/<id_usuario>/` no navegador ou via cURL, substituindo `<id_usuario>` pelo ID do usuário.
