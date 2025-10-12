from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, TaskType, get_peft_model
from datasets import Dataset

from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


def default():

    model_path = "ibm-granite/granite-4.0-micro"
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # drop device_map if running on CPU
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.eval()


    with open("llm_fine_tuning/data/sample1.txt", 'r') as f:
        # Read the entire content of the file as a single string
        content = f.read()
        #print(content)

    # change input text as desired
    chat = [
        #{ "role": "user", "content": f"Please summarize the content: {content}" },
        { "role": "user", "content": f"write code to check even or odd number" },
    ]
    chat = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    print(f"\nChat: {chat}")

    # tokenize the text
    input_tokens = tokenizer(chat, return_tensors="pt")
    print(f"\ninput token: {input_tokens}")

    # generate output tokens
    output = model.generate(**input_tokens, 
                            max_new_tokens=1000)

    # decode output tokens into text
    output = tokenizer.batch_decode(output)

    # print output
    print("Output:\n\n", output[0])



def get_model_and_tokenizr():
    # Load model and tokenizer
    model_id = "ibm-granite/granite-4.0-micro"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    return model_id, model, tokenizer


def get_formatted_data():

    #print([dataset.id for dataset in list_datasets()])
    ds = load_dataset("gopalkalpande/bbc-news-summary", split='train')
    print(ds[0])

    formatted_data = [f"<|user|>\ncategory: {example['File_path']} Articles: {example['Articles']}\n<|assistant|>\n{example['Summaries']}" for example in ds]

    print("\n\n", formatted_data[0])
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
        output_dir="llm_fine_tuning/data/granite-4.0-micro-lora",
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

    model.save_pretrained("llm_fine_tuning/data/granite-4.0-micro-lora")  
    tokenizer.save_pretrained("llm_fine_tuning/data/granite-4.0-micro-lora")


if __name__ =="__main__":
    fine_tune()