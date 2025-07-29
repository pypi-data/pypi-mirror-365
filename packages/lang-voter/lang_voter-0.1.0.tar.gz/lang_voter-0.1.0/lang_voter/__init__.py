from .voter import get_prediction

def predict_language(text: str, voting: str = "hard") -> str:
    return get_prediction(text, voting=voting)