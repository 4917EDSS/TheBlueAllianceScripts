import os
import webapp2
import json
import numpy as np
import jinja2
import collections
from google.appengine.api import urlfetch

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.globals.update({'uri_for': webapp2.uri_for})

# parsed_matches: list of ([frcXXXX, frcYYYY, frcZZZZ], score) tuples
# team_list: list of teams as they come from TBA ("frc4917")
# team_id_map: dict mapping list of teams as they come from TBA ("frc4917") to unique ints (1,2,3...)
def _calculate_opr(parsed_matches, team_list, team_id_map):
    # OPR calc taken to match the blue alliance's calc
    """
    Returns: a dict where
    key: a string representing a team number (Example: "254", "254B", "1114")
    value: a float representing the stat (OPR/DPR/CCWM) for that team
    """
    if not parsed_matches:
        return {}
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

    opr_ranking_dict = collections.OrderedDict()
    i = 1;
    for team in iter(sorted(stat_dict, key=stat_dict.get, reverse=True)):
        opr_ranking_dict[team] = {"value": stat_dict[team], "rank": i}
        i += 1
        
    return opr_ranking_dict

# team_number is the string number of the team ("4917")
# year is the string number of the year ("2017")
def getEvents(team_number, year=None):
    if not year:
        year = 2017
    url = "http://www.thebluealliance.com/api/v2/team/frc" + str(team_number) + "/" + str(year) + "/events"
    headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}
    for i in range(3):
        try:
            r = urlfetch.fetch(url=url, headers=headers, method='GET', validate_certificate=False)
            break
        except:
            pass
    contents = json.loads(r.content)

    events_list = []
    for event in contents:
        events_list.append(event['key'])

    return events_list
    

# event_code: string with event code ("2016onwa")
# include_fouls: whether to include foul points given to you by other team
# include_capture_breach: whether to include capture or breach points for qualification matches
# include_playoffs: whether to include playoff matches
def getOprs(event_code, include_fouls=True, include_capture_breach=True, include_playoffs=False):
    year = event_code[:4]
    url = "http://www.thebluealliance.com/api/v2/event/" + event_code + "/matches"
    headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}
    for i in range(3):
        try:
            r = urlfetch.fetch(url=url, headers=headers, method='GET', validate_certificate=False)
            break
        except:
            pass
    contents = json.loads(r.content)

    if not contents or isinstance(contents, dict):
        return {}
    matches = []
    team_list = []

    for match in contents:
        try:
            redAllianceStats = match['score_breakdown']['red']
            blueAllianceStats = match['score_breakdown']['blue']

            if not include_playoffs:
                if match['comp_level'] != 'qm':
                    continue

            if include_fouls:
                redAllianceScore = redAllianceStats['totalPoints']
                blueAllianceScore = blueAllianceStats['totalPoints']
            else:
                redAllianceScore = redAllianceStats['totalPoints'] - redAllianceStats['foulPoints']
                blueAllianceScore = blueAllianceStats['totalPoints'] - blueAllianceStats['foulPoints']

            if include_capture_breach:
                if str(year) == '2016':
                    if match['comp_level'] == 'qm':
                        if redAllianceStats['teleopTowerCaptured']:
                            redAllianceScore += 25
                        if redAllianceStats['teleopDefensesBreached']:
                            redAllianceScore += 20
                        if blueAllianceStats['teleopTowerCaptured']:
                            blueAllianceScore += 25
                        if blueAllianceStats['teleopDefensesBreached']:
                            blueAllianceScore += 20
                elif str(year) == '2017':
                    if match['comp_level'] == 'qm':
                        if redAllianceStats['kPaRankingPointAchieved']:
                            redAllianceScore += 20
                        if redAllianceStats['rotorRankingPointAchieved']:
                            redAllianceScore += 100
                        if blueAllianceStats['kPaRankingPointAchieved']:
                            blueAllianceScore += 20
                        if blueAllianceStats['rotorRankingPointAchieved']:
                            blueAllianceScore += 100

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
        except:
            pass

    team_id_map = {}
    for i, team in enumerate(team_list):
        team_id_map[team] = i

    return _calculate_opr(matches, team_list, team_id_map)

def getOptions(request):
    fouls = request.get('fouls')
    playoffs = request.get('playoffs')
    capture_breach = request.get('capturebreach')
    
    include_fouls = False
    if fouls and fouls=="True":
        include_fouls = True
    
    include_playoffs = False
    if playoffs and playoffs=="True":
        include_playoffs = True
    
    include_capture_breach = False
    if capture_breach and capture_breach=="True":
        include_capture_breach = True
    
    return {'include_fouls': include_fouls, 'include_playoffs': include_playoffs, 'include_capture_breach': include_capture_breach}
    

def getTeamsEventToOprMap(team_number, options, year):
    oprDict = collections.OrderedDict()
    teamEvents = getEvents(team_number, year)
    for event in teamEvents:
        oprs = getOprs(event, **options)
        try:
            oprDict[event] = oprs["frc" + str(team_number)]
        except KeyError:
            oprDict[event] = {"value": 0, "rank": 0}
    return oprDict
        
class TeamPage(webapp2.RequestHandler):
    def get(self, team_number):
        options = getOptions(self.request)
        oprDict = getTeamsEventToOprMap(team_number, options, self.request.get('year'))

        template_values = {
            'title': team_number,
            'valueDict': oprDict,
            'type': 'team',
            'year': self.request.get('year') or '2017',
            'options': options
        }
            
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class MainPage(webapp2.RequestHandler):
    def get(self, event_id):
        options = getOptions(self.request)
        oprs = getOprs(event_id, **options)
        if not oprs:
            # Get event
            url = "http://www.thebluealliance.com/api/v2/event/" + event_id + "/teams"
            headers={"X-TBA-App-Id" : "frc4917:customOPRCalculator:1"}
            for i in range(3):
                try:
                    r = urlfetch.fetch(url=url, headers=headers, method='GET', validate_certificate=False)
                    break
                except:
                    pass
            contents = json.loads(r.content)
            oprs = collections.OrderedDict()
            for t in contents:
                team = str(t["team_number"])
                teamOprDict = getTeamsEventToOprMap(team, options, self.request.get('year'))
                maxval = 0
                maxrank = 0
                for key, value in teamOprDict.iteritems():
                    maxval = max(maxval, value['value'])
                    if maxval == value['value']:
                        maxrank = value['rank']
                oprs[team] = {'rank':maxrank, 'value':maxval}


        oprDict = collections.OrderedDict()
        for team in iter(oprs):
            if team[0] == 'f':
                outTeam = team[3:]
            else:
                outTeam = team;
            oprDict[outTeam] = oprs[team]
        
        template_values = {
            'title': event_id,
            'valueDict': oprDict,
            'type': 'event',
            'year': self.request.get('year') or '2017',
            'options': options
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    webapp2.Route('/<event_id>', MainPage, name='event'),
    webapp2.Route('/t/<team_number>', TeamPage, name='team'),
], debug=True)
