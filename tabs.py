import streamlit as st
import pandas as pd
import requests
from statsbombpy import sb
from mplsoccer import Pitch
from requests.exceptions import RequestException

SUMMARY_URL = 'http://localhost:8000/summary/match_summary'
PROFILE_URL = 'http://localhost:8000/profile/player_profile'
ERROR_MESSAGE = 'Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente.'


def tab_overview(mytab):
    '''
    Função que cria a aba de visão geral da partida e narração.
    '''
    with mytab:
        st.title('Visão Geral da Partida :soccer:')
        json_selected_match_info = st.session_state['json_selected_match_info']

        col1, col2 = st.columns(2)
        col1.markdown("### Competição")
        col1.write(f"{json_selected_match_info['competition_name']}")
        col1.markdown("### Data da Partida")
        col1.write(f"{json_selected_match_info['match_date']}")
        col2.markdown("### Time da Casa")
        col2.write(f"{json_selected_match_info['home_team_name']}")
        col2.markdown("### Time Visitante")
        col2.write(f"{json_selected_match_info['away_team_name']}")
        col3, col4 = st.columns(2)
        home_team = json_selected_match_info['home_team_name']
        away_team = json_selected_match_info['away_team_name']
        home_score = json_selected_match_info['home_score']
        away_score = json_selected_match_info['away_score']
        col3.markdown("### Resultado")
        col3.write(f"{home_team} {home_score} x {away_score} {away_team}")
        col4.markdown("### Estádio")
        col4.write(json_selected_match_info['stadium_name'])

        st.markdown("## Narração da Partida:studio_microphone:")
        if st.button('Gerar Narração'):
            if (json_selected_match_info and st.session_state['selected_match_id']) is not None:
                with st.spinner('Gerando narração sensacional...'):
                    try:
                        response = requests.post(
                            SUMMARY_URL,
                            json={'match_id': int(st.session_state['selected_match_id']),
                                  'match_info': str(json_selected_match_info)}
                        )
                        response.raise_for_status()

                        summary = response.json().get('assistant', ERROR_MESSAGE)

                        st.markdown(
                            f'<div style="text-align: justify;">{summary}</div>', unsafe_allow_html=True)
                    except RequestException as e:
                        error_message = f'Erro de conexão: {str(e)}'
                        st.error(error_message)


def player_stats_tab(mytab):
    '''
    Criação da aba de perfil do jogador.
    '''
    with mytab:
        st.title('Perfil do Jogador:mag_right:')
        st.write('Selecione um jogador para ter o resumo dele na partida')

        match_id = st.session_state['selected_match_id']

        events = sb.events(match_id=int(match_id))

        home_team = events[events['type'] == 'Starting XI'].iloc[0]['team']
        away_team = [team for team in events['team'].unique()
                     if team != home_team][0]

        home_team_events = events[events['team'] == home_team]
        away_team_events = events[events['team'] == away_team]

        home_team_players = home_team_events['player'].dropna().unique()
        away_team_players = away_team_events['player'].dropna().unique()

        all_players = list(
            set(home_team_players).union(set(away_team_players)))

        selected_player = st.selectbox(
            'Selecione um jogador', all_players, index=None)

        if st.button('Gerar Perfil do Jogador'):
            if (selected_player and match_id) is not None:
                with st.spinner('Gerando um perfil impecável...'):
                    try:
                        response = requests.post(
                            PROFILE_URL,
                            json={'match_id': match_id,
                                  'player_name': selected_player}
                        )
                        response.raise_for_status()

                        profile = response.json().get('assistant', ERROR_MESSAGE)

                        st.markdown(
                            f'<div style="text-align: justify;">{profile}</div>', unsafe_allow_html=True)
                    except RequestException as e:
                        error_message = f'Erro de conexão: {str(e)}'
                        st.error(error_message)


def pass_map_tab(mytab):
    '''
    Criação da aba de mapa de passe.
    '''
    with mytab:
        st.title('Mapa de Passe:man-running:')
        st.write(
            'Selecione um jogador para visualizar o mapa de passe dele na partida')

        match_id = st.session_state['selected_match_id']
        events = sb.events(match_id=match_id)

        home_team = events[events['type'] == 'Starting XI'].iloc[0]['team']
        away_team = [team for team in events['team'].unique()
                     if team != home_team][0]

        selected_team = st.selectbox(
            'Selecione time', [home_team, away_team], key='pass_team_selectbox', index=None)

        if selected_team is not None:

            events = sb.events(match_id=match_id)
            team_events = events[events['team'] == selected_team]
            players = team_events['player'].unique()
            players = players[~pd.isna(players)]
            selected_player = st.selectbox(
                'Selecione jogador', players, key='pass_player_selectbox', index=None)

            if selected_player is not None:
                with st.spinner('Carregando mapa de passes...'):
                    player_events = team_events[team_events['player']
                                                == selected_player]

                    pitch = Pitch(pitch_color='grass',
                                  line_color='white', line_zorder=2)
                    fig, ax = pitch.draw()

                    pass_events = player_events[player_events['type'] == 'Pass']

                    for _, event in pass_events.iterrows():
                        x = event['location'][0]
                        y = event['location'][1]
                        pass_end_location = event['pass_end_location']
                        x_end = pass_end_location[0]
                        y_end = pass_end_location[1]
                        pass_outcome = event['pass_outcome']

                        if pd.isna(pass_outcome):
                            color = 'blue'
                            alpha = 0.7
                            label = 'Passes Concluídos'
                        else:
                            color = 'red'
                            alpha = 0.5
                            label = 'Passes Incompletos'

                        pitch.arrows(x, y, x_end, y_end, color=color,
                                     alpha=alpha, ax=ax, width=2, label=label)

                    handles, labels = ax.get_legend_handles_labels()
                    by_label = dict(zip(labels, handles))
                    ax.legend(by_label.values(), by_label.keys(),
                              loc='upper left', fontsize='small')

                    st.pyplot(fig)
