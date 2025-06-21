# Vid2Insight Evaluation Framework

This directory contains the evaluation framework for the Vid2Insight project, which helps measure the quality of generated content compared to ground truth data.

## Directory Structure

```
evaluation/
├── __init__.py
├── README.md (this file)
├── calculate_all_metrics.py  # Core metrics calculation functions
├── ground_truth/             # Reference/ground truth content
│   ├── detailed_product_Doc.txt
│   ├── executive_summary.txt
│   ├── General_purpose_chat.txt
│   ├── ground_truth.txt
│   ├── Product_chat.txt
│   ├── Student_chat.txt
│   ├── student_mcq.txt
│   ├── student_summary.txt
│   └── Summary.txt
├── model_outputs/            # Generated outputs from models
│   ├── model_generated_exec_summary.txt
│   ├── model_generated_general_chat.txt
│   ├── model_generated_product_chat.txt
│   ├── model_generated_product_doc.txt
│   ├── model_generated_student_chat.txt
│   ├── model_generated_student_mcq.txt
│   └── model_generated_student_summary.txt
├── reports/                  # Evaluation reports
│   ├── exec_summary_evaluation_report.md
│   ├── general_chat_evaluation_report.md
│   ├── product_chat_evaluation_report.md
│   ├── product_doc_evaluation_report.md
│   ├── student_chat_evaluation_report.md
│   ├── student_mcq_evaluation_report.md
│   └── student_summary_evaluation_report.md
├── generate_output/          # Scripts to generate model outputs
│   ├── generate_exec_summary.py
│   ├── generate_exec_summary_direct.py
│   ├── generate_general_chat.py
│   ├── generate_product_chat.py
│   ├── generate_product_doc.py
│   ├── generate_student_chat.py
│   ├── generate_student_mcq.py
│   └── generate_student_summary.py
└── evaluate_scores/          # Scripts to evaluate and score outputs
    ├── direct_transcript_evaluation.py
    ├── evaluate_exec_summary.py
    ├── evaluate_general_chat.py
    ├── evaluate_product_chat.py
    ├── evaluate_product_doc.py
    ├── evaluate_student_chat.py
    ├── evaluate_student_mcq.py
    ├── evaluate_student_summary.py
    ├── evaluate_transcript.py
    └── extract_transcript.py
```

## Evaluation Workflow

1. **Generate Outputs**: Scripts in the `generate_output/` directory extract information from transcripts and generate content using the Vid2Insight models.

2. **Compare with Ground Truth**: Scripts in the `evaluate_scores/` directory compare the generated content with ground truth files from `ground_truth/` directory using various metrics.

3. **Review Reports**: The evaluation results are saved as markdown files in the `reports/` directory for easy review.

## Running Evaluations

Each evaluation script follows a common pattern:

```bash
# Example command to run evaluation for executive summary
python -m evaluation.evaluate_scores.evaluate_exec_summary

# Example command to run evaluation for student summary
python -m evaluation.evaluate_scores.evaluate_student_summary
```

## Metrics Used

The evaluation framework uses the following metrics:

- **BERT Score**: Measures semantic similarity between generated text and reference text
- **BLEU Score**: Measures n-gram precision between generated text and reference text
- **ROUGE Score**: Measures overlap of n-grams between generated text and reference text
- **LLM Evaluation**: Uses language models to evaluate specific aspects such as:
  - Correctness
  - Relevance
  - Coherence
  - Fluency
  - Helpfulness
  - Harmlessness

## Adding New Evaluation Tasks

To add a new evaluation task:

1. Add ground truth file in `ground_truth/`
2. Create generate script in `generate_output/`
3. Create evaluation script in `evaluate_scores/`
4. Run the evaluation and review the results in the `reports/` directory
