import os
from magenta.models.coconet import lib_util
import tensorflow as tf


def save_midis(midi_datas, midi_path, label=""):
  midi_fpath = os.path.join(midi_path, "%s.midi" % (label))
  tf.logging.info("Writing midi to %s", midi_fpath)
  with lib_util.atomic_file(midi_fpath) as p:
    midi_datas.write(p)
  return midi_fpath

