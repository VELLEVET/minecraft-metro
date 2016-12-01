"""
Directions' stations to address converter

Converts directions dict to address dict
"""


def get_common_address_part(base, other):
    """
    Returns common address part including first different level

    :param base: Base address
    :param other: Other address
    :return: Common address part
    """

    result = str()
    for i in range(0, min(len(base), len(other))):
        b = base[i]
        o = other[i]

        result += str(o)

        if b != o:
            break

    return result


def convert_stations_to_addresses(directions, stations_and_crosses):
    """

    :param directions:
    :param stations_and_crosses:
    :return:
    """

    result = dict()

    for cid, dirs in directions.items():
        result[cid] = dict()

        base_addr = stations_and_crosses['crosses'][cid]['address']

        for d, stations in dirs.items():
            result[cid][d] = list()

            for s in stations:
                other_addr = stations_and_crosses['stations'][s]['address']
                common_addr = get_common_address_part(base_addr, other_addr)

                result[cid][d] += [{
                    'id': s,
                    'address': common_addr
                }]

    return result