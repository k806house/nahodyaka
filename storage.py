import pickle

import numpy as np

import config


class EmbeddingStorage:
    def __init__(self):
        self.index = {}
        self.__id_cnt = 0

    def add(self, emb):
        while self.__id_cnt in self.index:
            self.__id_cnt += 1
        self.index[self.__id_cnt] = emb
        return self.__id_cnt

    def remove(self, emb_id):
        self.index.pop(emb_id)

    def search(self, query, k):
        distances = []
        for emb_id, emb in self.index.items():
            dist = np.sum(np.square(query - emb))
            distances.append((dist, emb_id))
        distances.sort()
        return distances[:k]

    def save(self):
        pickle.dump(self.index, config.DUMP_PATH)

    def load(self):
        self.index = pickle.load(config.DUMP_PATH)
