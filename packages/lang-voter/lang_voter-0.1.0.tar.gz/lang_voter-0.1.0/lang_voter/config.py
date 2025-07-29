# LANG_VOTER/config.py

MODEL_CONFIG = [
    {
        "name": "svc",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/word_char_combined_tfidf_vectorizer.pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/svm-C1-kernel-linear---word(1,2)+char(2,6).pkl",
    },
    {
        "name": "sgd",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/SGD_word+char_tfidf_vectorizer.pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/sgd_model.pkl",
    },
    {
        "name": "random_forest",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/vectorizer---word(1-2)+char(2-6).pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/rf-n100-depthNone-crit-gini---word(1-2)+char(2-6).pkl",
    },
    {
        "name": "naive_bayes",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/word_char_combined_vectorizer---combined-char2-6-word1-2.pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/mnb-alpha-1.0---combined-char2-6-word1-2.pkl",
    },
    {
        "name": "decision_tree",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/vectorizer---dt-depthNone-crit-gini---combined-word(1,2)+char(2,6).pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/dt-depthNone-crit-gini---combined-word(1,2)+char(2,6).pkl",
    },
    
    {
        "name": "logistic",
        "vectorizer_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/logreg-C1-penaltyl2---vectorizer---word(1-2)+char(2-6).pkl",
        "model_url": "https://huggingface.co/yash-ingle/IDLD_Models/resolve/main/logreg-C1-penaltyl2---word(1-2)+char(2-6).pkl",
    }
]
