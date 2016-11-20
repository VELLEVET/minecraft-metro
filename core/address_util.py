"""
Address utils
"""


def addr_to_str(addr):
    """
    Converts address list to address string

    :param addr: Address list
    :return: Address string
    """
    result = ''

    for l in addr:
        result += str(l)

    return result