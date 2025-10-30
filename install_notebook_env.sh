# this scriipt shows how to set up a venv for running pyearthtools through a notebook on the JASMIN compute cluster. Conda environments do not work with the JASMIN notebook service, so we can't have a c entral install at this time, so each person need to set up their own env.

#this should be run from a terminal started from jupyterhub
# youu will need to create separate environments for running notebooks on CPU and GPU. The same install script can be used for, because libraries will be installed based on the platform the install script is run from.

# comment/uncomment the env name based on whether you are runing on CPU or GPU
export ENV_NAME=pet_devnb_cpu
#export ENV_NAME=pet_devnb_gpu


mkdir ~/venv
python -m venv ~/venv/${ENV_NAME}
.  ~/venv/${ENV_NAME}/bin/activate

#this script needs to run in the root directory of the pyearthtools repo

#cd /path/to/pyearthtools/repo
pip install -r requirements.txt

#the next command need to run from the jasmin siter archive repo
#cd path/to/jasmin/site/archive/repo
pip install -e .

# once the environment is setup, we need to "install" it so it is usable in a jupyter notebook
python -m ipykernel install --user --name ${ENV_NAME}


