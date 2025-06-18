"""Configuration for evaluation models."""

# LLM model configurations
LLM_MODELS = {
    'gemini': {
        'provider': 'google_genai',
        'model_name': 'gemini-2.0-flash-001',
        'max_tokens': 2048
    },
    'gpt': {
        'provider': 'openai',
        'model_name': 'gpt-4o',
        'max_tokens': 2048
    },
    'azure_openai': {
        'provider': 'azure_openai',
        'model_name': 'gpt-4',
        'max_tokens': 2048
    }
}

# Default model to use for evaluation
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
