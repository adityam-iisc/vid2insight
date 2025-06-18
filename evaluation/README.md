# Text Score Evaluation Toolkit

A comprehensive code for evaluating the quality of generated text through various metrics, including both automated metrics and LLM-based evaluation.

## Features

- **Multiple Evaluation Metrics**:
  - **BERT Score**: Evaluates semantic similarity using contextual embeddings
  - **BLEU Score**: Measures n-gram overlap between generated text and reference
  - **ROUGE Score**: Evaluates recall and precision of n-grams
  - **LLM-based Evaluation**: Uses a large language model as judge to evaluate various aspects of text quality

## Getting Started

### Prerequisites

Required packages:
```
bert-score
nltk
rouge
pandas
matplotlib
langchain-core
google-generativeai==0.6.15 (specific version due to compatibility)
```

### Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root directory with your API keys:
```
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

```
vid2insight/
├── evaluation/
│   ├── __init__.py
│   ├── calculate_all_metrics.py
│   ├── llm_evaluation.py
│   ├── langsmith_evaluation.py
│   ├── run_evaluation.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── model_config.py
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── criteria.py
│   │   └── paths.py
│   └── metrics/
│       ├── __init__.py
│       ├── calculate_bert_score.py
│       ├── calculate_bleu_score.py
│       └── calculate_rouge_score.py
```

## Usage

### Command Line Interface

The code provides a simple command line interface. You can use either the wrapper script in the project root or run the evaluation script directly from the eval folder:

#### Run a specific evaluation:

```bash
# Using the root wrapper script
python run_evaluation.py bert --reference ground_truth.txt --prediction model_generated.txt
python run_evaluation.py bleu --reference ground_truth.txt --prediction model_generated.txt
python run_evaluation.py rouge --reference ground_truth.txt --prediction model_generated.txt
python run_evaluation.py llm --reference ground_truth.txt --prediction model_generated.txt

# Or directly using the evaluation script
python evaluation/run_evaluation.py bert --reference ground_truth.txt --prediction model_generated.txt
```

#### Run all evaluations:

```bash
python run_evaluation.py all --reference ground_truth.txt --prediction model_generated.txt
```

#### Specify custom LLM evaluation metrics:

```bash
python run_evaluation.py llm --reference ground_truth.txt --prediction model_generated.txt --metrics correctness relevance fluency
```

#### Specify custom metrics for all evaluations:

```bash
python run_evaluation.py all --reference ground_truth.txt --prediction model_generated.txt --metrics bert bleu llm
```

### Using the Python API

You can also use the toolkit programmatically:

```python
from evaluation import calculate_bert_score, calculate_bleu_score, calculate_rouge_score, run_llm_evaluation, calculate_all_metrics

# Run individual evaluations
bert_results = calculate_bert_score('ground_truth.txt', 'model_generated.txt')
bleu_results = calculate_bleu_score('ground_truth.txt', 'model_generated.txt')
rouge_results = calculate_rouge_score('ground_truth.txt', 'model_generated.txt')
llm_results = run_llm_evaluation('ground_truth.txt', 'model_generated.txt')

# Or run all evaluations at once
all_results = calculate_all_metrics('ground_truth.txt', 'model_generated.txt')
```

## Configuration

The toolkit uses several configuration files:

- `evaluation/constants/criteria.py`: Defines evaluation criteria and metrics
- `evaluation/constants/paths.py`: Defines file paths and output directories
- `evaluation/config/model_config.py`: Configures LLM models for evaluation

## Output

Evaluation results are saved to the `eval_results` directory:

- JSON files with detailed scores
- CSV file with LLM evaluation results
- Visualization of LLM evaluation scores
- Combined file with all evaluation results

## License

[MIT License](LICENSE)
