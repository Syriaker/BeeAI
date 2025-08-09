from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import login
from django.conf import settings
import os


class MistralService:
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
    TOKENIZER = None
    MODEL = None
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    def load_model(cls):

        if cls.MODEL is None or cls.TOKENIZER is None:
            print(f"Загрузка модели {cls.MODEL_NAME}...")
            login(token="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") #спрятать потом
            cls.TOKENIZER = AutoTokenizer.from_pretrained(cls.MODEL_NAME)
            cls.MODEL = AutoModelForCausalLM.from_pretrained(cls.MODEL_NAME, torch_dtype=torch.float16)
            cls.MODEL.to(cls.DEVICE)
            cls.MODEL.eval()
            print("Модель загружена.")

    @classmethod
    def generate_response(cls, prompt: str) -> str:

        cls.load_model()

        formatted_prompt = f"Проанализируй следующие данные из Яндекс.Метрики и дай краткое заключение: {prompt}.  В заключении укажи основные тренды и предложи улучшения." #тестовый промпт, поменять потом под задачи

        inputs = cls.TOKENIZER(formatted_prompt, return_tensors="pt").to(cls.DEVICE)

        with torch.no_grad():
            outputs = cls.MODEL.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.15
            )

        decoded_output = cls.TOKENIZER.decode(outputs[0], skip_special_tokens=True)
        return decoded_output
