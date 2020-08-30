#!/usr/bin/env python3
import json
import sys


def parse_json(json_data):
    airframes = {}
    weapons = {}
    pilots = {}

    for pilot in json_data:
        pilot_data = json_data[pilot]

        pilot_name = parse_pilot_name(pilot_data)
        pilots[pilot_name] = {'airframeTime' : {},'weaponsEmployed' : [], 'numHits' : 0, 'kills' : 0, 'shot' : 0,
                'pilotDeath' : 0, 'crash' : 0, 'eject' : 0, 'targetsDestroyed' : {}, 'LSO' : {}}

        print('Processing: {}'.format(pilot_name))

        for aircraft in pilot_data['times']:
            if aircraft not in airframes:
                airframes[aircraft] = {'weaponsEmployed' : [], 'numHits' : 0, 'kills' : 0, 'shot' : 0,
                        'total' : 0, 'inAir': 0, 'pilotDeath' : 0, 'crash' : 0, 'eject' : 0, 'targetsDestroyed' : {}}
            aircraft_data = pilot_data['times'][aircraft]

            airframes[aircraft]['total'] += aircraft_data['total']
            airframes[aircraft]['inAir'] += aircraft_data['inAir']

            pilots[pilot_name]['airframeTime'][aircraft] = {}
            pilots[pilot_name]['airframeTime'][aircraft]['total'] = aircraft_data['total']
            pilots[pilot_name]['airframeTime'][aircraft]['inAir'] = aircraft_data['inAir']

            if 'weapons' in aircraft_data:
                for weapon in aircraft_data['weapons']:
                    if weapon not in weapons:
                        weapons[weapon] = {'numHits' : 0, 'kills' : 0, 'shot' : 0}

                    if weapon not in airframes[aircraft]['weaponsEmployed']:
                        airframes[aircraft]['weaponsEmployed'].append(weapon)

                    if weapon not in pilots[pilot_name]['weaponsEmployed']:
                        pilots[pilot_name]['weaponsEmployed'].append(weapon)
                    
                    for stat in aircraft_data['weapons'][weapon]:
                        if stat != 'gun' and stat != 'hit':
                            statistic = aircraft_data['weapons'][weapon][stat]
                            airframes[aircraft][stat] += statistic
                            weapons[weapon][stat] += statistic
                            pilots[pilot_name][stat] += statistic

            if 'actions' in aircraft_data:
                if 'LSO' in aircraft_data['actions']:
                    lso_data = aircraft_data['actions']['LSO']
                    pilots[pilot_name]['LSO'] = lso_data

                if 'losses' in aircraft_data['actions']:
                    loss_data = aircraft_data['actions']['losses']
                    for stat in loss_data:
                        statistic = loss_data[stat]
                        airframes[aircraft][stat] += statistic
                        pilots[pilot_name][stat] += statistic

            if 'kills' in aircraft_data:
                kill_data = aircraft_data['kills']
            
                for kill_type in kill_data:
                    if kill_type not in airframes[aircraft]['targetsDestroyed']:
                        airframes[aircraft]['targetsDestroyed'][kill_type] = {'total' : 0}

                    if kill_type not in pilots[pilot_name]['targetsDestroyed']:
                        pilots[pilot_name]['targetsDestroyed'][kill_type] = {'total' : 0}

                    for category in kill_data[kill_type]:
                        if category not in airframes[aircraft]['targetsDestroyed'][kill_type]:
                            airframes[aircraft]['targetsDestroyed'][kill_type][category] = 0

                        if category not in pilots[pilot_name]['targetsDestroyed'][kill_type]:
                            pilots[pilot_name]['targetsDestroyed'][kill_type][category] = 0
                
                        airframes[aircraft]['targetsDestroyed'][kill_type][category] += kill_data[kill_type][category]
                        pilots[pilot_name]['targetsDestroyed'][kill_type][category] += kill_data[kill_type][category]

    return airframes, weapons, pilots


def parse_pilot_name(pilot_data):
    pilot_name = ''

    for name in pilot_data['names']:
        if '[40TH SOC]' in name.upper():
            if len(pilot_name) > 0:
                pilot_name += ', AKA '
            pilot_name += name

    if pilot_name == '':
        pilot_name = pilot_data['names'][0]

    return pilot_name


def print_file(string):
    filename = 'stats_output.txt'
    with open(filename, 'a') as f:
        f.write(string)


def fancy_header(title):
    num_asterisks = int((80 - (len(title) + 2)) / 2)
    asterisks = '*' * num_asterisks
    print_file('{} {} {}\n'.format(asterisks, title, asterisks))


def fancy_footer():
    print_file('*' * 80)


def output_airframe_stats(airframes):
    airframe_stats = ''

    for airframe in airframes:
        weapons_employed = airframes[airframe]['weaponsEmployed']
        kills = airframes[airframe]['kills']
        cockpit_time = round(airframes[airframe]['total'] / 60, 2)
        air_time = round(airframes[airframe]['inAir'] / 60, 2)
        deaths = airframes[airframe]['pilotDeath']
        crashes = airframes[airframe]['crash']
        ejections = airframes[airframe]['eject']
        targets = get_targets_as_str(airframes[airframe]['targetsDestroyed'])

        airframe_stats += '[{}]:\n'.format(airframe)
        airframe_stats += 'Weapons Employed: {}\n'.format(', '.join(weapons_employed))
        airframe_stats += 'Kills: {}\n'.format(kills)
        airframe_stats += 'Total time in cockpit: {} minutes\n'.format(cockpit_time)
        airframe_stats += 'Total time in air: {} minutes\n'.format(air_time)
        airframe_stats += 'Crashes: {}\n'.format(crashes)
        airframe_stats += 'Ejections: {}\n'.format(ejections)
        airframe_stats += 'Deaths: {}'.format(deaths)

        if len(targets) > 0:
            airframe_stats += '\nTargets destroyed:\n{}'.format(targets)

        airframe_stats += '\n\n'

    fancy_header('AIRFRAME STATISTICS')
    print_file(airframe_stats)


def get_targets_as_str(targets):
    targets_str = ''

    for j, target in enumerate(targets):
        targets_str += '\t<{}>: '.format(target)

        for i, target_type in enumerate(targets[target]):
            targets_str += '{}: {}'.format(target_type, targets[target][target_type])

            if i < len(targets[target]) - 1:
                targets_str += ', '

        if j < len(targets) - 1:
            targets_str += '\n'

    return targets_str


def output_weapon_stats(weapons):
    weapon_str = ''

    for weapon in weapons:
        kills = weapons[weapon]['kills']
        shots = weapons[weapon]['shot']
        hits = weapons[weapon]['numHits']
        accuracy = round(hits / max(shots, 1) * 100, 2)

        weapon_str += '[{:18s}]: '.format(weapon)
        weapon_str += '{:5d} Shots, '.format(shots)
        weapon_str += '{:5d} Hits, '.format(hits)
        weapon_str += '{:2d} Kills,\t'.format(kills)
        weapon_str += 'Accuracy: {}%'.format(accuracy)
        weapon_str += '\n'

    fancy_header('WEAPON STATISTICS')
    print_file('{}'.format(weapon_str))
    

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        raw_data = f.read()

    json_data = json.loads(raw_data)

    airframes, weapons, pilots = parse_json(json_data)

    output_airframe_stats(airframes)
    output_weapon_stats(weapons)
    fancy_footer()
