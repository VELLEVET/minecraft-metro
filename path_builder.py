"""
Metro routing script
By RedTeapot
Deps: networkx
"""

import logging as log
import networkx as nx
import sys

from data.Station import Station
from data.Cross import Cross
from data.Address import Address
from command_generator import generate_commands


def print_list(list_to_print):
    result = "["

    items = []

    for value in list_to_print:
        if isinstance(value, dict):
            items += [print_dict(value)]
        elif isinstance(value, list):
            items += [print_list(value)]
        else:
            items += [str(value)]

    result += ", ".join(items)
    result += "]"
    return result


def print_dict(dictionary):
    result = "{"
    items = []

    for key, value in dictionary.items():
        item = "\'" + str(key) + "\': "
        if isinstance(value, dict):
            item += print_dict(value)
        elif isinstance(value, list):
            item += print_list(value)
        else:
            item += str(value)
        items += [item]

    result += ", ".join(items)
    result += "}"
    return result


def process_connected_stations(cross, stations):
    directions = dict()
    lengths = dict()
    connected_stations = []

    def process_direction(d, obj):
        if obj is None or obj[0] != "s":
            return

        if d not in directions:
            directions[d] = []
        directions[d] += [obj]

        if d not in lengths:
            lengths[d] = dict()
        lengths[d][obj] = 1

        connected_stations.append(obj)

    direction = cross.get_n()
    process_direction('n', direction)
    direction = cross.get_s()
    process_direction('s', direction)
    direction = cross.get_w()
    process_direction('w', direction)
    direction = cross.get_e()
    process_direction('e', direction)

    return directions, lengths, connected_stations


def process_distant_stations(cross, shortest_paths, stations, connected_stations, connected_crosses_directions):
    directions = dict()
    directions['n'] = []
    directions['s'] = []
    directions['w'] = []
    directions['e'] = []

    lengths = dict()
    lengths['n'] = dict()
    lengths['s'] = dict()
    lengths['w'] = dict()
    lengths['e'] = dict()

    for i in range(0, cross.get_address().get_depth()):
        l = cross.get_address().at(i)
        stack = cross.get_address().get_to_depth(i)

        for q in range(0, 4):
            if q == l:
                continue
            quad_addr = Address(stack)
            quad_addr.push_level(q)

            quad_stations_str_ids = [str_id for str_id, s in stations.items()
                                     if quad_addr.partial_compare(s.get_address()) and
                                     str_id not in connected_stations]

            if len(quad_stations_str_ids) > 0:
                shortest_path = None
                for station in quad_stations_str_ids:
                    path = shortest_paths[cross.get_str_id()][station]
                    if shortest_path is None or len(path) < len(shortest_path):
                        shortest_path = path

                direction = connected_crosses_directions[shortest_path[1]]
                if quad_addr not in directions[direction]:
                    directions[direction] += [quad_addr]
                    lengths[direction]['-'.join(str(x) for x in quad_addr)] = len(shortest_path)

    return directions, lengths


def process_distant_crosses(cross, shortest_paths, crosses, connected_crosses_directions):
    directions = dict()
    directions['n'] = []
    directions['s'] = []
    directions['w'] = []
    directions['e'] = []

    lengths = dict()
    lengths['n'] = dict()
    lengths['s'] = dict()
    lengths['w'] = dict()
    lengths['e'] = dict()

    for i in range(0, cross.get_address().get_depth()):
        l = cross.get_address().at(i)
        stack = cross.get_address().get_to_depth(i)

        for q in range(0, 4):
            if q == l:
                continue
            quad_addr = Address(stack)
            quad_addr.push_level(q)

            quad_crosses_str_ids = [str_id for str_id, c in crosses.items()
                                    if quad_addr.partial_compare(c.get_address())]

            if len(quad_crosses_str_ids) > 0:
                shortest_path = None
                for distant_cross in quad_crosses_str_ids:
                    path = shortest_paths[cross.get_str_id()][distant_cross]
                    if shortest_path is None or len(path) < len(shortest_path):
                        shortest_path = path

                direction = connected_crosses_directions[shortest_path[1]]
                if quad_addr not in directions[direction]:
                    directions[direction] += [quad_addr]
                    lengths[direction]['-'.join(str(x) for x in quad_addr)] = len(shortest_path)

    return directions, lengths


def process_duplicates(directions, lengths):
    directions_new = dict()
    processed_addresses = []

    for d in ['n', 's', 'w', 'e']:
        directions_new[d] = []

    for d, addresses in directions.items():
        other_directions = [x for x in ['n', 's', 'w', 'e'] if x != d]

        other_directions_addresses = []
        other_directions_address_directions = []

        for other_direction in other_directions:
            for other_address in directions[other_direction]:
                other_directions_addresses += [other_address]
                other_directions_address_directions += [other_direction]

        for address in addresses:
            if address in processed_addresses:
                continue

            if address in other_directions_addresses:
                addresses_to_compare = []
                addresses_to_compare += [{'address': address,
                                          'direction': d,
                                          'length': lengths[d]['-'.join(str(x) for x in address)]}]
                for i in range(0, len(other_directions_addresses)):
                    if other_directions_addresses[i] == address:
                        addresses_to_compare += [{'address': other_directions_addresses[i],
                                                  'direction': other_directions_address_directions[i],
                                                  'length': lengths[other_directions_address_directions[i]][
                                                      '-'.join(str(x) for x in other_directions_addresses[i])]}]
                shortest_addr = 0
                for addr in addresses_to_compare:
                    if shortest_addr == 0 or addr['length'] < shortest_addr['length']:
                        shortest_addr = addr
                directions_new[shortest_addr['direction']] += [shortest_addr['address']]
            else:
                directions_new[d] += [address]

            processed_addresses += [address]

    log.debug("Directions before removing duplicates: %s", print_dict(directions))
    log.debug("Directions after removing duplicates: %s", print_dict(directions_new))

    return directions_new


def process_ranges(directions):
    directions_new = dict()

    for d, addresses in directions.items():
        if len(addresses) == 0:
            continue

        directions_new[d] = []
        addresses_collapsed = []

        for address in addresses:
            if address in addresses_collapsed:
                continue

            collapse = [v for v in addresses if v.get_depth() == address.get_depth() and
                        address != v and
                        address.get_array()[:-1] == v.get_array()[:-1]]

            range_start = address.at(-1)
            range_end = address.at(-1)

            for c in collapse:
                last = c.at(-1)
                if last - range_start == -1:
                    range_start = last
                if last - range_end == 1:
                    range_end = last

            if range_start == range_end:
                if address not in directions_new[d]:
                    directions_new[d] += [address]
            else:
                addresses_collapsed += collapse

                # Encode our range to store it in int
                # Like result = 10 * (start + 1) + end
                item = Address(address.get_array()[:-1] + [((range_start + 1) * 10 + range_end)])
                if item not in directions_new[d]:
                    directions_new[d] += [item]

    log.debug("Raw directions: %s", print_dict(directions))
    log.debug("Collapsed directions: %s", print_dict(directions_new))

    return directions_new


def process_cross_direction_addresses(cross, shortest_paths, stations, crosses):
    log.debug("Processing %s", cross)
    directions = dict()
    directions['n'] = []
    directions['s'] = []
    directions['w'] = []
    directions['e'] = []

    lengths = dict()
    lengths['n'] = dict()
    lengths['s'] = dict()
    lengths['w'] = dict()
    lengths['e'] = dict()

    connected_crosses_directions = dict()
    if cross.get_n() is not None:
        connected_crosses_directions[cross.get_n()] = 'n'
    if cross.get_s() is not None:
        connected_crosses_directions[cross.get_s()] = 's'
    if cross.get_w() is not None:
        connected_crosses_directions[cross.get_w()] = 'w'
    if cross.get_e() is not None:
        connected_crosses_directions[cross.get_e()] = 'e'

    directions_new, lengths_new, connected_stations = process_connected_stations(cross, stations)
    directions.update(directions_new)
    lengths.update(lengths_new)

    directions_new, lengths_new = process_distant_stations(cross, shortest_paths, stations, connected_stations,
                                                           connected_crosses_directions)
    directions.update(directions_new)
    lengths.update(lengths_new)

    directions_new, lengths_new = process_distant_crosses(cross, shortest_paths, crosses, connected_crosses_directions)
    directions.update(directions_new)
    lengths.update(lengths_new)

    directions_new = process_duplicates(directions, lengths)
    directions.update(directions_new)

    directions_new = process_ranges(directions)
    directions = directions_new

    return directions


def process(stations_data, crosses_data):
    stations = dict()
    crosses = dict()

    log.info("Loading stations from CSV")
    lines = stations_data.split('\n')[1:]  # Skip header
    for line in lines:
        station = Station.load_from_csv(line)
        stations[station.get_str_id()] = station
        log.debug("Adding station %s", station)

    log.info("Loading crosses from CSV")
    lines = crosses_data.split('\n')[1:]  # Skip header
    for line in lines:
        cross = Cross.load_from_csv(line)
        crosses[cross.get_str_id()] = cross
        log.debug("Adding cross %s", cross)

    log.info("Building graph")
    graph = nx.Graph()
    log.debug("Creating station nodes")
    for str_id, station in stations.items():
        graph.add_node(str_id, value=station)
    log.debug("Creating cross nodes")
    for str_id, cross in crosses.items():
        graph.add_node(str_id, value=cross)

    log.debug("Creating edges")
    for str_id, cross in crosses.items():
        if cross.get_n() is not None:
            graph.add_edge(str_id, cross.get_n())
        if cross.get_s() is not None:
            graph.add_edge(str_id, cross.get_s())
        if cross.get_w() is not None:
            graph.add_edge(str_id, cross.get_w())
        if cross.get_e() is not None:
            graph.add_edge(str_id, cross.get_e())

    log.debug("Finding shortest paths")
    shortest_paths = nx.shortest_path(graph)

    log.info("Processing crosses")
    crosses_directions = dict()
    for str_id, cross in crosses.items():
        crosses_directions[str_id] = process_cross_direction_addresses(cross, shortest_paths, stations, crosses)
    log.info("Done processing crosses directions")

    log.info("Generating commands")
    crosses_commands = dict()
    for str_id, cross in crosses.items():
        crosses_commands[str_id] = generate_commands(cross, crosses_directions[str_id])

    log.debug("Crosses commands: %s", crosses_commands)

    return crosses_commands

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

process(stationsData, crossesData)

log.info('Done')
