import logging
from os.path import abspath, dirname, join

import itertools
import psutil

STATS_LOG_FORMAT = '%(asctime)s    %(message)s'
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(logging.Formatter(STATS_LOG_FORMAT))

stats_logger = logging.getLogger('stats-logger')
stats_logger.addHandler(_stream_handler)
stats_logger.setLevel(logging.INFO)


class PerformanceCoefficient(object):
    VALUE = 5099000  # Value was got on Core i7-6500U CPU

    @classmethod
    def update_performance_coefficient(cls):
        start = psutil.Process().cpu_times().user
        cls.VALUE = 1
        iterations = 500000000
        load_cpu(iterations)
        finish = psutil.Process().cpu_times().user
        cls.VALUE = int(iterations / (finish - start))
        logging.info('Estimated performance coefficient: {}'.format(cls.VALUE))


class ValuesSequence(object):
    def __init__(self, base_sequence):
        self.base_sequence = base_sequence
        self.total_number = 0
        self.total_sum = 0.0

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.base_sequence)
        self.total_number += 1
        self.total_sum += value
        return value

    def next(self):
        return self.__next__()


def report_stats():
    io_ops, io_duration = 0, 0.0
    for seq in DURATIONS.values():
        if seq.total_number:
            io_ops, io_duration = seq.total_number, seq.total_sum

    cpu_ops, cpu_duration = 0, 0.0
    for seq in CPU_LOADS.values():
        if seq.total_number:
            cpu_ops, cpu_duration = seq.total_number, seq.total_sum

    cpu_times = psutil.Process().cpu_times()

    stats_logger.info(
        'IO: {io_ops: >9} {io_duration: >7,.1f}   '
        'CPU: {cpu_ops: >9} {cpu_duration: >6,.1f}   '
        'CPU-times: {cpu_user: >6,.1f} {cpu_system: >6,.1f}'
            .format(io_ops=io_ops, io_duration=io_duration,
                    cpu_ops=cpu_ops, cpu_duration=cpu_duration,
                    cpu_user=cpu_times.user, cpu_system=cpu_times.system))


def load_cpu(seconds):
    iterations = seconds * PerformanceCoefficient.VALUE
    while iterations > 0:
        y = 9999999
        x = y * y
        y = x - y * (y - 1)
        iterations -= y - (y - 1)


def _load_response_file(file_name):
    files_dir = join(dirname(abspath(__file__)), 'json_files')
    with open(join(files_dir, file_name)) as json_file:
        return json_file.read()


RESPONSE_FILES = {
    'missing': '',
    'tiny': _load_response_file('tiny.json'),
    'low': _load_response_file('low.json'),
    'normal': _load_response_file('normal.json'),
    'high': _load_response_file('high.json'),
    'huge': _load_response_file('huge.json'),
}


DURATIONS = {
    'missing': ValuesSequence(itertools.cycle([0])),
    'tiny': ValuesSequence(itertools.cycle([  # random 0.5-1.5 ms   X25
        0.00072, 0.00140, 0.00129, 0.00055, 0.00143, 0.00091, 0.00131, 0.00101,
        0.00097, 0.00054, 0.00087, 0.00066, 0.00115, 0.00148, 0.00053, 0.00088,
        0.00110, 0.00088, 0.00111, 0.00082, 0.00085, 0.00137, 0.00065, 0.00092,
        0.00125
    ])),
    'low': ValuesSequence(itertools.cycle([  # random 1-3 ms   X25
        0.00136, 0.00282, 0.00236, 0.00241, 0.00156, 0.00113, 0.00247, 0.00156,
        0.00290, 0.00175, 0.00126, 0.00280, 0.00185, 0.00134, 0.00244, 0.00137,
        0.00225, 0.00268, 0.00100, 0.00231, 0.00147, 0.00240, 0.00212, 0.00246,
        0.00137
    ])),
    'normal': ValuesSequence(itertools.cycle([  # random 30-60 ms   X25
        0.05226, 0.04101, 0.03083, 0.03783, 0.04223, 0.03961, 0.05321, 0.03193,
        0.04693, 0.04863, 0.03177, 0.03202, 0.03148, 0.05408, 0.03948, 0.04840,
        0.03275, 0.04711, 0.03473, 0.03261, 0.03674, 0.05408, 0.05087, 0.04297,
        0.03271
    ])),
    'high': ValuesSequence(itertools.cycle([  # random 500-800 ms   X25
        0.75404, 0.58158, 0.76888, 0.51184, 0.57822, 0.52086, 0.66615, 0.71396,
        0.72955, 0.53984, 0.62011, 0.74071, 0.55196, 0.67843, 0.70419, 0.64219,
        0.78352, 0.51477, 0.57359, 0.73417, 0.71345, 0.61352, 0.69332, 0.63462,
        0.63352
    ])),
    'huge': ValuesSequence(itertools.cycle([  # random 4000-7000 ms   X25
        6.46383, 6.29956, 6.74743, 4.08506, 6.22442, 4.29255, 5.27338, 6.64986,
        4.71255, 5.21431, 6.69220, 6.85728, 4.27424, 6.74587, 6.08067, 6.64657,
        6.68862, 6.67078, 5.86824, 6.41735, 5.04594, 5.47971, 6.44091, 4.73793,
        6.2143
    ]))
}


IO_NUMBER = {
    'missing': 0,
    'tiny': 1,
    'low': 2,
    'normal': 6,
    'high': 20,
    'huge': 70
}


CPU_LOADS = {
    'missing': ValuesSequence(itertools.cycle([0])),
    'tiny': ValuesSequence(itertools.cycle(reversed([  # random 0.005-0.015 ms   X18
        0.0000072, 0.0000140, 0.0000129, 0.0000055, 0.0000143, 0.0000091,
        0.0000097, 0.0000054, 0.0000087, 0.0000066, 0.0000115, 0.0000148,
        0.0000110, 0.0000088, 0.0000111, 0.0000082, 0.0000085, 0.0000137,
    ]))),
    'low': ValuesSequence(itertools.cycle(reversed([  # random 0.05-0.08 ms   X18
        0.0000637, 0.0000784, 0.00005409, 0.0000665, 0.0000743, 0.0000769,
        0.0000647, 0.0000715, 0.00006098, 0.0000772, 0.0000680, 0.0000561,
        0.0000533, 0.0000554, 0.00006227, 0.0000514, 0.0000597, 0.0000687
    ]))),
    'normal': ValuesSequence(itertools.cycle(reversed([  # random 0.5-0.8 ms   X18
        0.000637, 0.000784, 0.0005409, 0.000665, 0.000743, 0.000769,
        0.000647, 0.000715, 0.0006098, 0.000772, 0.000680, 0.000561,
        0.000533, 0.000554, 0.0006227, 0.000514, 0.000597, 0.000687
    ]))),
    'high': ValuesSequence(itertools.cycle(reversed([  # random 5-8 ms   X18
        0.00637, 0.00784, 0.005409, 0.00665, 0.00743, 0.00769,
        0.00647, 0.00715, 0.006098, 0.00772, 0.00680, 0.00561,
        0.00533, 0.00554, 0.006227, 0.00514, 0.00597, 0.00687
    ]))),
    'huge': ValuesSequence(itertools.cycle(reversed([  # random 50-80 ms   X18
        0.0637, 0.0784, 0.05409, 0.0665, 0.0743, 0.0769,
        0.0647, 0.0715, 0.06098, 0.0772, 0.0680, 0.0561,
        0.0533, 0.0554, 0.06227, 0.0514, 0.0597, 0.0687
    ])))
}
