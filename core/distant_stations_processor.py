"""
Distant station processor

Generates list of directions with cross' distant connected stations
"""


def process(stations_and_crosses, paths):
    """
    Process crosses' distant connected stations

    :param stations_and_crosses: Stations and crosses dict
    :param paths: Shortest paths dict
    :return: Crosses' directions dict containing distant connected stations
    """

    directions = dict()

    for cid, cross in stations_and_crosses['crosses'].items():
        directions[cid] = dict()

        for sid, station in stations_and_crosses['stations'].items():
            path = paths[cid][sid]
            direct = path[1]

            if direct == sid:
                continue

            for d, data in cross['connections'].items():
                if data['id'] == direct:
                    if d not in directions[cid].keys():
                        directions[cid][d] = list()

                    directions[cid][d] += [sid]

                    break

    return directions
