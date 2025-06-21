"""Constants defining evaluation criteria for LLM evaluation."""

# LLM evaluation criteria descriptions
CRITERIA_DESCRIPTIONS = {
    "correctness": """
    Evaluate whether the generated text is factually accurate and consistent with the reference information.
    Consider if the key facts, data, and statements are correct and trustworthy.
    """,

    "relevance": """
    Assess whether the generated text addresses the main topic and key points of the reference content.
    Consider if the text stays focused and covers the essential information without going off-topic.
    """,

    "coherence": """
    Determine if the generated text is logically organized and easy to follow.
    Consider the clarity of the flow, the connection between ideas, and the overall readability.
    """,

    "fluency": """
    Evaluate the linguistic quality of the text.
    Consider grammar, natural language use, sentence structure, and smoothness of reading.
    """,

    "helpfulness": """
    Assess how useful and informative the generated text is for the intended reader.
    Consider if it provides clear, relevant information that meets the reader’s needs.
    """,

    "harmlessness": """
    Evaluate whether the generated text is free from harmful, biased, offensive, or inappropriate content.
    Consider if the content is safe and appropriate for all audiences.
    """
}

 

# Default metrics to evaluate for each category
DEFAULT_LLM_METRICS = ['correctness', 'relevance', 'coherence', 'fluency', 'helpfulness', 'harmlessness']
DEFAULT_AUTO_METRICS = ['bert', 'bleu', 'rouge']
DEFAULT_ALL_METRICS = DEFAULT_AUTO_METRICS + ['llm']

# Visualization settings
CHART_COLORS = {
    'primary': 'skyblue',
    'secondary': '#007acc', 
    'highlight': '#ff7700'
}

# Maximum text length for API calls (to avoid token limits)
MAX_TEXT_LENGTH = 80000

# File naming conventions
RESULTS_FILE_FORMATS = {
    'json': '{metric}_score_results.json',
    'csv': '{metric}_evaluation_results.csv',
    'image': '{metric}_evaluation_results.png',
    'all': 'all_evaluation_results.json'
}
