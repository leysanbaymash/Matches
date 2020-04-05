import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

pd.options.display.max_columns = 20


# сводная таблица по матчам
def make_matches_df(teams):
    with open('germmatches', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    matches = []
    for i in range(57545, 57851):
        points1 = 0
        points2 = 0
        team1 = soup.find('tr', {'id': str(i)}).find('a').text
        team2 = soup.find('tr', {'id': str(i)}).find('td', {'class': 'rightalign'}).find('a').text
        score = soup.find('tr', {'id': str(i)}).find('td', {'class': 'score'}).find('a').text
        date = soup.find('tr', {'id': str(i)}).find('td', {'class': 'date'}).text
        if score != '':
            if int(score[0]) > int(score[2]):
                points1 = 3
            elif int(score[0]) < int(score[2]):
                points2 = 3
            else:
                points1 = 1
                points2 = 1
        teams.add(team1)
        matches.append({
            'team1': team1,
            'team2': team2,
            'team1_goals': (int(score[0]) if score != '' else 0),
            'team2_goals': (int(score[2]) if score != '' else 0),
            'date': date,
            'team1_points': points1,
            'team2_points': points2
        })
    matches_df =pd.DataFrame(matches)
    matches_df = matches_df[['team1', 'team2', 'team1_goals', 'team2_goals', 'date', 'team1_points', 'team2_points']]
    matches_df['date'] = pd.to_datetime(matches_df.date, format='%d.%m.%Y')
    return matches_df


def make_ranking_table(teams, matches_df):
    result = []
    for team in teams:
        points = (matches_df.loc[matches_df['team1'] == team]['team1_points'].sum() +
                  matches_df.loc[matches_df['team2'] == team]['team2_points'].sum())

        # количество сыгранных игр
        df_g1 = matches_df.loc[matches_df['team2'] == team][matches_df['date'] < '2020-03-13']
        df_g2 = matches_df.loc[matches_df['team1'] == team][matches_df['date'] < '2020-03-13']
        games_df = df_g1.merge(df_g2, how='outer')
        games = len(games_df.index)

        # количество побед
        df_w1 = matches_df.loc[matches_df['team2'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team2_points'] == 3]
        df_w2 = matches_df.loc[matches_df['team1'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team1_points'] == 3]
        wins = len(df_w1.merge(df_w2, how='outer').index)

        # количество игр, сыгранных в ничью
        df_d1 = matches_df.loc[matches_df['team2'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team2_points'] == 1]
        df_d2 = matches_df.loc[matches_df['team1'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team1_points'] == 1]
        draws = len(df_d1.merge(df_d2, how='outer').index)

        # количество проигрышей
        df_l1 = matches_df.loc[matches_df['team2'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team2_points'] == 0]
        df_l2 = matches_df.loc[matches_df['team1'] == team][matches_df['date'] < '2020-03-13'][
            matches_df['team1_points'] == 0]
        losses = len(df_l1.merge(df_l2, how='outer').index)

        # кол-во забитых мячей
        scored = matches_df.loc[matches_df['team1'] == team]['team1_goals'].sum() + \
                 matches_df.loc[matches_df['team2'] == team]['team2_goals'].sum()

        # кол-во пропущенных мячей
        conceded = matches_df.loc[matches_df['team1'] == team]['team2_goals'].sum() + \
                   matches_df.loc[matches_df['team2'] == team]['team1_goals'].sum()

        # разница голов
        goal_df = scored - conceded

        result.append({
            'Team_nm': team,
            'Games': games,
            'Wins': wins,
            'Draws': draws,
            'Losses': losses,
            'Goals': scored,
            'Goal_df': goal_df,
            'Points': points
        })

    result_df = pd.DataFrame(result)
    result_df = result_df[['Team_nm', 'Games', 'Wins', 'Draws', 'Losses', 'Goals', 'Goal_df', 'Points']]
    result_df = result_df.sort_values(by=['Points', 'Goal_df', 'Goals'], ascending=False)
    result_df.index = np.arange(1, 19)
    return result_df


def matches_by_team(team, matches_df, teams):
    if not (team in teams):
        return 'There is no such team participating in the championship'
    df_g1 = matches_df.loc[matches_df['team2'] == team]
    df_g2 = matches_df.loc[matches_df['team1'] == team]
    games_df = df_g1.merge(df_g2, how='outer')
    return games_df


def matches_by_date(date, matches_df):
    df = matches_df.loc[matches_df['date'] == date]
    if df.empty:
        return 'No matches on this date'
    return df


teams = set()
matches_df = make_matches_df(teams)
team = input('Which team match information do you want to receive?\n(Type a team name with a capital letter)\n')
print(matches_by_team(team, matches_df, teams))
date = input('\nWhich day match information do you want to receive?\nEnter date in format YYYY-MM-DD\n')
print(matches_by_date(date, matches_df))
choice = input('\nDo you want to see the ranking table?\n')
if choice.lower() == 'yes':
    print(make_ranking_table(teams, matches_df))
