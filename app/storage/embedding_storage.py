import os
import pickle

import numpy as np


class EmbeddingStorage:
    def __init__(self):
        self.index = {}
        self.__id_cnt = 0

    def add(self, emb):
        while self.__id_cnt in self.index:
            self.__id_cnt += 1
        self.index[self.__id_cnt] = np.array(emb, dtype=np.float32)
        return self.__id_cnt

    def emb_by_id(self, emb_id):
        return self.index[emb_id]

    def remove(self, emb_id):
        self.index.pop(emb_id)

    def k_nbrs(self, query, k):
        distances = []
        q = np.array(query)
        for emb_id, emb in self.index.items():
            dist = np.sum(np.square(q - emb))
            distances.append((dist, emb_id))
        distances.sort()
        return distances[:k]

    def save(self, filename):
        pickle.dump(self.index, filename)

    def load(self, filename):
        if os.path.exists(filename):
            self.index = pickle.load(filename)
