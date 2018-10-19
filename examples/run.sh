#!/bin/bash

RANK=$(($PMI_RANK%4))
export CUDA_VISIBLE_DEVICES=$RANK
python mpi_learn.py 2>&1
