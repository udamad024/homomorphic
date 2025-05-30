# cloud_compute_app.py
from fastapi import FastAPI
import tenseal as ts
import os
from azure.storage.blob import BlobClient

cloud_app = FastAPI()

@cloud_app.get("/compute/average/")
def compute_average():
    context = ts.context_from(open("context.tenseal", "rb").read())
    
    blob = BlobClient.from_connection_string(
        conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        container_name="encrypted-data",
        blob_name="bp.bin"
    )
    downloaded = blob.download_blob().readall()

    encrypted_vectors = []
    i = 0
    while i < len(downloaded):
        length = int.from_bytes(downloaded[i:i+4], 'big')
        i += 4
        enc_bytes = downloaded[i:i+length]
        i += length
        encrypted_vectors.append(ts.ckks_vector_from(context, enc_bytes))

    result = encrypted_vectors[0]
    for vec in encrypted_vectors[1:]:
        result += vec
    avg = result * (1.0 / len(encrypted_vectors))

    return {"encrypted_result": avg.serialize().hex()}
