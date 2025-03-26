#smolVLM/main.py

import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import time

print("Starting process...")
start_total = time.time()

# Load model and processor
print("Loading model and processor...")
start_load = time.time()
processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
model = AutoModelForVision2Seq.from_pretrained(
    "HuggingFaceTB/SmolVLM-256M-Instruct",
    torch_dtype=torch.float16
).to("cuda" if torch.cuda.is_available() else "cpu")
load_time = time.time() - start_load
print(f"Model loading time: {load_time:.2f} seconds")

# Load image
print("\nProcessing image...")
start_process = time.time()
image = Image.open("rabbit.jpg")

# Create input messages specifically for text extraction
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Please read and extract all text that appears in this image. Only output the text, nothing else."}
        ]
    }
]

# Prepare inputs
prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(text=prompt, images=[image], return_tensors="pt")
inputs = inputs.to("cuda" if torch.cuda.is_available() else "cpu")

# Generate outputs with focused parameters
generated_ids = model.generate(
    **inputs,
    max_new_tokens=100,  # Reduced for text-only output
    num_beams=2,
    temperature=0.3,     # Lower temperature for more focused output
    do_sample=False,     # Disabled sampling for more deterministic output
    repetition_penalty=1.2
)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
process_time = time.time() - start_process

print("\nExtracted text from image:")
print("-" * 50)
print(generated_text)

total_time = time.time() - start_total
print("\nTiming Summary:")
print("-" * 50)
print(f"Model Loading Time: {load_time:.2f} seconds")
print(f"Processing Time: {process_time:.2f} seconds")
print(f"Total Time: {total_time:.2f} seconds")
print(f"Running on: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
