import logging
import os
import json

import core.csv_converter as csv_converter
import core.graph_builder as graph_builder
import core.connected_stations_processor as connected_stations_processor
import core.distant_stations_processor as distant_stations_processor
import core.directions_array_merger as directions_array_merger
import core.station_to_address_converter as station_to_address_converter
import core.one_direction_address_merger as one_direction_address_merger


def initialize_logger():
    """
    Initializes logger and returns it
    """
    logger = logging.getLogger('RoutingTest')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] [%(name)s.%(levelname)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    error_file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'temp/logs/test.error.log'), 'w', delay=True)
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    debug_file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'temp/logs/test.debug.log'), 'w', delay=True)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    logger.addHandler(debug_file_handler)

    return logger


def save_json(filename, data, comment:str):
    file = open('temp/' + filename + '.json', 'w')
    file.write(json.dumps(data, indent='    ', ensure_ascii=False, sort_keys=True))
    file.close()

    log.info('Saved ' + comment.lower() + ' as JSON to temp/' + filename + '.json')

log = initialize_logger()


stations_file_name = 'stations.csv'
crosses_file_name = 'crosses.csv'

log.info('Starting')

stations_file = open(stations_file_name, 'r')
stations_csv = stations_file.read()
stations_file.close()

crosses_file = open(crosses_file_name, 'r')
crosses_csv = crosses_file.read()
crosses_file.close()

log.info('Opened stations and crosses CSV files')

stations_and_crosses_dict = csv_converter.convert(stations_csv, crosses_csv)

log.info('Converted CSV to dict')

save_json('converted', stations_and_crosses_dict, 'dict')

graph = graph_builder.build_graph(stations_and_crosses_dict)

log.info('Built graph')

paths = graph_builder.find_paths(graph)

log.info('Found shortest paths')

save_json('shortest_paths', paths, 'shortest paths')

directions_connected = connected_stations_processor.process(stations_and_crosses_dict)

log.info('Processed crosses\' directly connected stations')

save_json('connected_stations', directions_connected, 'crosses\' directly connected stations')

directions_distant = distant_stations_processor.process(stations_and_crosses_dict, paths)

log.info('Processed crosses\' distant connected stations')

save_json('distant_stations', directions_distant, 'crosses\' distant stations')

directions_stations = directions_array_merger.merge(directions_connected, directions_distant)

save_json('directions_stations', directions_stations, 'crosses\' stations directions')

address_dirs = station_to_address_converter.convert_stations_to_addresses(directions_stations, stations_and_crosses_dict)

log.info('Converted stations directions to address directions')

save_json('directions_addresses', address_dirs, 'crosses\' addresses directions')

merged_one = one_direction_address_merger.merge_addresses(address_dirs, paths)

log.info('Merged one direction addresses')

save_json('one_direction_merged', merged_one, 'one direction merged addresses')