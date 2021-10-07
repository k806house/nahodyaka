import os
from enum import Flag
from functools import lru_cache

import numpy as np
import tensorflow as tf
from app.storage import StorageClient
from PIL import Image

IMG_SIZE = (224, 224)


class Action(Flag):
    FOUND = False
    LOST = True


class Engine:
    def __init__(self, found_url, lost_url):
        self.model = tf.keras.models.load_model(
            os.environ["EMBEDDING_MODEL_PATH"],
            custom_objects={
                "triplet": None,
                "triplet_acc": None
            })

        self.found_storage_client = StorageClient(found_url)
        self.lost_storage_client = StorageClient(lost_url)

    def add(self, meta, act):
        emb = self.__get_emb(meta.filename)
        client = self.__action_to_storage(act)
        emb_id = client.emb_add(emb)
        client.meta_add(emb_id, meta)

    def search(self, meta, act, k=10):
        emb = self.__get_emb(meta.filename)
        client = self.__action_to_storage(~act)
        k_nbrs = client.emb_k_nbrs(emb, k)
        return [(dist, client.meta_search(emb_id)) for dist, emb_id in k_nbrs]

    @lru_cache(maxsize=None)
    def __get_emb(self, filename):
        img = Image.open(filename).resize(IMG_SIZE)
        arr = np.asarray(img)[np.newaxis, ...] / 255
        return self.model.predict(arr)

    def __action_to_storage(self, act):
        if act == Action.FOUND:
            return self.found_storage_client
        elif act == Action.LOST:
            return self.lost_storage_client
