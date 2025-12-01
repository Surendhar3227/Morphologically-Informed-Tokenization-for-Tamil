import numpy as np
from datasets import load_dataset
import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import TrainingArguments, DataCollatorForTokenClassification
from transformers import Trainer

from seqeval.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
)

MODEL_NAME = [PRETRAINED_TAMIL_BERT_MODEL] # Different trained models should be mentioned here
CHECKPOINT = [SAVED_CHECKPOINT_NAME] # Different checkpoints should be mentioned here
MODEL_DIR = f"[TAMIL_BERT_MODELS_BASE_DIR]/{MODEL_NAME}/{CHECKPOINT}"
PARQUET_DIR = "./Datasets/TamilNER/WikiAnn"
OUTPUT_DIR = f"[TAMIL_BERT_MODELS_BASE_DIR]/{MODEL_NAME}/tamil_ner_finetuned"

LABELS = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for i, label in enumerate(LABELS)}

MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 5e-5

def load_parquet_dataset(parquet_dir):
    dataset = load_dataset(
        "parquet",
        data_files={
            "train": f"{parquet_dir}/train.parquet",
            "validation": f"{parquet_dir}/validation.parquet",
            "test": f"{parquet_dir}/test.parquet",
        },
    )
    return dataset

def tokenize_and_align_labels(examples, tokenizer, max_length=MAX_LENGTH):
    sentences = [" ".join(tokens) for tokens in examples["tokens"]]
    tokenized_inputs = tokenizer(
        sentences,
        truncation=True,
        padding=False,
        max_length=max_length,
        is_split_into_words=False,
    )
    new_labels = []
    for i, label_list in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label_list[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        new_labels.append(label_ids)

    tokenized_inputs["labels"] = new_labels
    return tokenized_inputs

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)
    true_labels = []
    true_predictions = []
    
    for prediction, label in zip(predictions, labels):
        true_label_seq = []
        true_pred_seq = []
        
        for pred_id, label_id in zip(prediction, label):
            if label_id != -100:
                true_label_seq.append(ID2LABEL[label_id])
                true_pred_seq.append(ID2LABEL[pred_id])
        
        true_labels.append(true_label_seq)
        true_predictions.append(true_pred_seq)
    return {
        "precision": precision_score(true_labels, true_predictions),
        "recall": recall_score(true_labels, true_predictions),
        "f1": f1_score(true_labels, true_predictions),
        "accuracy": accuracy_score(true_labels, true_predictions),
    }


def print_detailed_report(predictions, labels, dataset_split, split_name):
    predictions = np.argmax(predictions, axis=2)
    
    true_labels = []
    true_predictions = []
    
    for prediction, label in zip(predictions, labels):
        true_label_seq = []
        true_pred_seq = []
        
        for pred_id, label_id in zip(prediction, label):
            if label_id != -100:
                true_label_seq.append(ID2LABEL[label_id])
                true_pred_seq.append(ID2LABEL[pred_id])
        
        true_labels.append(true_label_seq)
        true_predictions.append(true_pred_seq)

    print("\n" + "="*60)
    print(f"DETAILED CLASSIFICATION REPORT - {split_name.upper()}")
    print("="*60)
    print(classification_report(true_labels, true_predictions, digits=4))

    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS")
    print("="*60)
    for i in range(min(5, len(true_labels))):
        print(f"\nExample {i+1}:")
        print(f"Tokens: {' '.join(dataset_split[i]['tokens'][:20])}")  # First 20 tokens
        print(f"True:   {' '.join(true_labels[i][:20])}")
        print(f"Pred:   {' '.join(true_predictions[i][:20])}")

def main():
    print(f"Loading custom {MODEL_NAME} model from {MODEL_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_DIR,
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    dataset = load_parquet_dataset(PARQUET_DIR)

    tokenized_datasets = dataset.map(
        lambda examples: tokenize_and_align_labels(examples, tokenizer),
        batched=True,
        remove_columns=["tokens", "ner_tags"],
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="steps",
        eval_steps=500,
        save_steps=500,
        save_total_limit=3,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        warmup_steps=500,
        logging_dir=f"{OUTPUT_DIR}/logs",
        logging_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    print("\n" + "="*60)
    print("STARTING FINE-TUNING")
    print("="*60)
    trainer.train()

    print("\n" + "="*60)
    print("SAVING FINE-TUNED MODEL")
    print("="*60)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Fine-tuned model saved to {OUTPUT_DIR}")

    print("\n" + "="*60)
    print("EVALUATING ON VALIDATION SET")
    print("="*60)
    val_results = trainer.evaluate(tokenized_datasets["validation"])
    print(f"Validation F1: {val_results['eval_f1']:.4f}")
    print(f"Validation Precision: {val_results['eval_precision']:.4f}")
    print(f"Validation Recall: {val_results['eval_recall']:.4f}")

    print("\n" + "="*60)
    print("EVALUATING ON TEST SET")
    print("="*60)
    test_results = trainer.evaluate(tokenized_datasets["test"])
    print(f"Test F1: {test_results['eval_f1']:.4f}")
    print(f"Test Precision: {test_results['eval_precision']:.4f}")
    print(f"Test Recall: {test_results['eval_recall']:.4f}")

    print("\n" + "="*60)
    print("GENERATING DETAILED EVALUATION REPORTS")
    print("="*60)
    
    val_predictions, val_labels, _ = trainer.predict(tokenized_datasets["validation"])
    print_detailed_report(val_predictions, val_labels, dataset["validation"], "validation")
    
    test_predictions, test_labels, _ = trainer.predict(tokenized_datasets["test"])
    print_detailed_report(test_predictions, test_labels, dataset["test"], "test")


if __name__ == "__main__":
    main()