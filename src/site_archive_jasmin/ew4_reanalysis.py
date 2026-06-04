# (C) British Crown Copyright 2017-2026, Met Office.
# Please see LICENSE.md for license details.

"""
Pyearthtools dataset accessor on JASMIN for the Mera2 Reanalsysis subset for the EW4Energy project.

"""

from __future__ import annotations

import pathlib
import functools

import numpy

import pyearthtools.data

from pyearthtools.data import Petdt
from pyearthtools.data.indexes import ArchiveIndex
from pyearthtools.data.transforms import Transform, TransformCollection
from pyearthtools.data.archive import register_archive

from site_archive_jasmin.utilities import (
    cached_exists,
    cached_iterdir,
)  # Could these be moved into a generic module?


def _construct_merra2_aero_path(root_dir, template_str, querytime):
    path = root_dir / f'{querytime.year:04d}' / template_str.format(dt=querytime)
    return path

def _construct_merra2_meteo_path(root_dir, template_str, querytime):
    path = root_dir / f'{querytime.year:04d}' / template_str.format(dt=querytime)
    return path

AERO_VARS = [
    'AIRDENS',
    'BCPHILIC',
    'BCPHOBIC',
    'DELP',
    'DMS',
    'DU001',
    'DU002',
    'DU003',
    'DU004',
    'DU005',
    'LWI',
    'MSA',
    'OCPHILIC',
    'OCPHOBIC',
    'PS',
    'RH',
    'SO2',
    'SO4',
    'SS001',
    'SS002',
    'SS003',
    'SS004',
    'SS005',
]

METEO_VARS = [
    'T2M', 
    'U10M', 
    'U2M', 
    'V10M', 
    'V2M',
]
MERRA2_VARS = AERO_VARS + METEO_VARS


class MeteoHourFix(pyearthtools.data.transform.Transform):
    def __init__(self):
        pass

    def apply(self, ds):
        ds['time'] = [v1.values - numpy.timedelta64(30,'m') for v1 in ds['time']]
        return ds

class Ew4Merra2(ArchiveIndex):
    """Description of dataset"""
    meteo_fname_template = 'MERRA2_400.tavg1_2d_slv_Nx.{dt.year:04d}{dt.month:02d}{dt.day:02d}.SUB.nc'
    aero_fname_template = 'MERRA2_400.inst3_3d_aer_Nv.{dt.year:04d}{dt.month:02d}{dt.day:02d}.SUB.nc'
    ew4_merra2_interval = '1 hour'
    aero_vars = AERO_VARS
    meteo_vars = METEO_VARS
 
    @property
    def _desc_(self):
        return {
            "singleline": "MERRA2 ",
            "range": "2019 to 2025",
            "Documentation": "https://gmao.gsfc.nasa.gov/gmao-products/merra-2/",
        }

    def __init__(
        self,
        variables: list[str] | str,
        *,
        transforms: Transform | TransformCollection | None = None,
    ):
        """
        Init function for Merra2 accessor base class.
        """
        self._variables = variables
        super_transforms = TransformCollection([pyearthtools.data.transforms.variables.Trim(self._variables),]) + transforms
        
        # call the base class
        super().__init__(
            transforms=super_transforms,
            data_interval=Ew4Merra2.ew4_merra2_interval,
        )
        self.record_initialisation()

    def filesystem(
        self,
        querytime: str | Petdt,
    ) -> pathlib.Path | dict[str, str | pathlib.Path]:
        

        querytime = Petdt(querytime)
        paths = []
        

        for var_name in self._variables:
            try:
                paths += [self._var_path_lookup(querytime=querytime)]
            except KeyError:
                print(f'Non data for var {var_name}')
        #remove duplicate paths, which will be created from selecting aero and meteo variables.
        paths = list(set(paths))
        
        return paths

@register_archive("ew4_merra2_aero", sample_kwargs=dict(variable="SO2"))
class Ew4Merra2Aero(Ew4Merra2):
    def __init__(
        self,
        variables: list[str] | str,
        *,
        transforms: Transform | TransformCollection | None = None,
    ):

        # check list of variables against valid ones
        filtered_vars = [var1 for var1 in variables if var1 in AERO_VARS]
        
        if len(filtered_vars) == 0:
            raise DataError('Not valid variables selected')
        
        if len(filtered_vars) != len(variables):
            print('The following variables were selected but are not present in the dataset and rejected:\n', 
                  '\n'.join(var1 for var1 in variables if var1 not in AERO_VARS))
        else:
            print('All selected variables present in the dataset.')
            
        
        self._aero_dir = pathlib.Path(self.ROOT_DIRECTORIES['ew4_merra2_aero'])
        
        self._var_path_lookup = functools.partial(_construct_merra2_aero_path, 
                                             root_dir=self._aero_dir,
                                             template_str=Ew4Merra2.aero_fname_template,
                                            )

        transforms_super = transforms 
        super().__init__(variables=filtered_vars,transforms=transforms_super)

@register_archive("ew4_merra2_meteo", sample_kwargs=dict(variable="T2M"))
class Ew4Merra2Meteo(Ew4Merra2):
    def __init__(
        self,
        variables: list[str] | str,
        *,
        transforms: Transform | TransformCollection | None = None,
    ):

        # check list of variables against valid ones
        filtered_vars = [var1 for var1 in variables if var1 in METEO_VARS]
        
        if len(filtered_vars) == 0:
            raise DataError('Not valid variables selected')
        
        if len(filtered_vars) != len(variables):
            print('The following variables were selected but are not present in the dataset and rejected:\n', 
                  '\n'.join(var1 for var1 in variables if var1 not in MERRA2_VARS))
        else:
            print('All selected variables present in the dataset.')
            
        
        self._meteo_dir = pathlib.Path(self.ROOT_DIRECTORIES['ew4_merra2_meteo'])
        
        self._var_path_lookup = functools.partial(_construct_merra2_meteo_path, 
                                             root_dir=self._meteo_dir,
                                             template_str=Ew4Merra2.meteo_fname_template,
                                            )

        transforms_super =  TransformCollection([MeteoHourFix(),]) + transforms
        super().__init__(variables=filtered_vars,transforms=transforms_super)

ERA5_VARS = [
    'temperature',
    'specific_humidity',
    'u_component_of_wind',
    'v_component_of_wind',
    'geopotential',
    'vertical_velocity',
]

def _filter_vars(variables, var_whitelist):
    # check list of variables against valid ones
    filtered_vars = [var1 for var1 in variables if var1 in var_whitelist]
        
    if len(filtered_vars) == 0:
        raise DataError('Not valid variables selected')
        
    if len(filtered_vars) != len(variables):
        print('The following variables were selected but are not present in the dataset and rejected:\n', 
              '\n'.join(var1 for var1 in variables if var1 not in var_whitelist))
    else:
        print('All selected variables present in the dataset.')
    return filtered_vars

@register_archive("ew4_era5", sample_kwargs=dict(variable="temperature"))
class Ew4Era5(ArchiveIndex):
    """
    Access for EW4 Energy subset of ERA5 for use with nowcasting.
    """
    era5_fname_template = 'era5_pl_{dt.year:04d}_{dt.month:02d}_{var_name}.nc'
    template_interval = '1 hour'

    @property
    def _desc_(self):
        return {
            "singleline": "EW4 ERA5 Reanalsyis subset",
            "range": "April to September 2025",
            "Documentation": "https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation",
        }

    def __init__(
        self,
        variables: list[str] | str,
        *,
        transforms: Transform | TransformCollection | None = None,
    ):
        """
        Doc string for init function
        """

        self._filtered_vars = _filter_vars(variables, ERA5_VARS)
        self._data_dir = pathlib.Path(self.ROOT_DIRECTORIES['ew4_era5'])
        
        transforms_super = transforms 
        super().__init__(
            variables=self._filtered_vars,
            transforms=transforms_super)
        self.record_initialisation()

    def filesystem(
        self,
        querytime: str | Petdt,
    ) -> Path | dict[str, str | Path]:
        

        paths = []
        querytime = Petdt(querytime)

        for var1  in self._filtered_vars:
            paths += [self._data_dir / Ew4Era5.era5_fname_template.format(dt=querytime, var_name=var1)]
        
        return paths