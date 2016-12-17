"""
Address range builder

Merges adjacent addresses of cross direction into one range
E.g. 0 and 1 merges into range 0 - 1
"""


import core.address_util as address_util


def build(directions_addresses: dict):

    result = dict()

    for cid, cdata in directions_addresses.items():
        result[cid] = dict()
        for d, addrs in cdata.items():
            result[cid][d] = list()
            processed = list()

            for addr in addrs:
                if addr in processed:
                    continue

                built = False
                min_l = address_util.addr_last_level(addr)
                max_l = address_util.addr_last_level(addr)

                for oaddr in addrs:
                    if oaddr == addr:
                        continue
                    if len(oaddr) != len(addr):
                        continue
                    if oaddr[:-1] != addr[:-1]:
                        continue

                    ll = address_util.addr_last_level(oaddr)

                    if min_l - ll == 1:
                        built = True
                        min_l = ll
                        processed += [oaddr]

                    if ll - max_l == 1:
                        built = True
                        max_l = ll
                        processed += [oaddr]

                if built:
                    result[cid][d] += [{
                        'common': addr[:-1],
                        'min': min_l,
                        'max': max_l
                    }]
                else:
                    result[cid][d] += [addr]



    return result
