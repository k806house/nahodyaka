from enum import Flag

import numpy as np
import tensorflow as tf
from app.storage import StorageClient
from PIL import Image

EMBEDDING_MODEL_PATH = "./models/facenet150.h5"
FOUND_STORAGE_URL = "http://localhost:5000"
LOST_STORAGE_URL = "http://localhost:5001"
IMG_SIZE = (224, 224)


class Action(Flag):
    FOUND = False
    LOST = True


class Engine:
    def __init__(self):
        self.model = tf.keras.models.load_model(EMBEDDING_MODEL_PATH,
                                                custom_objects={
                                                    "triplet": None,
                                                    "triplet_acc": None
                                                })

        self.found_storage_client = StorageClient(FOUND_STORAGE_URL)
        self.lost_storage_client = StorageClient(LOST_STORAGE_URL)

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

    def __get_emb(self, filename):
        img = Image.open(filename).resize(IMG_SIZE)
        arr = np.asarray(img)[np.newaxis, ...] / 255
        return self.model.predict(arr)

    def __action_to_storage(self, act):
        if act == Action.FOUND:
            return self.found_storage_client
        elif act == Action.LOST:
            return self.lost_storage_client
