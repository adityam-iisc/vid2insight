"""Configuration for evaluation models.

"""

DEFAULT_LLM_MODEL = 'gemini'

# BERT score configuration
BERT_CONFIG = {
    'language': 'en',
    'model_type': 'roberta-large',
    'num_layers': 17,
    'batch_size': 3
}

# BLEU score configuration
BLEU_CONFIG = {
    'weights_1gram': (1, 0, 0, 0),
    'weights_2gram': (0.5, 0.5, 0, 0),
    'weights_3gram': (0.33, 0.33, 0.33, 0),
    'weights_4gram': (0.25, 0.25, 0.25, 0.25)
}
