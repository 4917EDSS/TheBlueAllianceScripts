import requests
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1'}

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
    url = 'https://www.thebluealliance.com/api/v2/event/' + event_code + '/stats'
    r = requests.get(url, headers=headers)
    stats_contents = r.json()
    if not ('oprs' in stats_contents and stats_contents['oprs'] and stats_contents['ccwms']): return

    url = 'https://www.thebluealliance.com/api/v2/event/' + event_code + '/matches'
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    if playoffs_only:
        matches_contents = [x for x in matches_contents if x['comp_level'] != 'qm']


    correct, total = prediction_percentage(stats_contents['oprs'], matches_contents)
    totals['opr_correct'] += correct
    totals['num_games'] += total
    correct, total = prediction_percentage(stats_contents['ccwms'], matches_contents)
    totals['ccwm_correct'] += correct


for year in range(2002, 2005):
    url = 'https://www.thebluealliance.com/api/v2/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    totals = {'num_games': 0, 'opr_correct': 0, 'ccwm_correct': 0}
    for event in events_contents:
        print event['key']
        do_event(event['key'], totals)

    print year
    print totals
    print 'OPR ' + str(totals['opr_correct'] / float(totals['num_games']))
    print 'CCWM ' + str(totals['ccwm_correct'] / float(totals['num_games']))
