from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, TaskType, get_peft_model
import json
from datasets import Dataset
from huggingface_hub import list_datasets

from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel
import torch


def get_formatted_data():

    #print([dataset.id for dataset in list_datasets()])

    #Load example dataset from file
    with open("llm_fine_tuning/data/concise_dataset.json", "r") as f:
        examples = json.load(f)

    # Format and tokenize
    formatted_data = [f"<|user|>\n{example['instruction']}\n<|assistant|>\n{example['response']}" for example in examples]

    return formatted_data


def get_train_test_split(tokenizer):
   
    # Tokenize dataset
    tokenized = tokenizer(
        get_formatted_data(),
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )

    # Wrap in Hugging Face Dataset
    dataset = Dataset.from_dict({
        "input_ids": tokenized["input_ids"].tolist(),
        "attention_mask": tokenized["attention_mask"].tolist(),
        "labels": tokenized["input_ids"].tolist()
    })

    # Split into train and eval
    split_dataset = dataset.train_test_split(test_size=0.1)
    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]

    return train_dataset, eval_dataset

def get_model_and_tokenizr():
    # Load model and tokenizer
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    return model_id, model, tokenizer

def fine_tune():
    # Load model and tokenizer
    _, model, tokenizer = get_model_and_tokenizr()

    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],  # adjust if needed
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    # Apply LoRA adapters to the base model
    model = get_peft_model(model, peft_config)

    train_dataset, eval_dataset = get_train_test_split(tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="llm_fine_tuning/data/tinyllama-lora",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=5e-5,
        num_train_epochs=3,
        logging_steps=1,
        eval_strategy="epoch",
        save_strategy="epoch",
        optim="adamw_torch",
    )

    # Trainer setup
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    # Start training
    trainer.train()

    model.save_pretrained("llm_fine_tuning/data/tinyllama-lora")  
    tokenizer.save_pretrained("llm_fine_tuning/data/tinyllama-lora")


def generate_response(model, prompt, max_new_tokens=500):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)

    # Get text after <|assistant|>
    if "<|assistant|>" in full_output:
        response = full_output.split("<|assistant|>\n")[1].strip()
    else:
        response = full_output.strip()

    # Stop at first newline or period if needed
    for stop_token in ["\n", ".", "!", "?"]:
        if stop_token in response:
            response = response.split(stop_token)[0].strip()
            break

    return response


def test():
    # Load tokenizer
    model_id, _, tokenizer = get_model_and_tokenizr()

    # Inference helper

    # Prompt
    instruction = "What is the capital of Kenya?"
    prompt = f"<|user|>\n{instruction}\n<|assistant|>\n"

    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(model_id)

    # Load LoRA-adapted model
    lora_model = AutoModelForCausalLM.from_pretrained(model_id)
    lora_model = PeftModel.from_pretrained(lora_model, "llm_fine_tuning/data/tinyllama-lora")

    # Generate responses
    base_response = generate_response(base_model, prompt)
    lora_response = generate_response(lora_model, prompt)

    # Print results
    print("=== Base Model Response ===")
    print("Question: ",instruction)
    print("Response: ",base_response)
    print("\n=== LoRA-Finetuned Model Response ===")
    print("Question: ",instruction)
    print("Response: ",lora_response)


if __name__ == "__main__":
    model_id, model, tokenizer = get_model_and_tokenizr()

    # formatted_data = get_formatted_data()
    # print(len(formatted_data))

    # train, test = get_train_test_split(tokenizer)
    # print( len(train), len(test) )

    # print("starting to fine tune")
    # fine_tune()
    # print("completed fine tune")

    test()