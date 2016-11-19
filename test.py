import logging
import os
import json

import core.csv_converter as csv_converter
import core.graph_builder as graph_builder
import core.connected_stations_processor as connected_stations_processor


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

converted_file = open('temp/converted.json', 'w')
converted_file.write(json.dumps(stations_and_crosses_dict, indent='    ', ensure_ascii=False, sort_keys=True))
converted_file.close()

log.info('Saved dict as JSON to temp/converted.json')

graph = graph_builder.build_graph(stations_and_crosses_dict)

log.info('Built graph')

paths = graph_builder.find_paths(graph)

log.info('Found shortest paths')

shortest_paths_file = open('temp/shortest_paths.json', 'w')
shortest_paths_file.write(json.dumps(paths, indent='    ', ensure_ascii=False, sort_keys=True))
shortest_paths_file.close()

log.info('Saved shortest paths as JSON to temp/shortest_paths.json')

directions = connected_stations_processor.process(stations_and_crosses_dict)

log.info('Processed crosses\' directly connected stations')

connected_stations_file = open('temp/connected_stations.json', 'w')
connected_stations_file.write(json.dumps(directions, indent='    ', ensure_ascii=False, sort_keys=True))
connected_stations_file.close()

log.info('Saved crosses\' directly connected stations JSON to temp/connected_stations.json')

