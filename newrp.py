#!/usr/bin/env python2
# I beleive Python 2.7.9 or greater is required for this script
from collections import defaultdict
import requests
import sys
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1',
'X-TBA-Auth-Key' : '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ'}

reqs = {}
def cached_request(url):
  if url not in reqs:
    r = requests.get(url, headers=headers)
    contents = r.json()
    reqs[url] = contents
  return reqs[url]
  

def get_oprs(event_code):
  url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/oprs'
  stats_contents = cached_request(url)
  if not (stats_contents and 'oprs' in stats_contents and stats_contents['oprs'] and stats_contents['ccwms']):
    return None, None
  oprs = stats_contents['oprs']
  return sorted(oprs.items(), key=lambda x: (x[1]), reverse=True)

def get_event_rankings(event_code, threshold=20):
  global outof
  url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/matches'
  matches_contents = cached_request(url)
  matches_contents = [x for x in matches_contents if x['comp_level'] == 'qm']

  rankings = {}
  for match in matches_contents:
    redRP = 0
    blueRP = 0
    redAlliance = match['alliances']['red']
    blueAlliance = match['alliances']['blue']
    if redAlliance['score'] > blueAlliance['score']:
      redRP += 2
    elif redAlliance['score'] < blueAlliance['score']:
      blueRP += 2
    else:
      blueRP += 1
      redRP += 1
    if not match['score_breakdown']:
      continue
    rsb = match['score_breakdown']['red']
    bsb = match['score_breakdown']['blue']
    if rsb['endgamePoints'] >= 16:
      redRP += 1
    red_balls = rsb['matchCargoTotal'] 
    if rsb['quintetAchieved']:
      red_balls += 2
    if red_balls >= threshold:
      redRP += 1

    if bsb['endgamePoints'] >= 16:
      blueRP += 1
    blue_balls = bsb['matchCargoTotal'] 
    if bsb['quintetAchieved']:
      blue_balls += 2
    if blue_balls >= threshold:
      blueRP += 1

    for t in redAlliance['team_keys']:
      if t not in rankings:
        rankings[t] = [0.0,0.0,0.0]
      if t not in redAlliance['dq_team_keys'] and t not in redAlliance['surrogate_team_keys']:
        rankings[t][0] += redRP
        rankings[t][1] += redAlliance['score']
      rankings[t][2] += 1.0
    for t in blueAlliance['team_keys']:
      if t not in rankings:
        rankings[t] = [0.0,0.0,0.0]
      if t not in blueAlliance['dq_team_keys'] and t not in blueAlliance['surrogate_team_keys']:
        rankings[t][0] += blueRP
        rankings[t][1] += blueAlliance['score']
      rankings[t][2] += 1.0
      

  return [x[0] for x in sorted(rankings.items(), key=lambda x: (x[1][0]/x[1][2], x[1][1]/x[1][2]), reverse=True)]
    

def score_agreement(oprs, ranking):
  score = 0
  for i in range(len(oprs)):
    score += abs(i - ranking.index(oprs[i][0]))
  return score

for event in ['2022carv', '2022hop', '2022new', '2022gal', '2022roe', '2022tur']:
  ranks = get_event_rankings(event)
  oprs = get_oprs(event)
  modifiedranks = get_event_rankings(event, threshold=30)
  with open(event, 'w') as f:
    for team, opr in oprs:
      f.write("{}, {:.1f}, {}, {}\n".format(team, opr, ranks.index(team)+1, modifiedranks.index(team)+1))
