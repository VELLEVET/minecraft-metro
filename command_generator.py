from path_builder import decode_range


def generate_way_command(cross, address, log, direction):
    directions_data = {
        'n': {
            's': {
                'rail': {'x': -1, 'z': 3},
                'detect': {'x': -3, 'z': 3},
                'rail_direction': 7
            },
            'w': {
                'rail': {'x': -5, 'z': 0},
                'detect': {'x': -3, 'z': 0},
                'rail_direction': 1
            },
            'e': {
                'rail': {'x': 4, 'z': 3},
                'detect': {'x': 1, 'z': 3},
                'rail_direction': 1
            }
        },
        's': {
            'n': {
                'rail': {'x': 1, 'z': -2},
                'detect': {'x': 3, 'z': -2},
                'rail_direction': 9
            },
            'w': {
                'rail': {'x': -5, 'z': -2},
                'detect': {'x': -3, 'z': -2},
                'rail_direction': 1
            },
            'e': {
                'rail': {'x': 4, 'z': 1},
                'detect': {'x': 2, 'z': 1},
                'rail_direction': 1
            }
        },
        'w': {
            'n': {
                'rail': {'x': 2, 'z': -4},
                'detect': {'x': 2, 'z': -2},
                'rail_direction': 0
            },
            's': {
                'rail': {'x': -1, 'z': 5},
                'detect': {'x': -1, 'z': 3},
                'rail_direction': 0
            },
            'e': {
                'rail': {'x': 2, 'z': -2},
                'detect': {'x': 2, 'z': -4},
                'rail_direction': 6
            }
        },
        'e': {
            'n': {
                'rail': {'x': 0, 'z': -4},
                'detect': {'x': 0, 'z': -2},
                'rail_direction': 0
            },
            's': {
                'rail': {'x': -3, 'z': 5},
                'detect': {'x': -3, 'z': 2},
                'rail_direction': 0
            },
            'w': {
                'rail': {'x': -3, 'z': 0},
                'detect': {'x': -3, 'z': -2},
                'rail_direction': 8
            }
        },
        'quad': {
            'n': {
                'rail': {'x': 0, 'z': 0},
                'detect': {'x': 0, 'z': 0},
                'rail_direction': 0
            },
            's': {
                'rail': {'x': 0, 'z': 0},
                'detect': {'x': 0, 'z': 0},
                'rail_direction': 0
            },
            'w': {
                'rail': {'x': 0, 'z': 0},
                'detect': {'x': 0, 'z': 0},
                'rail_direction': 0
            },
            'e': {
                'rail': {'x': 0, 'z': 0},
                'detect': {'x': 0, 'z': 0},
                'rail_direction': 0
            }
        }
    }
    r = 2
    y = 33
    score_prefix = 'score_metro_st_l_%i'
    score_min_postfix = '_min'

    connections = cross['connections']

    if len(connections) < 3:
        log.warning('Cross %s connections length is lesser than 3' % cross['name'])

    x = cross['x']
    z = cross['z']

    rx = x
    ry = y
    rz = z

    bx = x
    by = y
    bz = z

    if 'n' not in connections:
        data = directions_data['n'][direction]
    elif 's' not in connections:
        data = directions_data['s'][direction]
    elif 'w' not in connections:
        data = directions_data['w'][direction]
    elif 'e' not in connections:
        data = directions_data['e'][direction]
    else:
        data = directions_data['quad'][direction]

    # Offsets to switching rail from cross position
    rx += data['rail']['x']
    rz += data['rail']['z']

    # Offsets to detector rail from cross position
    bx += data['detect']['x']
    bz += data['detect']['z']

    rd = data['rail_direction']

    scores_list = []
    for i in range(len(address)):
        l = address[i]
        if l < 10:
            scores_list += [score_prefix % i + '=%i' % l]
            scores_list += [score_prefix % i + score_min_postfix + '=%i' % l]
        else:
            r_min, r_max = decode_range(l)
            scores_list += [score_prefix % i + '=%i' % r_min]
            scores_list += [score_prefix % i + score_min_postfix + '=%i' % r_max]

    scores = ','.join(scores_list)

    template = "/execute @p[x=%i,y=%i,z=%i,r=%i,%s] ~ ~ ~ setblock %i %i %i minecraft:rail %i"
    template = template % (bx, by, bz, r, scores, rx, ry, rz, rd)

    return template
