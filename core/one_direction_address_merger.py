"""
One cross' direction address merger

Merges similar addresses in similar cross' direction
"""


def merge_addresses(address_dirs: dict, paths: dict):
    """
    Merges similar addresses in single cross' direction

    Selects shortest path to specified address

    :rtype: dict
    :param address_dirs: Addresses directions
    :param paths: Shortest paths
    :return: Addresses directions with merged addresses in single cross' direction
    """

    result = dict()

    for cid, dirs in address_dirs.items():
        result[cid] = dict()

        for d, addrs in dirs.items():
            result[cid][d] = dict()

            for data in addrs:
                dist = len(paths[cid][data['id']])
                addr_encoded = data['address']

                if addr_encoded not in result[cid][d].keys() or result[cid][d][addr_encoded]['distance'] < dist:
                    result[cid][d][addr_encoded] = {
                        'distance': dist,
                        'id': data['id']
                    }

    return result
