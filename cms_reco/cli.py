#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of reana.
# Copyright (C) 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Reana workflow factory cli."""


import os

import click
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from .utils import (compute_backends, get_config_from_json,
                    load_config_from_cod, valid_run_years, workflow_engines)


@click.group()
def cms_reco():
    """Info."""
    pass


@click.option('--config_file',
              default='cms_reco/cms-reco-config.json',
              help='recid for the data set to be reconstructed')
@click.option('--recid',
              help='recid for the data set to be reconstructed')
@cms_reco.command()
def load_config(recid, config_file):
    """Download config file using the cern open data client."""
    load_config_from_cod(recid, config_file)
    print("Downloaded config file from cod as {}.".format(config_file))


@click.option('--compute_backend',
              default='kubernetes',
              help='compute backend to be used',
              type=click.Choice(compute_backends))
@click.option('--dataset',
              default="DoubleElectron",
              help='data set to be reconstructed')
@click.option('--directory',
              default='',
              help='directory for the analysis to be executed')
@click.option('--nevents',
              default='1',  # ToDo: change to "-1" for full data set reco
              help='number of events to be reconstructed')
@click.option('--workflow_engine',
              default='serial',
              help='workflow engine to be used',
              type=click.Choice(workflow_engines))
@click.option('--year',
              default="2011",
              help='year the data set was recorded',
              type=click.Choice(valid_run_years)
              )
@cms_reco.command()
def create_workflow(compute_backend, dataset, directory, nevents,
                    workflow_engine, year):
    """Create workflow from given parameters."""
    template_path = "{}/cms_reco/cookiecutter_template/workflow_factory/{}"\
        .format(os.getcwd(), workflow_engine)

    # Set COD configs
    config = get_config_from_json()

    if config['error']:
        print(config['error'])
    else:

        # Set REANA (non-COD) related configs
        config['compute_backend'] = compute_backend

        # Set optional configs
        if nevents:
            config['nevents'] = nevents
        if directory:
            config['directory_name'] = directory

        try:
            cookiecutter(template_path, no_input=True, extra_context=config)
        except OutputDirExistsException:
            print("Output Directory already exists, please choose a different "
                  "name or rename the existing one.")
        print("Created `{0}` directory.".format(config["directory_name"]))