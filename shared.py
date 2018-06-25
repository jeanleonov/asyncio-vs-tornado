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

    process = psutil.Process()
    cpu_times = process.cpu_times()
    memory = process.memory_full_info()

    stats_logger.info(
        'IO: {io_ops: >9} {io_duration: >7,.1f}   '
        'CPU: {cpu_ops: >9} {cpu_duration: >6,.1f}   '
        'CPU-times: {cpu_user: >6,.1f} {cpu_system: >6,.1f} '
        '{cpu_children_user: >6,.1f} {cpu_children_user: >6,.1f}    '
        'Memory: {mem_virt: >6,.1f} {mem_res: >6,.1f} {mem_uni: >6,.1f}'
        .format(io_ops=io_ops, io_duration=io_duration,
                cpu_ops=cpu_ops, cpu_duration=cpu_duration,
                cpu_user=cpu_times.user, cpu_system=cpu_times.system,
                cpu_children_user=cpu_times.children_user,
                cpu_children_system=cpu_times.children_system,
                mem_virt=float(memory.vms)/1024/1024,
                mem_res=float(memory.rss)/1024/1024,
                mem_uni=float(memory.uss)/1024/1024)
        .replace(',', '')
    )


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
    'tiny': ValuesSequence(itertools.cycle([  # random 0.5-2 ms   X24
        0.001165, 0.000503, 0.000853, 0.000615, 0.001860, 0.001779,
        0.001786, 0.000835, 0.001134, 0.001159, 0.001899, 0.001535,
        0.001647, 0.000656, 0.000875, 0.000741, 0.001385, 0.000674,
        0.001241, 0.000771, 0.000951, 0.000654, 0.001805, 0.001115,
    ])),
    'low': ValuesSequence(itertools.cycle([  # random 2-5 ms   X24
        0.003789, 0.002571, 0.002111, 0.002613, 0.003445, 0.002923,
        0.003220, 0.003631, 0.004286, 0.002221, 0.002461, 0.004845,
        0.002038, 0.004189, 0.003008, 0.002905, 0.004563, 0.002269,
        0.002736, 0.004235, 0.004439, 0.002162, 0.004836, 0.004772,
    ])),
    'normal': ValuesSequence(itertools.cycle([  # random 25-70 ms   X24
        0.025553, 0.028799, 0.035800, 0.027559, 0.073656, 0.073528,
        0.048619, 0.054152, 0.074836, 0.036991, 0.025832, 0.026936,
        0.058100, 0.025713, 0.043148, 0.062096, 0.074010, 0.043896,
        0.067063, 0.066379, 0.063867, 0.057188, 0.071563, 0.072562,
    ])),
    'high': ValuesSequence(itertools.cycle([  # random 500-800 ms   X24
        0.479635, 1.204827, 0.678252, 1.185812, 1.248146, 1.203648,
        0.621197, 0.520646, 0.445623, 1.113919, 1.020443, 0.759029,
        0.637582, 1.217379, 1.122568, 1.155758, 0.418684, 0.765499,
        0.673272, 0.625451, 1.280395, 1.002032, 1.202187, 0.969820
    ])),
    'huge': ValuesSequence(itertools.cycle([  # random 4000-7000 ms   X24
        0.615594, 0.704556, 0.722186, 0.873756, 0.872951, 0.621156,
        0.533312, 0.809434, 0.520779, 0.403861, 0.834314, 0.813135,
        0.427449, 0.683223, 0.496206, 0.638510, 0.886516, 0.508138,
        0.800857, 0.803219, 0.571662, 0.703795, 0.671992, 0.629472,
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
    'tiny': ValuesSequence(itertools.cycle(reversed([  # random 0.005-0.030 ms  X24
        0.000018, 0.000013, 0.000014, 0.000013, 0.000014, 0.000009,
        0.000007, 0.000016, 0.000020, 0.000028, 0.000013, 0.000030,
        0.000025, 0.000017, 0.000026, 0.000024, 0.000014, 0.000018,
        0.000017, 0.000028, 0.000007, 0.000027, 0.000007, 0.000028,
    ]))),
    'low': ValuesSequence(itertools.cycle(reversed([  # random 0.050-0.200 ms  X24
        0.000102, 0.000192, 0.000116, 0.000117, 0.000103, 0.000068,
        0.000051, 0.000185, 0.000184, 0.000074, 0.000120, 0.000143,
        0.000144, 0.000182, 0.000137, 0.000188, 0.000115, 0.000189,
        0.000093, 0.000134, 0.000182, 0.000200, 0.000098, 0.000196,
    ]))),
    'normal': ValuesSequence(itertools.cycle(reversed([  # random 0.5-1.5 ms  X24
        0.000938, 0.000515, 0.001124, 0.001293, 0.000774, 0.001468,
        0.000899, 0.000683, 0.001349, 0.000892, 0.000874, 0.000740,
        0.000944, 0.000967, 0.001200, 0.000982, 0.000764, 0.001237,
        0.001117, 0.001435, 0.001132, 0.001187, 0.001430, 0.001446,

    ]))),
    'high': ValuesSequence(itertools.cycle(reversed([  # random 5-15 ms   X24
        0.013226, 0.007671, 0.008585, 0.013754, 0.005320, 0.007592,
        0.012287, 0.007657, 0.009038, 0.009439, 0.011055, 0.012639,
        0.005999, 0.005831, 0.013674, 0.008588, 0.013762, 0.009938,
        0.005388, 0.010552, 0.011193, 0.006876, 0.011000, 0.008247,
    ]))),
    'huge': ValuesSequence(itertools.cycle(reversed([  # random 50-150 ms   X24
        0.087546, 0.054300, 0.096088, 0.100918, 0.129317, 0.141902,
        0.146268, 0.128219, 0.096636, 0.114030, 0.095098, 0.094107,
        0.105108, 0.085582, 0.143492, 0.118011, 0.077473, 0.060770,
        0.101820, 0.137710, 0.134219, 0.069578, 0.058889, 0.138179,
    ])))
}
