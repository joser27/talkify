#smolVLM/main.py

import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image

# Load model and processor
processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
model = AutoModelForVision2Seq.from_pretrained(
    "HuggingFaceTB/SmolVLM-256M-Instruct",
    torch_dtype=torch.float16
).to("cuda" if torch.cuda.is_available() else "cpu")

# Load your image
image = Image.open("rabbit.jpg")

# Create input messages
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Please read and transcribe any text visible in this image, maintaining the original formatting."}
        ]
    }
]

# Prepare inputs
prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(text=prompt, images=[image], return_tensors="pt")
inputs = inputs.to("cuda" if torch.cuda.is_available() else "cpu")

# Generate outputs with better parameters
generated_ids = model.generate(
    **inputs,
    max_new_tokens=500,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.2,
    num_return_sequences=1
)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("\nModel's description of the image:")
print("-" * 50)
print(generated_text)
