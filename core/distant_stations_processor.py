"""
Distant station processor

Generates list of directions with cross' distant connected stations
"""


def find_crosses_or_stations_by_addr(addr: str, stations_and_crosses: dict):
    result = list()

    for cid, cross in stations_and_crosses['crosses'].items():
        if cross['address'][:len(addr)] == addr:
            result += [cid]

    for sid, station in stations_and_crosses['stations'].items():
        if station['address'][:len(addr)] == addr:
            result += [station['cross_id']]

    return result


def nearest_station_or_cross(src_id, dst_ids, paths):
    result_id = ''
    result_distance = -1

    for dst_id in dst_ids:
        path = paths[src_id][dst_id]
        dst = len(path)

        if dst < result_distance or result_distance == -1:
            result_id = dst_id
            result_distance = dst

    return result_id


def process(stations_and_crosses: dict, paths: dict):
    """
    Process crosses' distant connected stations

    :rtype: dict
    :param stations_and_crosses: Stations and crosses dict
    :param paths: Shortest paths dict
    :return: Crosses' directions dict containing distant connected stations addresses
    """

    qnames = ['0', '1', '2', '3']

    directions = dict()

    for cid, cross in stations_and_crosses['crosses'].items():
        directions[cid] = dict()

        l = -1
        for a in cross['address']:
            l += 1
            prefix = cross['address'][:l]

            for q in qnames:
                if q == a:
                    continue

                addr = prefix + q

                stations_or_crosses = find_crosses_or_stations_by_addr(addr, stations_and_crosses)

                if len(stations_or_crosses) == 0:
                    continue

                nearest = nearest_station_or_cross(cid, stations_or_crosses, paths)

                if nearest == cid:
                    continue

                direct = paths[cid][nearest][1]

                for d, conn in cross['connections'].items():
                    if conn['id'] == direct:
                        direction = d
                        break

                if direction not in directions[cid].keys():
                    directions[cid][direction] = list()

                directions[cid][direction] += [{
                    'address': addr,
                    'direct': direct,
                    'nearest': nearest,
                    'id': nearest
                }]

    return directions
