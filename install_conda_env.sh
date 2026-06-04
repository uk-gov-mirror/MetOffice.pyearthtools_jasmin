# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

# this scriipt shows how to set up a venv for running pyearthtools through a notebook on the JASMIN compute cluster. # comment/uncomment the env name based on whether you are runing on CPU or GPU

#export ENV_NAME=pet_dev_cli_cpu
export ENV_NAME=pet_dev_cli_gpu


export CACHE_DIR=/work/nopw/shaddad/cache/ 
export CONDA_PATH=/gws/nopw/j04/mohc_shared/users/shaddad/conda/${ENV_NAME}


conda create -c conda-forge -y -p ${CONDA_PATH} python=3.13 graphviz pip
conda activate ${CONDA_PATH}


#the next command needs to run in the root directory of the pyearthtools repo. This will be the directory into which you cloned the PyEarthTools repository.
cd ~/prog/pet_fork
export TMPDIR=$CACHE_DIR
pip install --cache-dir $CACHE_DIR -r requirements.txt

#the next command need to run from the jasmin siter archive repo. This will be the directory into which you cloned the pyearthtools_jasmin repository.
cd ~/prog/pyearthtools_jasmin
pip install --cache-dir $CACHE_DIR -e .


