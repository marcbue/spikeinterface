import shutil
from pathlib import Path

import pytest
import numpy as np

from spikeinterface.core import NumpyRecording, NumpySorting, NumpyEvent
from spikeinterface.core.tests.testing_tools import create_sorting_npz
from spikeinterface.core import NpzSortingExtractor

cache_folder = Path('./my_cache_folder')


def _clean_all():
    if cache_folder.exists():
        shutil.rmtree(cache_folder)


def setup_module():
    _clean_all()


def teardown_module():
    _clean_all()


def test_NumpyRecording():
    sampling_frequency = 30000
    timeseries_list = []
    for seg_index in range(3):
        traces = np.zeros((1000, 5), dtype='float64')
        timeseries_list.append(traces)

    rec = NumpyRecording(timeseries_list, sampling_frequency)
    print(rec)

    rec.save(folder=cache_folder / 'test_NumpyRecording')


def test_NumpySorting():
    sampling_frequency = 30000

    # empty
    unit_ids = []
    sorting = NumpySorting(sampling_frequency, unit_ids)
    # print(sorting)

    # 2 columns
    times = np.arange(0, 1000, 10)
    labels = np.zeros(times.size, dtype='int64')
    labels[0::3] = 0
    labels[1::3] = 1
    labels[2::3] = 2
    sorting = NumpySorting.from_times_labels(times, labels, sampling_frequency)
    print(sorting)
    assert sorting.get_num_segments() == 1

    sorting = NumpySorting.from_times_labels([times] * 3, [labels] * 3, sampling_frequency)
    # print(sorting)
    assert sorting.get_num_segments() == 3

    # from other extracrtor
    num_seg = 2
    file_path = 'test_NpzSortingExtractor.npz'
    create_sorting_npz(num_seg, file_path)
    other_sorting = NpzSortingExtractor(file_path)

    sorting = NumpySorting.from_extractor(other_sorting)
    # print(sorting)


def test_NumpyEvent():
    # one segment - dtype simple
    d = {
        'trig0': np.array([1, 10, 100]),
        'trig1': np.array([1, 50, 150]),
    }
    event = NumpyEvent.from_dict(d)

    times = event.get_event_times('trig0')
    assert times[2] == 100

    times = event.get_event_times('trig1')
    assert times[2] == 150

    # 2 segments - dtype simple
    event = NumpyEvent.from_dict([d, d])
    times = event.get_event_times('trig1', segment_index=1)
    assert times[2] == 150

    # 2 segments - dtype structured for one trig
    d = {
        'trig0': np.array([1, 10, 100]),
        'trig1': np.array([1, 50, 150]),
        'trig3': np.array([(1, 20), (50, 30), (150, 60)], dtype=[('times', 'int64'), ('duration', 'int64')]),
    }
    event = NumpyEvent.from_dict([d, d])
    times = event.get_event_times('trig1', segment_index=1)
    assert times[2] == 150

    times = event.get_event_times('trig3', segment_index=1)
    assert times.dtype.fields is not None
    assert times['times'][2] == 150
    assert times['duration'][2] == 60

    times = event.get_event_times('trig3', segment_index=1, end_time=100)
    assert times.size == 2


if __name__ == '__main__':
    _clean_all()
    # ~ test_NumpyRecording()
    # ~ test_NumpySorting()
    test_NumpyEvent()
