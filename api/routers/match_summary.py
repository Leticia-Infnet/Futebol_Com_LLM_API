import yaml
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastapi import APIRouter
from models.match_summary import MatchSummaryModel, LLMModel, LLMResponse
from utils.dataprep import GetMatchStats
from fastapi import HTTPException

router = APIRouter()

# Tentar carregar as variáveis de ambiente do arquivo .env, se não existir, configurar manualmente
ENV_PATH = os.path.abspath(os.path.join('..', '.env'))

print(ENV_PATH)


if os.getenv('GEMINI_API_KEY') is None:
    try:
        load_dotenv(dotenv_path=ENV_PATH,
                    override=True)
    except FileNotFoundError:
        print('Arquivo .env não encontrado. As variáveis de ambiente devem ser configuradas manualmente.')

# Configuração do cliente com a chave da API
client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY')
)


def yaml_conversion(data: dict) -> str:
    return yaml.dump(data, allow_unicode=True)


def generate_match_summary(match_id: int, match_info: str) -> str:
    lineups = GetMatchStats(match_id).get_lineups()
    events = GetMatchStats(match_id).get_events()
    player_stats = GetMatchStats(match_id).get_player_stats()
    lineups_yaml = yaml_conversion(lineups)
    match_info_yaml = yaml_conversion(match_info)
    events_yaml = yaml_conversion(events)
    player_stats_yaml = yaml_conversion(player_stats)

    prompt = (f'''
                Elabore um resumo envolvente e informativo do jogo descrito abaixo, em português, através do conteúdo dos YAML fornecidos:
                - Lineups: {lineups_yaml} - contêm informações sobre as escalações dos times
                - Match Info: {match_info_yaml} - contêm informações gerais da partida como data, estádio, times, placar, nome da competição.
                - Events: {events_yaml} - contêm informações sobre os eventos da partida passes, faltas cometidas, faltas sofridas, interceptações, recuperação de bola, dribles e suas localizações.
                - Player Stats: {player_stats_yaml} - contêm informações sobre os jogadores individuais com os jogadores e, junto com os eventos, irão dar a visão geral da partida.
                Utilize apenas as informações fornecidas, sem fazer suposições ou preencher lacunas, como por exemplo adivinhar a ordem dos eventos da partida.
                O objetivo é criar um texto cativante e acessível, destacando os principais acontecimentos e aspectos interessantes da partida.
                O resumo deve ter no máximo 250 palavras e ser escrito como um comentarista esportivo, com o tom escolhido pelo usuário.
                Mencione a data da partida explicitamente, sem utilizar termos como 'hoje'.
                Não use termos como de acordo com os dados que me foram fornecidos, ou algo do tipo.
                Focalize os momentos-chave do jogo, não entre em detalhes excessivos sobre cada jogador.
                ''')

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
            top_p=0.95,
            top_k=40
        ))

    return response.text


@router.post('/match_summary')
async def match_summary(request: MatchSummaryModel) -> LLMResponse:
    try:
        response = generate_match_summary(
            match_id=request.match_id,
            match_info=request.match_info
        )

        response_text = LLMModel(message=response)
        return LLMResponse(assistant=response_text.message)

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
