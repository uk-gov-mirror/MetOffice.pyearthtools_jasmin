# PyEarthTools - JASMIN Plugin and Site Archive
Code for PyEarthTools site archive on JASMIN compute and data facility.

This repo contains the code for accessing data stored on JASMIN. You may need to get access to the Met Office Group Workspace to be able to use the site archive on JASMIN.

### Installation

To install the site archive, first install pyearthtools following the [instructions in the docs](https://pyearthtools.readthedocs.io/en/latest/newuser.html). Once that is done, you should install this site archive in the same environment using pip:

```
cd $REPO_ROOT
pip install -e .
```

Once you've done this, to use the site archive, you will need to copy a config file into your home space. You should copy the `.pyearthtoolscong_dscop` file to `~/.pyearthtoolsconfig`.

You will then be able to use the site archive as follows:
```
import pyearthtools.data
import site_archive_jasmin

era5 = pyearthtools.data.archive.ERA5lowres(["2m_temperature", "u", "v"])
```

### PyEarthTools Links
* [PyEarthTools docs](https://pyearthtools.readthedocs.io/)
* [Tutorial Gallery](https://pyearthtools.readthedocs.io/en/latest/notebooks/Gallery.html)