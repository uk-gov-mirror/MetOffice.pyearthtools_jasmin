# (C) British Crown Copyright 2017-2026, Met Office.
# Please see LICENSE.md for license details.

"""
Template for a pyearthtools dataset accessor on JASMIN

"""

from __future__ import annotations

from pathlib import Path


import pyearthtools.data

from pyearthtools.data import Petdt
from pyearthtools.data.exceptions import DataNotFoundError
from pyearthtools.data.indexes import ArchiveIndex, decorators
from pyearthtools.data.transforms import Transform, TransformCollection
from pyearthtools.data.archive import register_archive

from site_archive_jasmin.utilities import (
    cached_exists,
    cached_iterdir,
)  # Could these be moved into a generic module?




@register_archive("template_name", sample_kwargs=dict(variable="2t"))
class TemplateAccessor(ArchiveIndex):
    """Description of dataset"""

    @property
    def _desc_(self):
        return {
            "singleline": "Dataset name",
            "range": "start datetime to end datetime",
            "Documentation": "https:/organisation.org/path/to/docs",
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

        # set up the accessor
        
        # call the base class
        super().__init__(
            transforms=base_transform + (transforms or TransformCollection()),
            data_interval=ERA_RESOLUTION,
        )
        self.record_initialisation()

    def filesystem(
        self,
        querytime: str | Petdt,
    ) -> Path | dict[str, str | Path]:
        

        paths = {}
        querytime = Petdt(querytime)

        # build a dictionary of filenames based on the parameters of this accessor to be used for loading
        
        return paths

    # Do we need this?
    @property
    def _import(self):
        """module to import when this class is used"""
        return "pyearthtools.site_archive_met_office.TemplateAccessor"
