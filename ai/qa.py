import torch
from transformers import pipeline

class MedicalQABot:
    """Medical Q&A bot using Hugging Face Transformers."""
    def __init__(self, model_name='deepset/bert-base-cased-squad2'):
        self.qa_pipeline = pipeline('question-answering', model=model_name, tokenizer=model_name)

    def answer(self, question, context):
        """Answer a question given a context string."""
        result = self.qa_pipeline({'question': question, 'context': context})
        return result['answer'] 