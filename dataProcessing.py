import numpy as np
import pretty_midi
import os
import math
from sklearn.model_selection import train_test_split
import tensorflow as tf
import magenta.models.coconet.lib_pianoroll as mag
import magenta.models.coconet.save_midi_mod as mag2


def extract_pitches(pr, max_l):
    # rows: the amount of pitches in the pianoroll, ergo 128
    # cols: the amount of timesteps, which varies: 300, 400, 500, ...
    (rows, cols) = pr.shape
    new_pr = []

    for i in range(cols):
        pitches, dummy = np.nonzero(pr[:, [i]])
        length = len(pitches)
        if length == 0:
            pitches = [float('nan')]
        if length > max_l:
            max_l = length
        temp = []
        if length > 0:
            for j in range(length):
                pitches[j] = reduce_range_36_81(pitches[j])
                temp.append(pitches[j])
        else:
            temp = pitches
        new_pr.append(list(set(temp)))  # set: to make sure there are no double notes after range reduction
    return new_pr, max_l


def reduce_range_36_81(number):
    new_number = 0
    if not math.isnan(number):
        if number < 36:
            fraction = (36 - number) / 12
            steps = math.ceil(fraction)
            new_number = number + 12 * steps
        elif number <= 81:
            new_number = number
        elif number > 81:
            fraction = (number - 81) / 12
            steps = math.ceil(fraction)
            new_number = number - 12 * steps
    else:
        new_number = number
    return float(new_number)


def midi_to_format(midi_in_path, max_l):
    # input: path to a complete MIDI file
    global lengte
    midi_data = pretty_midi.PrettyMIDI(midi_in_path)
    if len(midi_data.instruments) > 0:
        pr_allinstr = []
        number_instruments = 4
        counter = 0
        # extract pianorolls for all (e.g.) 4 instruments and put them in a list called 'pr_allinstr'
        for i in midi_data.instruments:
            if not i.is_drum:
                sep_roll = i.get_piano_roll(fs=2)   # 8
                temp_pr, max_l = extract_pitches(sep_roll, max_l)
                pr_allinstr.append(temp_pr)
                lengte = len(pr_allinstr)
                counter += 1
                if counter > (number_instruments - 1):
                    break

        adapted_roll = []
        for t in range(2500):
            instr_combination = []
            for j in range(number_instruments):
                try:
                    instr_combination.append(pr_allinstr[j][t])
                except IndexError as e:
                    instr_combination.append([float('nan')])
            adapted_roll.append(instr_combination)
        cropped_roll = crop_roll(adapted_roll)
        return cropped_roll, max_l
    else:
        return None, None


def crop_roll(input_roll):
    cropped_roll = input_roll[0:64]
    divisor = int(2500 / 64)
    best_count = 256 - count_nans(cropped_roll) + 4 * count_unique(cropped_roll)
    # to choose which crop to use: based on having little 'nan' and a lot of different notes
    for i in range(divisor):
        temp_roll = input_roll[i * 64:(i + 1) * 64]
        new_count = 256 - count_nans(temp_roll) + 4 * count_unique(temp_roll)
        if new_count > best_count:
            cropped_roll = temp_roll
            best_count = new_count
    return cropped_roll


def count_nans(roll):
    length = len(roll)
    count = 0
    for i in range(length):
        count += count_nans_sublist(roll[i])
    return count


def count_unique(roll):
    length = len(roll)
    totaleset = set()
    for i in range(length):
        subunis = extract_unique_sublist(roll[i])
        totaleset.update(subunis)
    return len(totaleset)


def extract_unique_sublist(roll):
    flat_list = [item for sublist in roll for item in sublist]
    return customset(flat_list)


def customset(X):
    L = set()
    for i in X:
        if str(i) != 'nan' and i not in L:
            L.add(i)
    return L


def count_nans_sublist(roll):
    flat_list = [item for sublist in roll for item in sublist]
    count = 0
    for xx in flat_list:
        if str(xx) == 'nan':
            count += 1
    return count


def construct_file(input_directory, total_files):
    output = np.empty(total_files, dtype=object)
    max_l = 0
    i = 0

    for subdir, dirs, files in os.walk(input_directory):
        if i > (total_files - 1):
            break
        else:
            for file in files:
                filepath = subdir + os.sep + file
                miditest = filepath.endswith(".midi") or filepath.endswith(".mid")
                try:
                    formatted_midi, new_max = midi_to_format(filepath, max_l)
                    if formatted_midi is not None and miditest:
                        max_l = new_max
                        output[i] = formatted_midi
                        i = i + 1
                        print('File #' + str(i))
                except (OSError, KeyError, EOFError, ValueError, IndexError, MemoryError) as e:
                    print(e)
                    continue
                if i > (total_files - 1):
                    break
    return output


amount_of_files_to_process = 10
folder = '/home/user/Documents/midifiles/'
out = construct_file(folder, amount_of_files_to_process)

# Choose if you would like to convert the processed pianorolls back to MIDI, to check the results

converttomidi = False
amount_midi_conversions = 10

if converttomidi:
    PED = mag.PianorollEncoderDecoder(separate_instruments=True, num_instruments=4, quantization_level=0.125)
    for i in range(amount_midi_conversions):
        adaproll = out[i]
        adappr = mag.PianorollEncoderDecoder.encode_list_of_lists(PED, adaproll)
        midiout = mag.PianorollEncoderDecoder.decode_to_midi(PED, adappr)
        tempdir = '/home/user/Documents/midiconversions/'
        midi_path = os.path.join(tempdir, str(i))
        tf.gfile.MakeDirs(midi_path)
        testfile = "testfile" + str(i)
        mag2.save_midis(midiout, midi_path, testfile)


out_train, out_test = train_test_split(out, test_size=0.2)
out_train, out_valid = train_test_split(out_train, test_size=0.25)

# Choose if you would like to save the files, along with the desired directory and file name
I_want_to_save = True
dir_path = '/home/user/Documents/formatted_midi/'
save_name = 'dataset_1000_final'


if I_want_to_save:
    np.save(dir_path + save_name + '_train.npy', out_train)
    np.save(dir_path + save_name + '_test.npy', out_test)
    np.save(dir_path + save_name + '_valid.npy', out_valid)
    np.savez_compressed(dir_path + save_name + '_full.npz', out_train, out_test, out_valid)

