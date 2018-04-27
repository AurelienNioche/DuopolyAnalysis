# SpatialCompetition
# Copyright (C) 2018  Aurélien Nioche, Basile Garcia & Nicolas Rougier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing as mlt
import tqdm
import os
import numpy as np

import simulation.model as model

import simulation.backup as backup
import simulation.parameters as parameters


def get_heutistics():
    return model.get_heuristics()


def run(param):

    m = model.Model(param)
    return m.run()


def produce_data(parameters_file, data_file):

    """
    Produce data for 'pooled' condition using multiprocessing
    :param parameters_file: Path to parameters file (string)
    :param data_file: Path to the future data files (dictionary with two entries)
    :return: a 'pool backup' (arbitrary Python object)
    """

    json_parameters = parameters.load(parameters_file)

    pool_parameters = parameters.extract_parameters(json_parameters)

    pl = mlt.Pool()

    backups = []

    for bkp in tqdm.tqdm(
            pl.imap_unordered(run, pool_parameters),
            total=len(pool_parameters)):
        backups.append(bkp)

    pool_backup = backup.PoolBackup(parameters=json_parameters, backups=backups)
    pool_backup.save(parameters_file, data_file)

    return pool_backup


def data_already_produced(*args):

    """
    If data files already exist, return True
    :param args: Path to data files
    :return: True or False
    """
    return np.all([os.path.exists(i) for i in args])


def pool(force=False):

    heuristics = model.get_heuristics()

    backups = {}

    for h in heuristics:

        parameters_file = "simulation/results/json/pool_{}.json".format(h)
        data_file = "simulation/results/pickle/pool_{}.p".format(h)

        if not data_already_produced(data_file) or force:
            pool_backup = produce_data(parameters_file, data_file)

        else:
            pool_backup = backup.PoolBackup.load(data_file)

        backups[h] = pool_backup

    return backups


def batch(force=False):

    heuristics = model.get_heuristics()

    backups = {}

    for h in heuristics:

        parameters_file = "simulation/results/json/batch_{}.json".format(h)
        data_file = "simulation/results/pickle/batch_{}.p".format(h)

        if not data_already_produced(data_file) or force:
            batch_backup = produce_data(parameters_file, data_file)

        else:
            batch_backup = backup.PoolBackup.load(data_file)

        backups[h] = batch_backup

    return backups


def individual(force=False):

    heuristics = model.get_heuristics()

    backups = {i: dict() for i in heuristics}

    for h in heuristics:

        for r in ("25", "50"):

            parameters_file = "simulation/results/json/{}_{}.json".format(r, h)
            data_file = "simulation/results/pickle/{}_{}.p".format(r, h)

            if not data_already_produced(parameters_file, data_file) or force:

                json_parameters = parameters.load(parameters_file)
                param = parameters.extract_parameters(json_parameters)
                run_backup = run(param)
                run_backup.save(parameters_file, data_file)

            else:
                run_backup = backup.RunBackup.load(data_file)

            backups[h][r] = run_backup

    return backups
