"""
Metro routing script
By RedTeapot
Deps: networkx
"""

import logging as log
import networkx as nx
import sys


def process_connected_stations(cross, stations, directions, lengths):
    for direction, value in cross['connections'].items():
        if value['type'] == 's':
            address = stations[value['number']]['address']
            directions[direction] += [address]
            lengths[direction]['-'.join(str(x) for x in address)] = 1

    return directions, lengths


def generate_way_command(address):
    template = '/execute @e[x={x},y={y},z={z},r={r},{scores}] ~ ~ ~ setblock {rx} {ry} {rz} minecraft:rail {rd}'

    scores = []
    score_prefix = 'score_'
    score_name = 'metro_st_l_{l}'
    score_min_suffix = '_min'

    for i in range(0, len(address)):
        l = address[i]

        if l < 10:
            score = score_prefix + score_name + score_min_suffix
            score = score.replace('{l}', str(i))
            score += '=' + str(l)
            scores += [score]

            score = score_prefix + score_name
            score = score.replace('{l}', str(i))
            score += '=' + str(l)
            scores += [score]
        else:
            div, mod = divmod(l, 10)
            score = score_prefix + score_name + score_min_suffix
            score = score.replace('{l}', str(i))
            score += '=' + str(div - 1)
            scores += [score]

            score = score_prefix + score_name
            score = score.replace('{l}', str(i))
            score += '=' + str(mod)
            scores += [score]

    template = template.replace('{scores}', ','.join(scores))
    return template


def process_cross(cross, paths, crosses, stations):
    log.info('Processing cross %s', cross['number'])

    directions = dict()
    directions['n'] = []
    directions['s'] = []
    directions['w'] = []
    directions['e'] = []

    lengths = dict()
    lengths['n'] = dict()
    lengths['s'] = dict()
    lengths['e'] = dict()
    lengths['w'] = dict()

    directions, lengths = process_connected_stations(cross, stations, directions, lengths)

    connected_stations = []
    for direction, value in cross['connections'].items():
        if value['type'] == 's':
            connected_stations += [value['number']]

    connected_crosses_directions = dict()
    for direction, value in cross['connections'].items():
        if value['type'] == 'c':
            connected_crosses_directions[value['number']] = direction

    log.debug('Connected stations: %s', connected_stations)

    # Walk through entire address array
    level_stack = []
    for i in range(0, len(cross['address'])):
        l = cross['address'][i]
        level_stack.append(l)

        # Process quads on this depth level except one where current station is located at
        for quad in range(0, 4):
            if quad == l:
                continue

            current_address = level_stack[:-1] + [quad]

            # Process crosses in this quad
            quad_crosses = [k for k, v in crosses.items() if v['address'][:i+1] == current_address]
            if len(quad_crosses) > 0:
                # log.debug('Crosses at %s: %s', current_address, quad_crosses)

                # Get path from current cross to each other in this quad
                shortest_path = 0
                for c in quad_crosses:
                    path = paths[cross['name']]['c' + str(c)]
                    if shortest_path == 0 or len(path) < len(shortest_path):
                        shortest_path = path
                # log.debug('Shortest path to %s is %s', current_address, shortest_path)

                if shortest_path != 0:
                    # Add current address to necessary direction
                    direction = connected_crosses_directions[int(shortest_path[1][1:])]
                    # log.debug('Direction for address %s: %s', current_address, direction)

                    if current_address not in directions[direction]:
                        directions[direction] += [current_address]
                        lengths[direction]['-'.join(str(x) for x in current_address)] = len(shortest_path)

            # Process stations in this quad
            quad_stations = [k for k, v in stations.items() if v['address'][:i+1] == current_address and
                             v['number'] not in connected_stations]
            if len(quad_stations) > 0:
                # log.debug('Stations at %s: %s', current_address, quad_stations)

                # Get path from current cross to each station in this quad
                shortest_path = 0
                for s in quad_stations:
                    path = paths[cross['name']]['s' + str(s)]
                    if shortest_path == 0 or len(path) < len(shortest_path):
                        shortest_path = path
                # log.debug('Shortest path to %s is %s', current_address, shortest_path)

                if shortest_path != 0:
                    # Add current address to necessary direction
                    direction = connected_crosses_directions[int(shortest_path[1][1:])]
                    # log.debug('Direction for address %s: %s', current_address, direction)

                    if current_address not in directions[direction]:
                        directions[direction] += [current_address]
                        lengths[direction]['-'.join(str(x) for x in current_address)] = len(shortest_path)

    log.debug('Directions addresses: %s', directions)
    log.debug('Directions lengths: %s', lengths)

    # Now we need to remove duplicates in different directions
    directions_noduplicates = dict()
    processed_addresses = []
    for d in ['n', 's', 'e', 'w']:
        directions_noduplicates[d] = []
    for direction, addresses in directions.items():
        other_directions = [x for x in ['n', 's', 'e', 'w'] if x != direction]

        other_directions_addresses = []
        other_directions_address_directions = []

        for d in other_directions:
            for other_address in directions[d]:
                other_directions_addresses += [other_address]
                other_directions_address_directions += d

        for address in addresses:
            if address not in processed_addresses:
                if address in other_directions_addresses:
                    addresses_to_compare = []
                    addresses_to_compare += [{'address': address,
                                              'direction': direction,
                                              'length': lengths[direction]['-'.join(str(x) for x in address)]}]
                    for i in range(0, len(other_directions_addresses)):
                        if other_directions_addresses[i] == address:
                            addresses_to_compare += [{'address': other_directions_addresses[i],
                                                      'direction': other_directions_address_directions[i],
                                                      'length': lengths[other_directions_address_directions[i]]['-'.join(str(x) for x in other_directions_addresses[i])]}]
                    shortest_addr = 0
                    for addr in addresses_to_compare:
                        if shortest_addr == 0 or addr['length'] < shortest_addr['length']:
                            shortest_addr = addr
                    directions_noduplicates[shortest_addr['direction']] += [shortest_addr['address']]
                else:
                    directions_noduplicates[direction] += [address]
                processed_addresses += [address]

    # Now we need to collapse multiple adjacent quads to one range
    # Like 0, 1, 2 -> 0..2

    directions_collapsed = dict()
    for direction, addresses in directions_noduplicates.items():
        if len(direction) == 0:
            continue

        directions_collapsed[direction] = []
        addresses_collapsed = []

        for address in addresses:
            if address in addresses_collapsed:
                continue

            collapse = [v for v in addresses if len(address) == len(v) and
                        address != v and
                        address[:-1] == v[:-1]]
            range_start = address[-1]
            range_end = address[-1]
            for c in collapse:
                last = c[-1]
                if last - range_start == -1:
                    range_start = last
                if last - range_end == 1:
                    range_end = last

            if range_start == range_end:
                if address not in directions_collapsed[direction]:
                    directions_collapsed[direction] += [address]
            else:
                # Add collapsed addresses to collapsed addresses list
                addresses_collapsed += collapse

                # Encode our range to store it in int
                # Like result = 10 * (start + 1) + end
                item = address[:-1] + [((range_start + 1) * 10 + range_end)]
                if item not in directions_collapsed[direction]:
                    directions_collapsed[direction] += [item]

    log.debug('Collapsed directions addresses: %s', directions_collapsed)

    commands = dict()
    for direction, addresses in directions_collapsed.items():
        commands[direction] = []
        for address in addresses:
            commands[direction] += [generate_way_command(address)]

    log.info('Done processing cross %s', cross['number'])

    return commands


def main(stations_data, crosses_data):

    log.info('Parsing CSV data')
    log.debug('Creating stations dict')

    stations = dict()
    for line in stations_data.split('\n')[1:]:
        columns = line.split(',')

        row = dict()
        row['number'] = int(columns[0])
        row['title'] = columns[1]
        row['address'] = []

        for level in columns[2].split('-'):
            row['address'].append(int(level))

        row['name'] = 's' + str(row['number'])

        stations[row['number']] = row

        log.debug('Parsed station %s', row)

    log.debug('Creating crosses dict')

    crosses = dict()
    for line in crosses_data.split('\n')[1:]:
        columns = line.split(',')

        row = dict()
        row['number'] = int(columns[0])
        row['address'] = []

        for level in columns[1].split('-'):
            row['address'].append(int(level))

        row['x'] = int(columns[6])
        row['z'] = int(columns[7])
        row['name'] = 'c' + str(row['number'])
        row['connections'] = dict()

        for direction in ['n', 's', 'w', 'e']:
            column = {'n': 2, 's': 3, 'w': 4, 'e': 5}[direction]
            if columns[column] == '-':
                continue
            row['connections'][direction] = dict()
            row['connections'][direction]['type'] = columns[column][0]
            row['connections'][direction]['number'] = int(columns[column][1:])

        crosses[row['number']] = row

        log.debug('Parsed cross %s', row)

    log.info('Building graph')
    log.debug('Creating nodes')
    graph = nx.Graph()
    for number, station in stations.items():
        graph.add_node(station['name'], type='s')
        log.debug('Added station %s', station['name'])

    for number, cross in crosses.items():
        graph.add_node(cross['name'], type='c')
        log.debug('Added cross %s', cross['name'])

    log.debug('Creating edges')
    for number, cross in crosses.items():
        for direction in ['n', 's', 'w', 'e']:
            if direction in cross['connections'].keys():
                direction = cross['connections'][direction]
                if direction['type'] == 'c':
                    other = crosses[direction['number']]['name']
                else:
                    other = stations[direction['number']]['name']
                graph.add_edge(cross['name'], other)
                log.debug('Created edge between %s and %s', cross['name'], other)

    log.debug('Building shortest paths')
    paths = nx.shortest_path(graph)

    log.info('Processing crosses')
    crosses_commands = dict()
    for number, cross in crosses.items():
        crosses_commands[number] = process_cross(cross, paths, crosses, stations)
    log.info('Done processing crosses')

    print('Done processing')

    while True:
        user_input = input('Input cross number (or \'q\' to quit): ')
        if user_input == 'q':
            log.info('User exit')
            break
        cross_number = int(user_input)
        while True:
            user_input = input('Input direction (\'n\', \'s\', \'e\' or \'w\' or \'q\' to proceed to next cross): ')
            if user_input == 'q':
                break
            cross_direction = user_input
            x, y, z = input('Input x y z: ').split(' ')
            r = 2
            rx, ry, rz = input('Input RAIL x y z: ').split(' ')
            rd = input('Input rail direction: ')
            commands = crosses_commands[cross_number][cross_direction]
            for command in commands:
                command = command.replace('{x}', str(x))
                command = command.replace('{y}', str(y))
                command = command.replace('{z}', str(z))

                command = command.replace('{r}', str(r))

                command = command.replace('{rx}', str(rx))
                command = command.replace('{ry}', str(ry))
                command = command.replace('{rz}', str(rz))

                command = command.replace('{rd}', str(rd))

                print(command)

    print('Closing')

log.basicConfig(filename='path_builder.debug.log', level=log.DEBUG, filemode='w')
log.info('Started')

file = open(sys.argv[1], 'r')
log.info('Loading stations file %s', file.name)
stationsData = file.read()
file.close()

file = open(sys.argv[2], 'r')
log.info('Loading crosses file %s', file.name)
crossesData = file.read()
file.close()

log.info('Starting processing')

main(stationsData, crossesData)

log.info('Done')
