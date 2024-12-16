import yaml
import os
from google import genai
from google.genai import types
from fastapi import HTTPException
from dotenv import load_dotenv
from utils.dataprep import GetMatchStats
from fastapi import APIRouter
from models.player_profile import PlayerProfileModel, LLMModel, LLMResponse
from statsbombpy import sb

router = APIRouter()

# Tentar carregar as variáveis de ambiente do arquivo .env, se não existir, configurar manualmente
ENV_PATH = os.path.abspath(os.path.join('..', '.env'))


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


def generate_player_profile(match_id: int, player_name: str) -> str:
    events = sb.events(match_id=match_id)
    player_events = events[events['player'] == player_name]
    stats = {
        "Jogador": player_name,
        "Passes Completos": player_events[
            (player_events['type'] == 'Pass') & (
                player_events['pass_outcome'].isna())
        ].shape[0],
        "Tentativas de Passes": player_events[player_events['type'] == 'Pass'].shape[0],
        "Chutes": player_events[player_events['type'] == 'Shot'].shape[0],
        "Chutes no Alvo": player_events[
            (player_events['type'] == 'Shot') & (
                player_events['shot_outcome'] == 'On Target')
        ].shape[0],
        "Faltas Cometidas": player_events[player_events['type'] == 'Foul Committed'].shape[0],
        "Faltas Sofridas": player_events[player_events['type'] == 'Foul Won'].shape[0],
        "Contestações de Bola": player_events[player_events['type'] == 'Tackle'].shape[0],
        "Interceptações": player_events[player_events['type'] == 'Interception'].shape[0],
        "Dribles Completados": player_events[
            (player_events['type'] == 'Dribble') & (
                player_events['dribble_outcome'] == 'Complete')
        ].shape[0],
        "Tentativas de Dribles": player_events[player_events['type'] == 'Dribble'].shape[0],
        "Gols (exceto pênaltis)": player_events[
            (player_events['type'] == 'Shot') &
            (player_events['shot_outcome'] == 'Goal') &
            (player_events['shot_type'] != 'Penalty')
        ].shape[0],
        "Gols de Pênalti": player_events[
            (player_events['type'] == 'Shot') &
            (player_events['shot_outcome'] == 'Goal') &
            (player_events['shot_type'] == 'Penalty')
        ].shape[0],
        "Recuperações de Bola": player_events[player_events['type'] == 'Ball Recovery'].shape[0],
        "Bloqueios": player_events[player_events['type'] == 'Block'].shape[0],
        "Paralisações por Lesão": player_events[player_events['type'] == 'Injury Stoppage'].shape[0],
        "Perda de Controle": player_events[player_events['type'] == 'Miscontrol'].shape[0],
        "Cartões Amarelos": player_events[
            (player_events['type'] == 'Foul Committed') &
            (player_events['foul_committed_card'].eq(
                'Yellow Card') if 'foul_committed_card' in player_events else False)
        ].shape[0],
        "Cartões Vermelhos": player_events[
            (player_events['type'] == 'Foul Committed') &
            (player_events['foul_committed_card'].eq(
                'Red Card') if 'foul_committed_card' in player_events else False)
        ].shape[0]
    }
    player_stats_yaml = yaml_conversion(stats)

    events = GetMatchStats(match_id=match_id).get_events()

    events_yaml = yaml_conversion(events)

    prompt = (f'''
                Elabore um resumo envolvente e informativo do jogador selecionado, em português, através do conteúdo dos YAML fornecidos:
                        - Player_stats: {player_stats_yaml} - contêm informações sobre as estatísticas do jogador na partida. Como: passes completos,
                        tentativas de passes, chutes, chutes no alvo, faltas cometidas, faltas sofridas, contestações de bola, interceptações, dribles completados,
                        tentativas de dribles, gols (exceto pênaltis), gols de pênalti, recuperações de bola, bloqueios, cartões amarelos, cartões vermelhos,
                        paralisações por lesão, perda de controle.
                        - Events: {events_yaml} - contêm informações sobre os eventos gerais da partida, envolvendo todos os jogadores.
                        Com a combinação das estatísticas do jogador e dos eventos da partida, você irá traçar o perfil do jogador na partida.
                        Utilize apenas as informações fornecidas, sem fazer suposições ou preencher lacunas, como por exemplo adivinhar a ordem dos eventos da partida.
                        Não use termos como de acordo com os dados que me foram fornecidos, ou algo do tipo.
                        O objetivo é criar um texto cativante e acessível, destacando os principais acontecimentos e aspectos interessantes do jogador na partida.
                        O resumo deve ter no máximo 250 palavras e ser escrito como um comentarista esportivo.
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


@router.post('/player_profile')
async def player_profile(request: PlayerProfileModel) -> LLMResponse:
    try:
        response = generate_player_profile(
            match_id=request.match_id,
            player_name=request.player_name
        )

        response_text = LLMModel(message=response)
        return LLMResponse(assistant=response_text.message)

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
