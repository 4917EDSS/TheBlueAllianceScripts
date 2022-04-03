#!/usr/bin/env python2
# I beleive Python 2.7.9 or greater is required for this script
import requests
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1',
'X-TBA-Auth-Key' : '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ'}

def get_alliance_stat(stats, alliance):
    total_stat = 0;
    try:
        for team in alliance['team_keys']:
            total_stat += stats[team]
    except KeyError:
        # For some "bye" matches, they just make up an alliance of teams that didn't attend the event.
        return None
    return total_stat
        
def prediction_percentage(stats, matches):
    total = 0
    correct = 0
    for match in matches:
        redAlliance = match['alliances']['red']
        blueAlliance = match['alliances']['blue']
        if (redAlliance['score'] == blueAlliance['score']): continue
        redAllianceStat = get_alliance_stat(stats, redAlliance);
        blueAllianceStat = get_alliance_stat(stats, blueAlliance);

        if ((redAllianceStat > blueAllianceStat) == (redAlliance['score'] > blueAlliance['score'])):
            correct += 1
        total += 1

    return correct, total


def do_event(event_code, totals, playoffs_only=True):
    url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/oprs'
    r = requests.get(url, headers=headers)
    stats_contents = r.json()
    if not (stats_contents and 'oprs' in stats_contents and stats_contents['oprs'] and stats_contents['ccwms']): return

    url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/matches'
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    if playoffs_only:
        matches_contents = [x for x in matches_contents if x['comp_level'] != 'qm']

    total = 0
    opr_correct = 0
    ccwm_correct = 0
    for match in matches_contents:
        redAlliance = match['alliances']['red']
        blueAlliance = match['alliances']['blue']
        redOpr = get_alliance_stat(stats_contents['oprs'], redAlliance);
        blueOpr = get_alliance_stat(stats_contents['oprs'], blueAlliance);
        redCcwm = get_alliance_stat(stats_contents['ccwms'], redAlliance);
        blueCcwm = get_alliance_stat(stats_contents['ccwms'], blueAlliance);
        if not redOpr or not blueOpr:
            continue

        total += 1
            
        if ((redOpr > blueOpr) == (redAlliance['score'] > blueAlliance['score'])):
            opr_correct += 1
            
        if ((redCcwm > blueCcwm) == (redAlliance['score'] > blueAlliance['score'])):
            ccwm_correct += 1
            
        if ((redOpr>blueOpr) != (redCcwm > blueCcwm)):
            totals['diff_prediction'] += 1

    totals['num_games'] += total
    totals['opr_correct'] += opr_correct
    totals['ccwm_correct'] += ccwm_correct


for year in range(2022, 2023):
    if year == 2021:
        # 2021 had no events and messes this up.
        continue
    url = 'https://www.thebluealliance.com/api/v3/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    totals = {'num_games': 0, 'opr_correct': 0, 'ccwm_correct': 0, 'diff_prediction': 0}
    for event in events_contents:
        if event['event_type'] >= 6:
            # Don't care about weird events, like offseasons or remote.
            # https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/event_type.py#L2
            continue
        do_event(event['key'], totals)

    print(year)
    print(totals)
    print('OPR ' + str(totals['opr_correct'] / float(totals['num_games'])))
    print('CCWM ' + str(totals['ccwm_correct'] / float(totals['num_games'])))
