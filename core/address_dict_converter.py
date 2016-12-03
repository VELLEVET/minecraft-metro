"""
Address dict converter module

Converts dict with stations' addresses stored as 'address' => 'direction' to 'direction' => ['address', 'address', ...]
"""


def convert(address_dict: dict):
    """
    Converts stations' directions and addresses dict

    :rtype: dict
    :param address_dict: Address dict like 'address' => 'direction'
    :return: Address dict like 'direction' => ['address', 'address', ...]
    """
    result = dict()

    for cid, data in address_dict.items():
        result[cid] = dict()

        for addr, adata in data.items():
            d = adata['direction']
            if d not in result[cid]:
                result[cid][d] = list()

            result[cid][d] += [addr]

    return result
