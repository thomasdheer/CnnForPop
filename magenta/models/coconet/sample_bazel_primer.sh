# Copyright 2020 The Magenta Authors. Adapted by Thomas D'heer
# Use this script to prime your generated sample with a given sequence.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash

set -x
set -e

# ADAPT THE 'checkpoint' VARIABLE TO THE PATH OF THE LOCATION WHERE YOU HAVE STORED THE DESIRED MODEL CHECKPOINT

# To use a model trained on the J.S. Bach chorales dataset:
# checkpoint=$HOME/Downloads/checkpoint/coconet_checkpoint/coconet-64layers-128filters/

# For a custom model trained on 10.000 songs from the Lakh dataset
checkpoint=$HOME/Documents/trained_models/lakh10k/

# Change this to path where the samples should be saved.
generation_output_dir=$HOME/samples

# Change this to the path to the input MIDI file that you'd like to be used as a primer melody
# If not applicable, select 'None'
priming=True
prime_midi_fpath=$HOME/Documents/formatted_midi/blankspace_primer.mid

# Set timeExtension to True if you want to extend the samples by moving-window sampling
timeExtension=True

# Generation parameters.
# Number of samples to generate in a batch.
gen_batch_size=1
piece_length=32
strategy=igibbs
tfsample=False

# Run command.
python coconet_sample_primer.py \
--checkpoint="$checkpoint" \
--gen_batch_size=$gen_batch_size \
--piece_length=$piece_length \
--temperature=0.99 \
--strategy=$strategy \
--tfsample=$tfsample \
--priming=$priming \
--timeExtension=$timeExtension \
--generation_output_dir=$generation_output_dir \
--prime_midi_fpath=$prime_midi_fpath \
--logtostderr