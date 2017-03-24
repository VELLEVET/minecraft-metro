"""
Directions address array merger

Merges directions addresses array with specific format
"""


def merge(a: dict, b: dict):
    """
    Merge two directions addresses dicts
    :rtype: dict
    :param a: Directions addresses dict
    :param b: Other directions addresses dict
    :return: Merged directions addresses dict
    """

    result = a.copy()

    for cid, cdata in b.items():
        if cid not in result.keys():
            result[cid] = dict()

        for d, addresses in cdata.items():
            if d not in result[cid]:
                result[cid][d] = list()

            result[cid][d] += addresses

    return result