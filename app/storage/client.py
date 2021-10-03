from urllib.parse import urljoin

import requests

from .metadata_storage import Metadata


class StorageClient:
    def __init__(self, url):
        self.url = url

    def emb_add(self, emb):
        response = requests.post(urljoin(self.url, "emb/add"),
                                 json={"emb": emb.tolist()})
        data = response.json()
        return data["emb_id"]

    def emb_k_nbrs(self, emb, k):
        response = requests.get(urljoin(self.url, "emb/k_nbrs"),
                                json={
                                    "emb": emb.tolist(),
                                    "k": k
                                })
        data = response.json()
        k_nbrs = []
        for match in data["k_nbrs"]:
            k_nbrs.append((match["dist"], match["emb_id"]))
        return k_nbrs

    def meta_add(self, emb_id, meta):
        requests.post(urljoin(self.url, "meta/add"),
                      json={
                          "emb_id": emb_id,
                          "meta": {
                              "filename": meta.filename,
                              "chat_id": meta.chat_id,
                              "msg_id": meta.msg_id,
                              "other": meta.other
                          },
                      })
        return

    def meta_search(self, emb_id):
        response = requests.get(urljoin(self.url, "meta/search"),
                                json={"emb_id": emb_id})
        data = response.json()
        m = data["meta"]
        meta = Metadata(m["filename"], m["chat_id"], m["msg_id"], m["other"])
        return meta
