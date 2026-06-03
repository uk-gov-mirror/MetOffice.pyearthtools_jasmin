#!/usr/bin/env python
"""
cds_era5_pl_download.py

This script was generated using ChatGPT and reviewed by Stephen Haddad.

Download ERA5 pressure-level data from the Copernicus Climate Data Store.

Example
-------
python download_era5_pl.py \
    --start-date 2020-01-01 \
    --end-date 2020-03-31 \
    --pressure-levels 500 700 850 \
    --variables temperature geopotential

Requirements
------------
pip install cdsapi
"""

from __future__ import annotations

import argparse
import calendar
import copy
import logging
from datetime import date, datetime
from pathlib import Path

import cdsapi


LOGGER = logging.getLogger(__name__)


REQUEST_TEMPLATE = {
    "product_type": "reanalysis",
    "data_format": "netcdf",
    "download_format": "unarchived",
    "variable": None,
    "pressure_level": None,
    "year": None,
    "month": None,
    "day": None,
    "time": [f"{hour:02d}:00" for hour in range(24)],
    "area": [27,-20,2,27],
}


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download ERA5 pressure-level data from CDS."
    )

    parser.add_argument(
        "--start-date",
        required=True,
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        help="Start date (YYYY-MM-DD).",
    )

    parser.add_argument(
        "--end-date",
        required=True,
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        help="End date (YYYY-MM-DD).",
    )

    parser.add_argument(
        "--pressure-levels",
        required=True,
        nargs="+",
        help="Pressure levels in hPa (e.g. 500 700 850).",
    )

    parser.add_argument(
        "--variables",
        required=True,
        nargs="+",
        help="ERA5 variable names.",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level.",
    )

    parser.add_argument(
        "--download-dir",
        dest='download_dir',
        type=Path,
        help="Output directory for data.",
    )

    return parser.parse_args()


def month_iterator(start_date: date, end_date: date):
    """
    Yield (year, month) tuples covering the date range.
    """
    year = start_date.year
    month = start_date.month

    while (year < end_date.year) or (
        year == end_date.year and month <= end_date.month
    ):
        yield year, month

        month += 1
        if month > 12:
            month = 1
            year += 1


def build_request(
    variable: str,
    pressure_levels: list[str],
    year: int,
    month: int,
):
    """
    Build a CDS request from the template.
    """
    request = copy.deepcopy(REQUEST_TEMPLATE)

    _, last_day = calendar.monthrange(year, month)

    request["variable"] = variable
    request["pressure_level"] = pressure_levels
    request["year"] = str(year)
    request["month"] = f"{month:02d}"
    request["day"] = [f"{d:02d}" for d in range(1, last_day + 1)]

    return request


def download_month(
    client: cdsapi.Client,
    variable: str,
    pressure_levels: list[str],
    year: int,
    month: int,
    download_dir: Path,
):
    """
    Download one month of one variable.
    """
    request = build_request(
        variable=variable,
        pressure_levels=pressure_levels,
        year=year,
        month=month,
    )

    output_file = (
        download_dir
        / f"era5_pl_{year}_{month:02d}_{variable}.nc"
    )

    LOGGER.info(
        "Downloading variable=%s year=%s month=%s -> %s",
        variable,
        year,
        month,
        output_file,
    )

    client.retrieve(
        "reanalysis-era5-pressure-levels",
        request,
        str(output_file),
    )

    LOGGER.info("Completed %s", output_file)


def main():
    """
    Main program entry point.
    """
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.start_date > args.end_date:
        raise ValueError("start-date must be <= end-date")

    LOGGER.info("Creating CDS API client")
    client = cdsapi.Client()

    LOGGER.info(
        "Processing date range %s to %s",
        args.start_date,
        args.end_date,
    )

    for year, month in month_iterator(
        args.start_date,
        args.end_date,
    ):
        for variable in args.variables:
            download_month(
                client=client,
                variable=variable,
                pressure_levels=args.pressure_levels,
                year=year,
                month=month,
                download_dir=args.download_dir,
            )

    LOGGER.info("All downloads complete")


if __name__ == "__main__":
    main()
