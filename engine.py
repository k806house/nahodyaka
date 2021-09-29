import numpy as np
import tensorflow as tf
from PIL import Image

import config
from storage import EmbeddingStorage


class Engine:
    def __init__(self):
        self.model = tf.keras.models.load_model(config.MODEL_PATH,
                                                custom_objects={
                                                    "triplet": None,
                                                    "triplet_acc": None
                                                })

        self.storage = EmbeddingStorage()
        self.id_to_file = {}

    def add(self, file):
        img = Image.open(file).resize(config.IMG_SIZE)
        arr = np.asarray(img)[np.newaxis, ...] / 255
        emb = self.model.predict(arr)
        emb_id = self.storage.add(emb)
        self.id_to_file[emb_id] = file

    def search(self, file, k=10):
        img = Image.open(file).resize(config.IMG_SIZE)
        arr = np.asarray(img)[np.newaxis, ...] / 255
        emb = self.model.predict(arr)
        k_nbrs = self.storage.search(emb, k)
        return [(dist, self.id_to_file[emb_id]) for dist, emb_id in k_nbrs]
