# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

# this scriipt shows how to set up a venv for running pyearthtools through a notebook on the JASMIN compute cluster. Conda environments do not work with the JASMIN notebook service, so we can't have a c entral install at this time, so each person need to set up their own env.

#this should be run from a terminal started from jupyterhub
# youu will need to create separate environments for running notebooks on CPU and GPU. The same install script can be used for, because libraries will be installed based on the platform the install script is run from.

# comment/uncomment the env name based on whether you are runing on CPU or GPU
# export ENV_NAME=pet_dev_nb_cpu
export ENV_NAME=pet_dev_nb_gpu

#uncomment if you don't have a venv directory
# mkdir ~/venv

export CACHE_DIR=/work/nopw/shaddad/cache/ 
export VENV_PATH=/gws/nopw/j04/mohc_shared/users/shaddad/venv/${ENV_NAME}

python -m venv $VENV_PATH
.  ${VENV_PATH}/bin/activate

#the next command needs to run in the root directory of the pyearthtools repo. This will be the directory into which you cloned the PyEarthTools repository.
cd ~/prog/pet_fork
export TMPDIR=$CACHE_DIR
pip install --cache-dir $CACHE_DIR -r requirements.txt

#the next command need to run from the jasmin siter archive repo. This will be the directory into which you cloned the pyearthtools_jasmin repository.
cd ~/prog/pyearthtools_jasmin
pip install --cache-dir $CACHE_DIR -e .

# once the environment is setup, we need to "install" it so it is usable in a jupyter notebook
pip install ipykernel
python -m ipykernel install --user --name ${ENV_NAME}

