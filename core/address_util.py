"""
Address utils
"""


def addr_to_str(addr: list):
    """
    Converts address list to address string

    :rtype: str
    :param addr: Address list
    :return: Address string
    """
    result = str()

    for l in addr:
        result += str(l)

    return result


def str_to_addr(addr: str):
    """
    Converts address string to address list

    :rtype: list
    :param addr: Address string
    :return: Address list
    """
    
    result = list()

    for l in addr:
        result += [int(l)]

    return result
