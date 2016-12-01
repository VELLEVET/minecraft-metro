"""
Directions array merger

Merges directions array with specific format
"""


def merge(a: dict, b: dict):
    """
    Merge two directions dicts

    :rtype: dict
    :param a: Directions dict
    :param b: Other directions dict
    :return: Merged directions dict
    """

    result = a.copy()

    for cid, data in result.items():
        for d, stations in data.items():
            if isinstance(stations, str):
                result[cid][d] = [stations]

    for cid, data in b.items():
        if cid not in result.keys():
            result[cid] = dict()

        for d, stations in data.items():
            if d not in result[cid]:
                result[cid][d] = list()

            if isinstance(stations, str):
                result[cid][d] += [stations]
            else:
                result[cid][d] += stations

    return result
