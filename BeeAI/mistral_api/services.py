from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import login
from django.conf import settings
import os
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

class MistralService:
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
    TOKENIZER = None
    MODEL = None
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(DEVICE)

    @classmethod
    def load_model(cls):
        if cls.MODEL is not None:
            print("Модель уже была загружена.")
            return

        if cls.MODEL is None or cls.TOKENIZER is None:


            print(f"Загрузка модели {cls.MODEL_NAME}...")
            login(token="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") #спрятать потом
            cls.TOKENIZER = AutoTokenizer.from_pretrained(cls.MODEL_NAME, use_fast=False)
            cls.MODEL = AutoModelForCausalLM.from_pretrained(
                cls.MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto"  # Позволяет transformers оптимально распределить модель
            )
            cls.MODEL.eval()
            print("Модель загружена.")

    @classmethod
    def generate_response(cls, prompt: str) -> str:

        formatted_prompt = f"<s>[INST] Проанализируй следующие данные из Яндекс.Метрики и дай очень краткое заключение на русском языке (ограничься двумя предложениями): {prompt}. В заключении предложи улучшения и способы увеличть полученные цифры, основываясь на полученных данных. [/INST]"

        #inputs = cls.TOKENIZER(formatted_prompt, return_tensors="pt").to(cls.DEVICE)
        inputs = cls.TOKENIZER(formatted_prompt, return_tensors="pt").to(cls.MODEL.device)
        with torch.no_grad():
            outputs = cls.MODEL.generate(
                **inputs,
                max_new_tokens=250,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.15
            )
        full_output = cls.TOKENIZER.decode(outputs[0], skip_special_tokens=True)

        if "[/INST]" in full_output:
            response = full_output.split("[/INST]")[1].strip()
        else:
            response = full_output.replace(formatted_prompt, "").strip()

        return response