import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForMultipleChoice, TrainingArguments, Trainer
import torch

# 1. Download MedMCQA dataset from Hugging Face
dataset = load_dataset('openlifescienceai/medmcqa', split='train[:1000]')  # Use a subset for demo

# 2. Prepare the tokenizer and model
model_name = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMultipleChoice.from_pretrained(model_name)

# 3. Preprocess the data for multiple-choice QA
def preprocess(example):
    choices = [example['opa'], example['opb'], example['opc'], example['opd']]
    question = example['question']
    inputs = tokenizer([question] * 4, choices, truncation=True, padding='max_length', max_length=128, return_tensors='pt')
    label = int(example['cop']) - 1  # cop is 1-based
    return {
        'input_ids': inputs['input_ids'],
        'attention_mask': inputs['attention_mask'],
        'labels': torch.tensor(label)
    }

dataset = dataset.map(preprocess)

def collate_fn(batch):
    input_ids = torch.stack([item['input_ids'] for item in batch])
    attention_mask = torch.stack([item['attention_mask'] for item in batch])
    labels = torch.tensor([item['labels'] for item in batch])
    return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': labels}

# 4. Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=1,
    per_device_train_batch_size=2,
    save_steps=10,
    save_total_limit=2,
    logging_steps=5,
    remove_unused_columns=False,
    report_to=[]
)

# 5. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=collate_fn,
)

# 6. Train the model
if __name__ == '__main__':
    print('Starting training...')
    trainer.train()
    model.save_pretrained('./ai/medqa_model')
    tokenizer.save_pretrained('./ai/medqa_model')
    print('Training complete. Model saved to ./ai/medqa_model')

# Instructions:
# Run this script with: python ai/train_medqa.py
# For full dataset, remove [:1000] in load_dataset, but ensure you have enough resources. 