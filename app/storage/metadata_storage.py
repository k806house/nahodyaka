from dataclasses import dataclass


@dataclass
class Metadata:
    filename: str
    chat_id: str
    msg_id: str
    other: dict


class MetadataStorage:
    def __init__(self):
        self.index = {}

    def add(self, emb_id, meta):
        self.index[emb_id] = meta

    def search(self, emb_id):
        return self.index[emb_id]
