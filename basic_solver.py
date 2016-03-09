
# Calculates OPR/DPR/CCWM
# For implementation details, see
# http://www.chiefdelphi.com/forums/showpost.php?p=484220&postcount=19

# M is n x n where n is # of teams
# s is n x 1 where n is # of teams
# solve [M][x]=[s] for [x]

# x is OPR and should be n x 1

import numpy as np
import requests

def _calculate_opr(parsed_matches, team_list, team_id_map):
    """
    Returns: a dict where
    key: a string representing a team number (Example: "254", "254B", "1114")
    value: a float representing the stat (OPR/DPR/CCWM) for that team
    """
    n = len(team_list)
    M = np.zeros([n, n])
    s = np.zeros([n, 1])

    # Constructing M and s
    for teams, score in parsed_matches:
        for team1 in teams:
            team1_id = team_id_map[team1]
            for team2 in teams:
                M[team1_id, team_id_map[team2]] += 1
            s[team1_id] += score

    # Solving M*x = s for x
    try:
        x = np.linalg.solve(M, s)
    except (np.linalg.LinAlgError, ValueError):
        return {}

    stat_dict = {}
    for team, stat in zip(team_list, x):
        stat_dict[team] = stat[0]

    return stat_dict

event_code = raw_input('Enter an event code for a 2016 match (such as 2016onto2): ')
exclude_fouls = raw_input('Would you like to remove foul points from OPR calculation?(y/n) ').lower() != 'n'
include_capture_breach = raw_input('Would you like to add points for capture/breach during quals in OPR calculation?(y/n) ').lower() != 'n'
include_playoffs = raw_input('Would you like to include playoff scores in OPR calculation?(y/n) ').lower() != 'n'
url = "http://www.thebluealliance.com/api/v2/event/" + event_code + "/matches"
headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}

r = requests.get(url, headers=headers)

contents = r.json()
matches = []
team_list = []


for match in contents:
    redAllianceStats = match['score_breakdown']['red']
    blueAllianceStats = match['score_breakdown']['blue']
    # TBA uses only qualification matches to calculate the OPRS, and does not account for anything special
    # thus, arguments of exclude_fouls = n, include_capture_breach = n, include_playoffs = n
    if not include_playoffs:
        if match['comp_level'] != 'qm':
            continue

    if exclude_fouls:
        redAllianceScore = redAllianceStats['totalPoints'] - redAllianceStats['foulPoints']
        blueAllianceScore = blueAllianceStats['totalPoints'] - blueAllianceStats['foulPoints']
    else:
        redAllianceScore = redAllianceStats['totalPoints']
        blueAllianceScore = blueAllianceStats['totalPoints']

    if include_capture_breach:
        if match['comp_level'] == 'qm':
            if redAllianceStats['teleopTowerCaptured']:
                redAllianceScore += 25
            if redAllianceStats['teleopDefensesBreached']:
                redAllianceScore += 20
            if blueAllianceStats['teleopTowerCaptured']:
                blueAllianceScore += 25
            if blueAllianceStats['teleopDefensesBreached']:
                blueAllianceScore += 20

    redAlliance = match['alliances']['red']['teams']
    blueAlliance = match['alliances']['blue']['teams']

    for team in redAlliance:
        if team_list.count(team) < 1:
            team_list.append(team)
    for team in blueAlliance:
        if team_list.count(team) < 1:
            team_list.append(team)

    matches.append((redAlliance, redAllianceScore))
    matches.append((blueAlliance, blueAllianceScore))

team_id_map = {}
for i, team in enumerate(team_list):
    team_id_map[team] = i

oprs = _calculate_opr(matches, team_list, team_id_map)

for team in iter(sorted(oprs, key=oprs.get, reverse=True)):
    if team[0] == 'f':
        outTeam = team[3:]
    else:
        outTeam = team;
    print outTeam, '\t', oprs[team]

