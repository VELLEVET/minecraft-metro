"""
One cross' direction address merger

Merges similar addresses in similar cross' direction
"""


import core.address_util as address_util


def merge_addresses(address_dirs, paths):
    """

    :param address_dirs:
    :param paths:
    :return:
    """

    result = dict()

    for cid, dirs in address_dirs.items():
        result[cid] = dict()

        for d, addrs in dirs.items():
            result[cid][d] = dict()

            for data in addrs:
                dist = len(paths[cid][data['id']])
                addr_encoded = address_util.addr_to_str(data['address'])

                if addr_encoded not in result[cid][d].keys() or result[cid][d][addr_encoded] < dist:
                    result[cid][d][addr_encoded] = dist

    return result