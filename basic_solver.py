import requests

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
        redAllianceStat = get_alliance_stat(stats, redAlliance);
        blueAllianceStat = get_alliance_stat(stats, blueAlliance);

        if ((redAllianceStat > blueAllianceStat) == (redAlliance['score'] > blueAlliance['score'])):
            correct += 1
        total += 1

    return correct / float(total)


def do_event(event_code, playoffs_only=True):
    url = "https://www.thebluealliance.com/api/v2/event/" + event_code + "/matches"
    headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}
    r = requests.get(url, headers=headers)
    stats_contents = r.json()

    url = "https://www.thebluealliance.com/api/v2/event/" + event_code + "/matches"
    headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    if playoffs_only:
        matches_contents = [x for x in matches_contents if x['comp_level'] != 'qm']


    print prediction_percentage(stats_contents, matches_contents)


do_event(raw_input('Enter an event code'))
