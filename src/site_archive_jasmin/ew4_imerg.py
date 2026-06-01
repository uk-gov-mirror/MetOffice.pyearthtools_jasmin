# (C) British Crown Copyright 2017-2026, Met Office.
# Please see LICENSE.md for license details.

import pathlib
import datetime


import pyearthtools.data as petdata
import pyearthtools.pipeline as petpipe

from pyearthtools.data import Petdt
from pyearthtools.data.exceptions import DataNotFoundError
from pyearthtools.data.indexes import ArchiveIndex, FileSystemIndex, decorators
from pyearthtools.data.transforms import Transform, TransformCollection
from pyearthtools.data.archive import register_archive
from pyearthtools.data.time import TimeDelta

from site_archive_jasmin.utilities import (
    cached_exists,
    cached_iterdir,
)  
def get_imerg_path(start_dt, time_delta, fname_template, data_dir):
    day_minutes = start_dt.hour * 60 + start_dt.minute
    date_str = '{dt.year:04d}{dt.month:02d}{dt.day:02d}'.format(dt=start_dt)
    time_template = '{dt.hour:02d}{dt.minute:02d}{dt.second:02d}'
    start_time = time_template.format(dt=start_dt)
    end_time = time_template.format(dt=start_dt+time_delta-datetime.timedelta(seconds=1))
    imerg_path = data_dir / fname_template.format(date_str=date_str,
                                              start_time=start_time,
                                              end_time=end_time,
                                                  day_minutes=day_minutes,
                                             )
    return imerg_path


def date_matches(datetime1, datetime2):
    if datetime1.year != datetime2.year:
        return False
    if datetime1.month != datetime2.month:
        return False
    if datetime1.day != datetime2.day:
        return False
    if datetime1.hour != datetime2.hour:
        return False
        
    return True



@register_archive("ew4_imerg_2025", sample_kwargs=dict())
class Ew4Imerg(ArchiveIndex):
    """PyEarthTools accessor to access the version of GPM IMERG prepared for the EW4Energy project"""

    imerg_fname_template = '3B-HHR-E.MS.MRG.3IMERG.{date_str}-S{start_time}-E{end_time}.{day_minutes:04d}.V07B.HDF5.SUB.nc4'
    # ew4_imerge_res = (30, "m")
    ew4_imerge_res = (1, "hour")
    @property
    def _desc_(self):
        return {
            "singleline": "GPM IMERG - EW4Energy project ",
            "range": "2025-04-01 to 2025-09-30",
            "Documentation": "https://gpm.nasa.gov/data/imerg",
        }

    def __init__(
        self,
        start: datetime.datetime | str,
        end: datetime.datetime | str,

        *,
        transforms: Transform | TransformCollection | None = None,
    ):
        """
        Doc string for init function
        """

        if type(start) is not datetime.datetime:
            self._start = datetime.datetime.fromisoformat(start)
        else:
            self._start = datetime.datetime(start)

        if type(end) is not datetime.datetime:
            self._end = datetime.datetime.fromisoformat(end)
        else:
            self._end = datetime.datetime(end)
        self._time_delta=datetime.timedelta(minutes=30)        


        # call the base class
        super().__init__(
            transforms=transforms,
            data_interval=Ew4Imerg.ew4_imerge_res,
        )
        self.record_initialisation()

    def filesystem(
        self,
        querytime: str | Petdt,
    ) -> pathlib.Path | dict[str, str ]:

        paths = []
        querytime = Petdt(querytime)
        if querytime > Petdt(self._end) or querytime < Petdt(self._start):
            raise DataNotFoundError('Query time is outside the range of data')
        
        

        ew4_imerg_dir = pathlib.Path(self.ROOT_DIRECTORIES['ew4_imerg_precip'])

      
        paths += [get_imerg_path(querytime,
                                           self._time_delta,
                                           Ew4Imerg.imerg_fname_template,
                                           ew4_imerg_dir
                                          )]

        return paths

