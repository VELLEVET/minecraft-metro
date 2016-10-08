"""
CSV converter module.

Converts stations and crosses CSV files.
"""


def convert(stations: str, crosses: str):
    """
    Convert given CSV strings to stations and crosses dict

    :param stations: Stations CSV
    :param crosses: Crosses CSV
    :return: Stations and crosses dict
    """
    stations_dict = dict()
    for line in stations.split('\n')[1:]:
        cols = line.split(',')

        row = dict()
        row['number'] = cols[0]
        row['label'] = cols[1]
        row['address'] = list()

        for l in cols[2].split('-'):
            row['address'].append(int(l))

        row['id'] = 's' + str(row['number'])
        row['cross_id'] = 'c' + cols[3]

        stations_dict[row['id']] = row

    crosses_dict = dict()
    for line in crosses.split('\n')[1:]:
        cols = line.split(',')

        row = dict()
        row['number'] = cols[0]
        row['address'] = list()

        for l in cols[1].split('-'):
            row['address'].append(int(l))

        row['id'] = 'c' + str(row['number'])

        dirs = dict()

        for d in ['n', 's', 'e', 'w']:
            col = {'n': 2, 's': 3, 'w': 4, 'e': 5}[d]
            dir = cols[col]
            if dir == '-':
                continue
            dirs[d] = dict()
            dirs[d]['type'] = dir[0:1]
            dirs[d]['number'] = dir[1:]
            dirs[d]['id'] = dir

        row['connections'] = dirs
        row['x'] = int(cols[6])
        row['z'] = int(cols[7])

        crosses_dict[row['id']] = row

    result = dict()
    result['stations'] = stations_dict
    result['crosses'] = crosses_dict

    return result
