#!/usr/bin/env python
#I believe Python 2.7.9 or greater is required for this script
import requests
headers={'X-TBA-App-Id' : 'frc4917:customOPRCalculator:1',
         'X-TBA-Auth-Key': '0iqkELghwiXt0AEDTipqrtUYJ66OYHVPgBdv2YMKwk4VxTFILVW6CtPUTN8hSKVQ'}


def do_event(event_code, totals, playoffs_only=True):
    url = 'https://www.thebluealliance.com/api/v3/event/'+event_code+'/matches'
    r = requests.get(url, headers=headers)
    matches_data = r.json()
    if not matches_data:
        return
    for i in range(len(matches_data)):
        if not matches_data[i]:
            continue
        if not matches_data[i]['score_breakdown']:
            continue
        if not matches_data[i]['score_breakdown']['blue']:
            continue
        blue =  matches_data[i]['alliances']['blue']['team_keys']
        red =  matches_data[i]['alliances']['red']['team_keys']
        for j in range(len(blue)):
            if blue[j] not in totals:
                totals[blue[j]] = [0, 0, 0]
            totals[blue[j]][0] += 1
            if 'autoRobot1' not in matches_data[i]['score_breakdown']['blue']:
                print (matches_data)
            if matches_data[i]['score_breakdown']['blue']['autoRobot' + str(j+1)] == "AutoRun":
                totals[blue[j]][1] += 1
            if matches_data[i]['score_breakdown']['blue']['endgameRobot' + str(j+1)] == "Climbing":
                totals[blue[j]][2] += 1

        for j in range(len(red)):
            if red[j] not in totals:
                totals[red[j]] = [0, 0, 0]
            totals[red[j]][0] += 1
            if matches_data[i]['score_breakdown']['red']['autoRobot' + str(j+1)] == "AutoRun":
                totals[red[j]][1] += 1
            if matches_data[i]['score_breakdown']['red']['endgameRobot' + str(j+1)] == "Climbing":
                totals[red[j]][2] += 1

for year in range(2018, 2019):
    url = 'https://www.thebluealliance.com/api/v2/events/' + str(year)
    r = requests.get(url, headers=headers)
    events_contents = r.json()

    totals = {}
    for event in events_contents:
        do_event(event['key'], totals)

    for a in totals:
        print (a + ', ' + str(totals[a][0]) + ', ' + str(totals[a][1]) + ', ' + str(totals[a][2]))
