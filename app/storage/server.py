from flask import Flask, request

from embedding_storage import EmbeddingStorage
from metadata_storage import Metadata, MetadataStorage

global emb_storage
emb_storage = EmbeddingStorage()

global meta_storage
meta_storage = MetadataStorage()

app = Flask(__name__)


@app.route("/emb/add", methods=["POST"])
def emb_add():
    emb = request.json["emb"]
    emb_id = emb_storage.add(emb)
    return {"emb_id": emb_id}


@app.route("/emb/k_nbrs", methods=["GET"])
def emb_k_nbrs():
    emb = request.json["emb"]
    k = request.json["k"]
    k_nbrs = emb_storage.k_nbrs(emb, k)
    return {
        "k_nbrs": [{
            "emb_id": emb_id,
            "dist": float(dist)
        } for dist, emb_id in k_nbrs]
    }


@app.route("/meta/add", methods=["POST"])
def meta_add():
    m = request.json["meta"]
    meta = Metadata(m["filename"], m["chat_id"], m["msg_id"], m["other"])
    meta_storage.add(request.json["emb_id"], meta)
    return {}


@app.route("/meta/search", methods=["GET"])
def meta_search():
    meta = meta_storage.search(request.json["emb_id"])
    return {"meta": meta}


if __name__ == "__main__":
    app.run(debug=True)
