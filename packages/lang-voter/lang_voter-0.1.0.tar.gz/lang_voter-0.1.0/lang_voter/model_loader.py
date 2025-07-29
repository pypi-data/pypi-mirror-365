import os
import pickle
import requests

def download_and_load(url, save_path):
    if not os.path.exists(save_path):
        r = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(r.content)
    with open(save_path, 'rb') as f:
        return pickle.load(f)

def load_model_and_vectorizer(name, urls, cache_dir="~/.indlang_voter"):
    os.makedirs(os.path.expanduser(cache_dir), exist_ok=True)
    model_path = os.path.expanduser(os.path.join(cache_dir, f"{name}_model.pkl"))
    vec_path = os.path.expanduser(os.path.join(cache_dir, f"{name}_vectorizer.pkl"))
    model = download_and_load(urls['model'], model_path)
    vectorizer = download_and_load(urls['vectorizer'], vec_path)
    return model, vectorizer