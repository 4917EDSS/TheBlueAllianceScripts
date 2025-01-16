#!/usr/bin/env python3
from collections import defaultdict
import urllib.request
import json
import sys

def get_json(url):
  request = urllib.request.Request(url)
  request.add_header('accept', 'application/json')
  request.add_header('X-TBA-Auth-Key', '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ')
  request.add_header('User-Agent', '4917')
  with urllib.request.urlopen(request) as response:
    return json.loads(response.read())
        
def get_winning_alliance(event_code):
    url = 'https://www.thebluealliance.com/api/v3/event/' + event_code + '/alliances'
    alliances = get_json(url)
    if not alliances:
      return None 
    for i in range(len(alliances)):
      a = alliances[i]
      if 'status' not in a:
        continue
      if a['status']['status'] == 'won':
        if 'name' in a:
          return a['name'][-1:]
        return str(i+1)
      # 2010ca had this issue.
      if a['status']['status'] == 'playing':
        if a['status']['current_level_record']['wins'] >= 2:
          if 'name' in a:
            return a['name'][-1:]
          return str(i+1)
    return None
        

winners_by_year = {}
for year in range(2010, 2024+1):
    winners_by_year[year] = defaultdict(int)
    if year == 2021:
        # 2021 had no events and messes this up.
        continue
    url = 'https://www.thebluealliance.com/api/v3/events/' + str(year)

    for event in get_json(url):
        if event['event_type'] >= 6:
            # Don't care about weird events, like offseasons or remote.
            # https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/event_type.py#L2
            continue
        try:
            winning_alliance = get_winning_alliance(event['key'])
            if not winning_alliance:
              print(event['key'] + ' FAILED')
              continue
            winners_by_year[year][winning_alliance] += 1
            
        except Exception as e:
          print (event['key'])
          raise e
          

    print(year)
    print(winners_by_year[year])

for y, winners in winners_by_year.items():
  print(y)
  print(winners)
