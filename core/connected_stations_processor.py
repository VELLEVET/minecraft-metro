"""
Connected stations processor

Generates list of directions with cross' directly connected stations
"""


def process(stations_and_crosses: dict):
    """
    Finds crosses' directly connected stations

    :rtype: dict
    :param stations_and_crosses:  Stations and crosses dict
    :return: Crosses' directions dict containing directly connected stations
    """

    directions = dict()

    for id, cross in stations_and_crosses['crosses'].items():
        directions[id] = dict()
        for d, params in cross['connections'].items():
            if params['type'] == 's':
                directions[id][d] = params['id']

    return directions
