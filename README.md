
# Dashboard futebol com LLM

Projeto como parte do Assessment de Desenvolvimento de Data-Driven Apps com Python, essa aplicação consome os dados da API do StatsBomb e disponibiliza ao usuário interagir com esses dados de maneira dinâmica, incluindo: sumarização/narração de partida com LLM, análise do perfil do jogador com LLM, visão geral da partida e mapa de passes dos jogadores.




## Linguagens, Frameworks e Ferramentas usadas



![Python](https://img.shields.io/badge/Python-3.11.9-blue?style=for-the-badge&logo=python&logoColor=yellow) ![FastAPI](https://img.shields.io/badge/fastapi-0.115.6-%23009485?style=for-the-badge&logo=fastapi&logoColor=%23009485) ![Streamlit](https://img.shields.io/badge/streamlit-1.41.0-red?style=for-the-badge&logo=streamlit&logoColor=red) ![Mplsoccer](https://img.shields.io/badge/mplsoccer-1.4.0-green?style=for-the-badge) ![Gemini](https://img.shields.io/badge/gemini-1.5--flash-%234796E3?style=for-the-badge&logo=googlegemini&logoColor=%234796E3)



## Rodando localmente

Clone o projeto

```
  git clone https://github.com/Leticia-Infnet/leticia_abreu_DR3_AT_parte2.git
```

Entre no diretório do projeto

```
  cd leticia_abreu_DR3_AT_parte2
```

Instale as dependências

```
  pip install -r requirements.txt
```

Crie um arquivo .env contendo sua chave da API do Gemini, no formato abaixo:

GEMINI_API_KEY = SUA_API_KEY

Da raíz do projeto, vá para o diretório da API

```
  cd api
```

Ative o server

```
uvicorn --host 0.0.0.0 --port 8000 main:app --reload
```

Em outro terminal, da raíz do diretório, rode a aplicação streamlit

```
streamlit run main.py
```


## Documentação da API

#### Faz o resumo da partida selecionada

```
  POST summary/match_summary
```

| Parâmetro da requisição  | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `match_id` | `int` | **Obrigatório**. O id da partida selecionada |
| `match_info`|`string`|**Obrigatório**. String JSON contendo as informações gerais da partida

#### Faz o perfil do jogador selecionado

```
  POST profile/player_profile
```

| Parâmetro da requisição  | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `match_id`      | `int` | **Obrigatório**. O id da partida selecionada |
| `player_name` | `string`| **Obrigatório**. O nome completo do jogador selecionado|


