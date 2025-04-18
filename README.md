# About

This repo is prepared for my lecture on fine-tuning OpenAI models with the Multi-Aspect Multi-Sentiment (MAMS) dataset for Aspect-Based Sentiment Analysis: [https://github.com/siat-nlp/MAMS-for-ABSA](https://github.com/siat-nlp/MAMS-for-ABSA).

## Setup

It's recommended to use a virtual environment to manage dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

The required dependencies are listed in `requirements.txt`:
- numpy: For numerical operations and statistics
- tiktoken: For token counting (used by OpenAI)

## Sample Datasets

For quick testing of OpenAI fine-tuning, you can use the following prepared datasets:
- Training data: `openai-jsonl/train_chat_200.jsonl` (200 examples)
- Validation data: `openai-jsonl/val_chat_15.jsonl` (15 examples)

These files are already formatted in the chat format required by OpenAI's fine-tuning API.

## Scripts Usage Guide

### XML to JSONL Transformation

The `transform_to_jsonl.py` script converts XML files from the MAMS dataset to JSONL format, with two output format options: standard and chat.

```bash
python transform_to_jsonl.py <xml_file_path> [--format FORMAT]
```

- `<xml_file_path>`: Path to the XML file to transform
- `--format FORMAT`: Output format type (standard or chat, default: standard)


Standard format (input/output pairs):
```bash
python transform_to_jsonl.py ./xml/test.xml
```

Chat format (system/user/assistant messages):
```bash
python transform_to_jsonl.py ./xml/train.xml --format chat
```

#### XML Format

```xml
<sentence>
  <text>We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible.</text>
  <aspectCategories>
    <aspectCategory category="place" polarity="neutral"/>
    <aspectCategory category="food" polarity="negative"/>
  </aspectCategories>
</sentence>
```

#### Transformed JSONL Formats

**Standard Format**:

```json
{
  "input": "We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible.",
  "output": {
    "place": "neutral",
    "food": "negative",
    "service": "unknown"
  }
}
```

**Chat Format**:

```json
{"messages": [{"role": "system", "content": "you are an expert data labeling assistant that always outputs json format"}, {"role": "user", "content": "We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible."}, {"role": "assistant", "content": "{\"place\":\"neutral\",\"food\":\"negative\",\"service\":\"unknown\"}"}]}
```

### JSONL Sampling

The `sample_jsonl.py` script allows you to randomly sample a subset of examples from a JSONL file.

```bash
python sample_jsonl.py input_file output_file sample_size [--seed SEED]
```

- `input_file`: Path to the input JSONL file
- `output_file`: Path to the output JSONL file
- `sample_size`: Number of samples to extract
- `--seed`: Optional random seed for reproducibility

Sample 200 examples from train_chat.jsonl:
```bash
python sample_jsonl.py ./openai-jsonl/train_chat.jsonl ./openai-jsonl/train_chat_200.jsonl 200 --seed 42
```

### Fine-tuning Dataset Validation and Cost Estimation

The `openai-finetune-check.py` script validates your JSONL dataset for OpenAI fine-tuning compatibility and provides cost estimates.

```bash
python openai-finetune-check.py <file_path> [--model MODEL]
python openai-finetune-check.py ./openai-jsonl/train_chat_200.jsonl --model gpt-4o-mini-2024-07-18
```

- `<file_path>`: Path to the JSONL file to check
- `--model`: Model to use for fine-tuning cost estimation (default: gpt-4.1-mini-2025-04-14)
  - Available options: gpt-4.1-2025-04-14, gpt-4.1-mini-2025-04-14, gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18

Check a dataset with default model (gpt-4.1-mini-2025-04-14):
```bash
python openai-finetune-check.py ./openai-jsonl/train_chat_200.jsonl
```

Check a dataset with a specific model:
```bash
python openai-finetune-check.py ./openai-jsonl/train_chat_200.jsonl --model gpt-4.1-2025-04-14
```

The script provides:
- Format validation (ensuring compatibility with OpenAI's requirements)
- Dataset statistics (number of examples, message distribution, token counts)
- Token limit warnings
- Training epochs estimation
- Cost estimation based on the selected model
- Reference pricing for inference


### Windsurf Prompt

Examples give to Windsurf to develop the scripts:

```
<sentence>
  <text>We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible.</text>
  <aspectCategories>
    <aspectCategory category="place" polarity="neutral"/>
    <aspectCategory category="food" polarity="negative"/>
  </aspectCategories>
</sentence>
<sentence>
  <text>The food was good, but it's not worth the wait--or the lousy service.</text>
  <aspectCategories>
    <aspectCategory category="food" polarity="positive"/>
    <aspectCategory category="service" polarity="negative"/>
  </aspectCategories>
</sentence>

{
  "input": "We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible.",
  "output": {
    "place": "neutral",
    "food": "negative"
    "service": "unknown"
  }
},
{
  "input": "The food was good, but it's not worth the wait--or the lousy service.",
  "output": {
  "place": "unknown",
    "food": "positive",
    "service": "negative"
  }
}

{"messages": [{"role": "system", "content": "you are an expert data labeling assistant that always outputs json format"}, {"role": "user", "content": "We went again and sat at the bar this time, I had 5 pints of guinness and not one buy-back, I ordered a basket of onion rings and there were about 5 in the basket, the rest was filled with crumbs, the chili was not even edible."}, {"role": "assistant", "content": "{"place": "neutral", "food":"negative", "service": "unknown"}"}]}
{"messages": [{"role": "system", "content": "you are an expert data labeling assistant"}, {"role": "user", "content": "The food was good, but it's not worth the wait--or the lousy service."}, {"role": "assistant", "content": "{"place": "unknown", "food":"positive", "service": "negative"}"}]}
```