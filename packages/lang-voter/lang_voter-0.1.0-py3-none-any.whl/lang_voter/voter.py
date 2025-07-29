from .config import model_urls
from .model_loader import load_model_and_vectorizer
from sklearn.ensemble import VotingClassifier
from collections import Counter

def get_prediction(text, voting="hard"):
    predictions = []
    probs = []

    for name, urls in model_urls.items():
        model, vectorizer = load_model_and_vectorizer(name, urls)
        vec = vectorizer.transform([text])
        pred = model.predict(vec)[0]
        predictions.append(pred)
        if hasattr(model, "predict_proba"):
            probs.append(model.predict_proba(vec)[0])

    if voting == "hard":
        return Counter(predictions).most_common(1)[0][0]
    elif voting == "soft" and probs:
        import numpy as np
        avg_prob = sum(probs) / len(probs)
        return model.classes_[np.argmax(avg_prob)]
    else:
        raise ValueError("Unsupported voting or no probability models available")