#!/usr/bin/env python2
# I beleive Python 2.7.9 or greater is required for this script
import requests
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1',
         'X-TBA-Auth-Key': '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ'}

def get_alliance_stat(stats, alliance):
    total_stat = 0;
    for team in alliance['teams']:
        total_stat += stats[team[3:]]
    return total_stat
        
def prediction_percentage(stats, matches):
    total = 0
    correct = 0
    for match in matches:
        redAlliance = match['alliances']['red']
        blueAlliance = match['alliances']['blue']
        if (redAlliance['score'] == blueAlliance['score']): continue
        try:
            redAllianceStat = get_alliance_stat(stats, redAlliance);
            blueAllianceStat = get_alliance_stat(stats, blueAlliance);
        except KeyError:
            continue

        if ((redAllianceStat > blueAllianceStat) == (redAlliance['score'] > blueAlliance['score'])):
            correct += 1
        total += 1

    return correct, total


def do_event(event_code, totals, playoffs_only=True):
    url = 'https://www.thebluealliance.com/api/v3/event/'+event_code+'/alliances'
    r = requests.get(url, headers=headers)
    alliance_data = r.json()
    if not alliance_data:
        return
    for i in range(len(alliance_data)):
        try:
            if alliance_data[i]['status']['status'] == "won":
                totals[i] += 1
        except:
            pass
    '''url = 'https://www.thebluealliance.com/api/v2/event/' + event_code + '/stats'
    r = requests.get(url, headers=headers)
    stats_contents = r.json()
    if not ('oprs' in stats_contents and stats_contents['oprs'] and stats_contents['ccwms']): return

    url = 'https://www.thebluealliance.com/api/v2/event/' + event_code + '/matches'
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    if playoffs_only:
        matches_contents = [x for x in matches_contents if x['comp_level'] != 'qm']

    for match in matches_contents:
        redAlliance = match['alliances']['red']
        blueAlliance = match['alliances']['blue']
        redOpr = get_alliance_stat(stats_contents['oprs'], redAlliance);
        blueOpr = get_alliance_stat(stats_contents['oprs'], blueAlliance);
        redCcwm = get_alliance_stat(stats_contents['ccwms'], redAlliance);
        blueCcwm = get_alliance_stat(stats_contents['ccwms'], blueAlliance);
        if ((redOpr>blueOpr) != (redCcwm > blueCcwm)):
            totals['diff_prediction'] += 1

    opr_correct, total = prediction_percentage(stats_contents['oprs'], matches_contents)
    totals['opr_correct'] += opr_correct
    totals['num_games'] += total
    correct, total = prediction_percentage(stats_contents['ccwms'], matches_contents)
    totals['ccwm_correct'] += correct'''


for year in range(2010, 2019):
    url = 'https://www.thebluealliance.com/api/v2/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    totals = [0,0,0,0,0,0,0,0]
    for event in events_contents:
        do_event(event['key'], totals)

    print(year)
    print(totals)
    for a in range(len(totals)):
        print(a, totals[a]/(sum(totals)*1.0))
