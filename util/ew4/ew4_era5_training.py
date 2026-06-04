#!/usr/bin/env python
import pathlib
import datetime
import math
import functools
import numpy

import xarray
import matplotlib.pyplot
import cartopy

import site_archive_jasmin
import pyearthtools.data
import pyearthtools.pipeline

import torch


def construct_pet_pipeline(region_extents):
    ew4_era5_accessor = pyearthtools.data.archive.ew4_era5(variables=['temperature','specific_humidity', 'vertical_velocity'])

    ew4_era5_prep = pyearthtools.pipeline.Pipeline(
        ew4_era5_accessor,
        pyearthtools.data.transform.region.Bounding(*region_extents),
        exceptions_to_ignore=pyearthtools.data.exceptions.DataNotFoundError,
    )

    ew4_era5_ml = pyearthtools.pipeline.Pipeline(
        # pyearthtools.pipeline.operations.xarray.reshape.CoordinateFlatten(['pressure_level']),
        pyearthtools.pipeline.operations.xarray.conversion.ToNumpy(),
        pyearthtools.pipeline.operations.numpy.reshape.Rearrange('c t h w -> t c h w'), # channel time height width -> time channel height width
    )

    train_range = pyearthtools.pipeline.Pipeline(
        pyearthtools.pipeline.modifications.TemporalWindow(prior_indexes=[0,], posterior_indexes=[0,], timedelta=pyearthtools.data.TimeDelta('1 hour')),
        iterator=pyearthtools.pipeline.iterators.DateRange('20250501T00', '20250701T00', interval='1 hour').randomise(),
        exceptions_to_ignore=pyearthtools.data.exceptions.DataNotFoundError,
    )
    val_range = pyearthtools.pipeline.Pipeline(
        pyearthtools.pipeline.modifications.TemporalWindow(prior_indexes=[0,], posterior_indexes=[0,], timedelta=TimeDelta('1 hour')),
        iterator=pyearthtools.pipeline.iterators.DateRange('20250701T00', '20250801T00', interval='1 hour'),
        exceptions_to_ignore=pyearthtools.data.exceptions.DataNotFoundError,
    )

    ew4_era5_train_pipe = ew4_era5_prep | ew4_era5_ml | train_range
    ew4_era5_val_pipe = ew4_era5_prep | ew4_era5_ml | val_range

    pipe_dict = {
        'accessor': ew4_era5_accessor,
        'ml': ew4_era5_ml,
        'train_section': train_range,
        'val_section': val_range,
        'train': ew4_era5_train_pipe,
        'val': ew4_era5_val_pipe,
    }

    return pipe_dict




class ERA5AutoEncoder(torch.nn.Module):
    def __init__(self, input_channels, max_pool=False):
        super(ERA5AutoEncoder, self).__init__()

        # we have "hard coded" a lot of the architecture hyperparameters in our model class.
        # Usually you want want to make these arguments for the class so you can vary hyperparameters more easily.
        # Hard coding here makes it easier to follow the architecture definition in the tutorial

        self._num_channels = [input_channels, 16,32]
        self._latent_array_dims = (-1,self._num_channels[-1],8,8)
        self._prelatent_size = functools.reduce(lambda a,b:a*b, self._latent_array_dims[1:])
        # self._latent_size = 500

        self._encoder = self._get_encoder(max_pool)
        self._decoder = self._get_decoder()

    def _get_encoder(self, max_pool):

        encoder = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=self._num_channels[0],
                            out_channels=self._num_channels[1],
                            kernel_size=3,
                            padding=1,
                            stride=2,
                           ),
            torch.nn.ReLU(),
            torch.nn.Conv2d(in_channels=self._num_channels[1],
                            out_channels=self._num_channels[2],
                            kernel_size=3,
                            padding=1,
                            stride=2,
                           ),
            torch.nn.ReLU(),
            torch.nn.Flatten(1, -1),
            )
        return encoder

    def _get_decoder(self):
        """
        """
        decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose2d(in_channels=self._num_channels[2], out_channels=self._num_channels[1], kernel_size=2,stride=2),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose2d(in_channels=self._num_channels[1], out_channels=self._num_channels[0], kernel_size=2,stride=2),
        )
        return decoder

    def forward(self, x):

        # Get latent representation
        latent = self._encoder(x)

        # Reconstruct input
        reconstructed = self._decoder(latent.view(self._latent_array_dims))

        return reconstructed

def setup_ml_model(device, sample_pipe):
    num_channels =  calc_num_channels(sample_pipe, device)
    era5_autoencoder = ERA5AutoEncoder(num_channels, False).to(device)

def calc_num_channels(sample_pipe, device):
    sample_tensor = torch.tensor(next(iter(sample_pipe))[0][0], dtype=torch.float32).to(device)
    num_channels = sample_tensor.shape[1]
    return num_channels

def get_batch_tensors(batch_size, ds_iterator, device):
    """
    Get a torch tensor for target and predictors from a pyearthtools pipeline iterator
    """
    predictor_batch_list = []
    target_batch_list = []
    for _ in range(batch_size):
        pred_sample, target_sample = next(ds_iterator)
        predictor_batch_list += [pred_sample[0]]
        target_batch_list += [target_sample[0]]

    # create numpy array of a batch
    predictor_array = numpy.concat(predictor_batch_list, axis=0)
    target_array = numpy.concat(target_batch_list, axis=0)

    # convert to a tensor and send to gpu
    predictor_gpu_tensor = torch.tensor(
        predictor_array,
        dtype=torch.float32,
    ).to(device)
    target_gpu_tensor = torch.tensor(
        target_array,
        dtype=torch.float32,
    ).to(device)

    return predictor_gpu_tensor, target_gpu_tensor


def run_training_loop(ew4_era5_train_pipe, ew4_era5_val_pipe, era5_autoencoder, device):

    # Loss function and optimizer
    # loss_function = torch.nn.L1Loss()
    # criterion = nn.KLDivLoss()
    loss_function = torch.nn.MSELoss()

    optimizer = torch.optim.Adam(era5_autoencoder.parameters(),
                                 lr=5e-3)

    num_epochs = 25
    num_samples = len(ew4_era5_train_pipe)
    batch_size = 8
    num_batches = math.ceil(num_samples / batch_size)

    for epoch_num in range(num_epochs):
        print(epoch_num)
        epoch_train_loss = 0.0
        epoch_val_loss = 0.0

    era5_train_iter = iter(ew4_era5_train_pipe)

    for batch_ix in range(num_batches):
        predictor_gpu_tensor, target_gpu_tensor = get_batch_tensors(batch_size, era5_train_iter, device)
        if (batch_ix % 100) == 0:
            print(batch_ix)
            optimizer.zero_grad()
            predictions = era5_autoencoder.forward(predictor_gpu_tensor)
            loss_batch = loss_function(predictions, target_gpu_tensor)
            loss_batch.backward()
            optimizer.step()
            epoch_train_loss += loss_batch.to('cpu').item()
        epoch_train_loss /= num_batches

        # calculate loss on validation data
        for val_predictor, val_target in ew4_era5_val_pipe:
            val_pred_tensor = torch.tensor(val_predictor[0], dtype=torch.float32).to(device)
            predictions_val = era5_autoencoder.forward(val_pred_tensor)
            val_target_tensor = torch.tensor(val_target[0], dtype=torch.float32).to(device)
            loss_batch_val = loss_function(predictions_val, val_target_tensor)
            epoch_val_loss += loss_batch_val.to('cpu').item()
            epoch_val_loss /= len(ew4_era5_val_pipe)
        print(epoch_train_loss)
        print(epoch_val_loss)

    return {'train': epoch_train_loss, 'val': epoch_val_loss}






def main():
    select_dt = datetime.datetime(2025,5,11,15,0)

    ghana_extents = {
        'latitude': (4.5,12.3),
        'longitude': (-3.8, 4.0),
    }

    ghana_pet_box = (ghana_extents['latitude'][0],
                     ghana_extents['latitude'][1],
                     ghana_extents['longitude'][0],
                     ghana_extents['longitude'][1],
                    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    pipe_dict = construct_pet_pipeline(ghana_pet_box)

    era5_autoencoder = setup_ml_model(device, pipe_dict['train'])

    loss_dict = run_training_loop(pipe_dict['train'], pipe_dict['val'], era5_autoencoder, device)



