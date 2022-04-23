#!/usr/bin/env python2
# I beleive Python 2.7.9 or greater is required for this script
from collections import defaultdict
import requests
import sys
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1',
'X-TBA-Auth-Key' : '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ'}

def get_alliance_stat(stats, alliance):
    total_stat = 0;
    if 'team_keys' in alliance:
        alliance = alliance['team_keys']

    try:
        for team in alliance:
            total_stat += stats[team]
    except KeyError:
        # For some "bye" matches, they just make up an alliance of teams that didn't attend the event.
        return None
    return total_stat
        
def who_had_worst_schedule(event_code):
    url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/oprs'
    r = requests.get(url, headers=headers)
    stats_contents = r.json()
    if not (stats_contents and 'oprs' in stats_contents and stats_contents['oprs'] and stats_contents['ccwms']):
        return None, None
    oprs = stats_contents['oprs']

    url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/matches'
    r = requests.get(url, headers=headers)
    matches_contents = r.json()
    matches_contents = [x for x in matches_contents if x['comp_level'] == 'qm']

    per_team_alliance_oprs = {}
    for match in matches_contents:
        redAlliance = match['alliances']['red']
        blueAlliance = match['alliances']['blue']
        redOpr = get_alliance_stat(oprs, redAlliance);
        blueOpr = get_alliance_stat(oprs, blueAlliance);
        if not redOpr or not blueOpr:
            continue

        for team in redAlliance['team_keys']:
            if team not in per_team_alliance_oprs:
                per_team_alliance_oprs[team] = [0,0]
            per_team_alliance_oprs[team][0] += redOpr - oprs[team]
            per_team_alliance_oprs[team][1] += blueOpr
        for team in blueAlliance['team_keys']:
            if team not in per_team_alliance_oprs:
                per_team_alliance_oprs[team] = [0,0]
            per_team_alliance_oprs[team][0] += blueOpr - oprs[team]
            per_team_alliance_oprs[team][1] += redOpr


    reduced = {k: (v[0]/2.0)/(v[1]/3.0) for k, v in per_team_alliance_oprs.items()}
    return min(reduced.items(), key=lambda x: x[1])
        

for year in range(2018, 2019):
    if year == 2021:
        # 2021 had no events and messes this up.
        continue
    url = 'https://www.thebluealliance.com/api/v3/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    with open('worstschedules{}.txt'.format(year), 'w') as f:
      for event in events_contents:
          if event['event_type'] >= 6:
              # Don't care about weird events, like offseasons or remote.
              # https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/event_type.py#L2
              continue
          try:
              team, score = who_had_worst_schedule(event['key'])
              if team:
                  if (score < 0.3):
                      print (team,score)
                  f.write('{} {} {}\n'.format(score, team, event['key']))
          except Exception:
            print (event['key'])
            t, v, tb = sys.exc_info()
            raise t, v, tb
          

    print(year)
