# -*- coding: utf-8 -*-
# Copyright 2007-2025 The HyperSpy developers
#
# This file is part of RosettaSciIO.
#
# RosettaSciIO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RosettaSciIO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RosettaSciIO. If not, see <https://www.gnu.org/licenses/#GPL>.


import os
from datetime import datetime

import numpy as np

from rsciio._docstrings import FILENAME_DOC, LAZY_UNSUPPORTED_DOC, RETURNS_DOC


def _cnv_time(timestr):
    try:
        if not isinstance(timestr, str):
            # for numpy < 2.0
            timestr = timestr.decode()
        t = datetime.strptime(timestr, "%H:%M:%S.%f")
        dt = t - datetime(t.year, t.month, t.day)
        r = float(dt.seconds) + float(dt.microseconds) * 1e-6
    except ValueError:
        r = float(timestr)
    return r


def _bad_file(filename):
    raise AssertionError("Cannot interpret as DENS heater log: %s" % filename)


def file_reader(filename, lazy=False):
    """
    Read a DENSsolutions DigiHeater logfile.

    Parameters
    ----------
    %s
    %s

    %s
    """
    if lazy is not False:
        raise NotImplementedError("Lazy loading is not supported.")

    with open(filename, "rt") as f:
        # Strip leading, empty lines
        line = str(f.readline())
        while line.strip() == "" and not f.closed:
            line = str(f.readline())
        try:
            date, version = line.split("\t")
        except ValueError:
            _bad_file(filename)
        if version.strip() != "Digiheater 3.1":
            _bad_file(filename)
        calib = str(f.readline()).split("\t")
        str(f.readline())  # delta_t
        header_line = str(f.readline())
        try:
            R0, a, b, c = [float(v.split("=")[1]) for v in calib]
            date0 = datetime.strptime(date, "%d/%m/'%y %H:%M")
            date = "%s" % date0.date()
            time = "%s" % date0.time()
        except ValueError:
            _bad_file(filename)
        original_metadata = dict(R0=R0, a=a, b=b, c=c, date=date0, version=version)

        if header_line.strip() != (
            "sample\ttime\tTset[C]\tTmeas[C]\tRheat[ohm]\tVheat[V]\t"
            "Iheat[mA]\tPheat [mW]\tc"
        ):
            _bad_file(filename)
        try:
            rawdata = np.loadtxt(
                f, converters={1: _cnv_time}, usecols=(1, 3), unpack=True
            )
        except ValueError:
            _bad_file(filename)

    times = rawdata[0]
    # Add a day worth of seconds to any values after a detected rollover
    # Hopefully unlikely that there is more than one, but we can handle it
    for rollover in 1 + np.where(np.diff(times) < 0)[0]:
        times[rollover:] += 60 * 60 * 24
    # Raw data is not necessarily grid aligned. Interpolate onto grid.
    offset, scale = np.polynomial.polynomial.polyfit(
        np.arange(times.size), times, deg=1
    )

    metadata = {
        "General": {
            "original_filename": os.path.split(filename)[1],
            "date": date,
            "time": time,
        },
        "Signal": {"signal_type": "", "quantity": "Temperature (Celsius)"},
    }

    axes = [
        {
            "size": times.size,
            "index_in_array": 0,
            "name": "Time",
            "scale": scale,
            "offset": offset,
            "units": "s",
            "navigate": False,
        }
    ]

    dictionary = {
        "data": rawdata[1],
        "axes": axes,
        "metadata": metadata,
        "original_metadata": {"DENS_header": original_metadata},
    }

    return [
        dictionary,
    ]


file_reader.__doc__ %= (FILENAME_DOC, LAZY_UNSUPPORTED_DOC, RETURNS_DOC)
