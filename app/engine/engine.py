import numpy as np
import tensorflow as tf
from app.storage import StorageClient
from PIL import Image

EMBEDDING_MODEL_PATH = "./models/facenet150.h5"
STORAGE_URL = "http://localhost:5000"
IMG_SIZE = (224, 224)


class Engine:
    def __init__(self):
        self.model = tf.keras.models.load_model(EMBEDDING_MODEL_PATH,
                                                custom_objects={
                                                    "triplet": None,
                                                    "triplet_acc": None
                                                })

        self.storage_client = StorageClient(STORAGE_URL)

    def add(self, meta):
        emb = self.__get_emb(meta.filename)
        emb_id = self.storage_client.emb_add(emb)
        self.storage_client.meta_add(emb_id, meta)

    def search(self, meta, k=10):
        emb = self.__get_emb(meta.filename)
        k_nbrs = self.storage_client.emb_k_nbrs(emb, k)
        return [(dist, self.storage_client.meta_search(emb_id))
                for dist, emb_id in k_nbrs]

    def __get_emb(self, filename):
        img = Image.open(filename).resize(IMG_SIZE)
        arr = np.asarray(img)[np.newaxis, ...] / 255
        return self.model.predict(arr)
