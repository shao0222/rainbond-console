#!/usr/bin/env python
# -*- coding: utf8 -*-
from compose import config
from compose.config.environment import Environment
import os
import logging

logger = logging.getLogger('default')

def get_config_path_from_options(options, environment):
    file_option = options.get('--file')
    if file_option:
        return file_option

    config_files = environment.get('COMPOSE_FILE')
    if config_files:
        return config_files.split(os.pathsep)
    return None


def parse_compose(file_dir, file_name=None):
    options = {}
    if file_name is not None:
        options["--file"] = [file_name]
    environment = Environment.from_env_file(file_dir)
    config_path = get_config_path_from_options(options, environment)
    return config.load(
        config.find(file_dir, config_path, environment)
    )

