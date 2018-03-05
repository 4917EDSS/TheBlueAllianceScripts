# I beleive Python 2.7.9 or greater is required for this script
import requests
import operator
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1'}

def get_alliance_stat(stats, alliance):
    total_stat = 0;
    for team in alliance['teams']:
        total_stat += stats[team[3:]]
    return total_stat
        
def prediction_percentage(matches):
    total = 0
    correct = 0
    team_list = {}
    for match in sorted(matches, key=lambda k: k['match_number']):
        try:
            redAlliance = match['alliances']['red']['teams']
            blueAlliance = match['alliances']['blue']['teams']
            redlliance = match['score_breakdown']['red']
            bluelliance = match['score_breakdown']['blue']
            
            if redlliance['rotor4Engaged']:
                for a in redAlliance:
                    if a in team_list:
                        team_list[a] += 1
                    else:
                        team_list[a] = 1
            if bluelliance['rotor4Engaged']:
                for a in blueAlliance:
                    if a in team_list:
                        team_list[a] += 1
                    else:
                        team_list[a] = 1
        except Exception as e:
            pass
        '''if (redAlliance['score'] == blueAlliance['score']): continue
        try:
            redAllianceStat = get_alliance_stat(stats, redAlliance);
            blueAllianceStat = get_alliance_stat(stats, blueAlliance);
        except KeyError:
            continue

        if ((redAllianceStat > blueAllianceStat) == (redAlliance['score'] > blueAlliance['score'])):
            correct += 1
        total += 1'''

    for key, value in team_list.iteritems():
        print key, value
    return correct, total


def do_event(event_code, totals, playoffs_only=True):
    url = 'https://www.thebluealliance.com/api/v2/event/' + event_code + '/matches'
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    if playoffs_only:
        matches_contents = [x for x in matches_contents if x['comp_level'] == 'qm']
    correct, total = prediction_percentage(matches_contents)


for year in range(2017, 2018):
    url = 'https://www.thebluealliance.com/api/v2/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    totals = {'num_games': 0, 'opr_correct': 0, 'ccwm_correct': 0}
    for event in events_contents:
        do_event(event['key'], totals)

