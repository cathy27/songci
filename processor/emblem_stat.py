import logging
import multiprocessing
import operator
from itertools import repeat

from mapreduce.driver import MapReduceDriver
from mapreduce.emblem_finals import EmblemFinals
from mapreduce.emblem_freq import EmblemFreq
from nlp.emblem import Emblem
from processor.data_source import MongoDataSource

data_source = MongoDataSource()
songci_list = data_source.find()
emblem_list = Emblem(songci_list).emblem_list()

logger = logging.getLogger('emblem_stat')
logging.basicConfig(level=logging.INFO)


def stat_freq():
    driver = MapReduceDriver(EmblemFreq.map_fn, EmblemFreq.reduce_fn)
    emblem_freq_stat = driver(emblem_list)
    emblem_freq_stat.sort(key=operator.itemgetter(1), reverse=True)

    total_len = len(emblem_freq_stat)
    logger.info('Total length of emblem_freq_stat is %d', total_len)

    workers = (multiprocessing.cpu_count() or 1) * 4

    emblem_freq_chunks = MapReduceDriver.chunks(emblem_freq_stat, int(total_len / workers))
    with multiprocessing.Pool(processes=workers) as pool:
        pool.starmap(save_freq_stat, zip(emblem_freq_chunks, repeat(total_len)))
        pool.close()

    data_source.create_index('emblem', 'name', unique=True)
    data_source.create_index('emblem', 'freq_rate')


def save_freq_stat(freq_stat, total_len):
    freq_threshold = 1
    prev_freq = prev_freq_rate = 0  # cache previous quotient (a.k.a. freq) to improve performance
    for emblem_freq in freq_stat:
        emblem_name, freq = emblem_freq
        if freq <= freq_threshold:
            break
        freq_rate = prev_freq_rate if freq == prev_freq else freq / total_len
        data_source.save('emblem', {'name': emblem_name}, {'freq_rate': freq_rate})
        prev_freq = freq
        prev_freq_rate = freq_rate


def stat_finals():
    driver = MapReduceDriver(EmblemFinals.map_fn, EmblemFinals.reduce_fn)
    emblem_finals_stat = driver(emblem_list)

    total_len = len(emblem_finals_stat)
    print(total_len)


if __name__ == '__main__':
    stat_finals()
