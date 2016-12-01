"""
Multiple cross' directions address merger

Merges similar addresses in multiple cross' directions
"""


def merge_addresses(address_dirs: dict, stations_and_crosses: dict):
    """
    Merges similar addresses in mutiple cross' directions

    Selects shortest path to specified address

    :rtype: dict
    :param stations_and_crosses: Stations and crosses dict
    :param address_dirs: Addresses directions
    :return: Addresses directions with merged addresses in multiple cross' directions
    """

    result = dict()

    for cid, dirs in address_dirs.items():
        result[cid] = dict()
        for d, addrs in dirs.items():
            for addr, data in addrs.items():
                if addr in result[cid]:
                    if result[cid][addr]['length'] == data['distance']:
                        # Calculate Manhattan distance
                        do = result[cid][addr]['direction']
                        so = stations_and_crosses['stations'][data['id']]
                        co = stations_and_crosses['crosses'][so['cross_id']]

                        c = stations_and_crosses['crosses'][cid]

                        x = c['x']
                        z = c['z']
                        xo = co['x']
                        zo = co['z']

                        dist = abs(xo - x) + abs(zo - z)

                        if 'mh_dist' not in result[cid][addr] or result[cid][addr]['mh_dist'] < data['mh_dist']:
                            result[cid][addr] = {
                                'direction': do,
                                'length': data['distance'],
                                'mh_dist': dist
                            }

                        continue
                    elif result[cid][addr]['length'] < data['distance']:
                        continue

                result[cid][addr] = {
                    'direction': d,
                    'length': data['distance']
                }

    return result
