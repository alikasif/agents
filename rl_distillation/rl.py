import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import ollama  # pip install ollama

# ----------------------------
# Fixed answer choices (policy output space)
# ----------------------------
ANSWERS = [
    "yes",
    "no",
    "maybe",
    "I don't know",
    "Paris",
    "Mumbai",
    "joke: why did the chicken cross the road?",
    "greeting: hello!",
    "bye!",
    "thank you!"
]

ANSWER_SIZE = len(ANSWERS)
VOCAB_SIZE = 2000

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "response_policy_ollama_nocache.pt"
OLLAMA_MODEL_NAME = "llama3.2:1b"  # or whatever local model you have

# ----------------------------
# Simple training dataset
# (question, ground_truth_answer)
# ----------------------------
TRAIN_QA = [
    ("what is the capital of france?", "Paris"),
    ("what is the capital of india?", "New Delhi"),
    ("say hello", "greeting: hello!"),
    ("tell me a joke", "joke: why did the chicken cross the road?"),
    ("say goodbye", "bye!"),
]


# ----------------------------
# Policy Network
# ----------------------------
class ResponsePolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(VOCAB_SIZE, 32)
        self.fc = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, ANSWER_SIZE)
        )

    def forward(self, tokens):
        # tokens: [batch, seq_len]
        e = self.embed(tokens)       # [batch, seq_len, emb]
        x = torch.mean(e, dim=1)     # [batch, emb]
        logits = self.fc(x)          # [batch, ANSWER_SIZE]
        return logits


policy = ResponsePolicy().to(device)
optimizer = optim.Adam(policy.parameters(), lr=1e-3)
ce_loss_fn = nn.CrossEntropyLoss()   # for strong "this is correct" updates


# ----------------------------
# Tokenizer
# ----------------------------
def tokenize(text: str) -> torch.Tensor:
    tokens = text.lower().split()
    ids = [hash(w) % VOCAB_SIZE for w in tokens]
    return torch.tensor([ids], dtype=torch.long)


# ----------------------------
# Reward model via Ollama
# ----------------------------
def get_llm_reward(question: str, agent_answer: str, ground_truth: str) -> int:
    """
    Ask Ollama to say if the agent_answer is correct (semantically)
    wrt the ground_truth for this question.
    Returns +1 or -1.
    """
    prompt = f"""
        You are a strict evaluator.

        Task:
            - You are given:
            - A user question.
            - An agent's answer.
            - The ground-truth correct answer.
        
        Rules:
            - If the agent's answer is semantically correct and matches the ground-truth meaning,
            respond with exactly: +1
            - Otherwise, respond with exactly: -1

        No explanation, no extra text. Only output +1 or -1.

        Question: {question}
        Agent answer: {agent_answer}
        Ground truth answer: {ground_truth}
"""

    resp = ollama.chat(
        model=OLLAMA_MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt.strip()}
        ],
    )
    content = resp["message"]["content"].strip()
    if "+1" in content:
        return 1
    elif "-1" in content:
        return -1
    else:
        # fallback if the model misbehaves
        return -1


# ----------------------------
# Training step: RL + (optional) extra supervised push
# ----------------------------
def train_step(question: str, ground_truth: str):
    
    # 1) forward pass
    tokens = tokenize(question).to(device)
    logits = policy(tokens)          # [1, ANSWER_SIZE]
    probs = torch.softmax(logits, dim=-1)
    dist = Categorical(probs)
    idx = dist.sample()              # [1]
    action_idx = idx.item()
    agent_answer = ANSWERS[action_idx]
    log_prob = dist.log_prob(idx)    # scalar

    # 2) get reward from Ollama
    reward = get_llm_reward(question, agent_answer, ground_truth)

    # 3) build loss
    #    RL part (REINFORCE): encourage or discourage this sampled action
    rl_loss = -log_prob * reward     # reward=+1 => push up log_prob; reward=-1 => push down

    loss = rl_loss

    # 4) If reward is positive, treat this as "this is correct"
    #    and add a stronger supervised term to really lock it in.
    if reward > 0:
        target = torch.tensor([action_idx], dtype=torch.long, device=device)
        ce_loss = ce_loss_fn(logits, target)   # make this action the top logit
        # weight it more strongly than RL if you want:
        loss = loss + 2.0 * ce_loss            # 2.0 is a hyperparameter

    # 5) optimize
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return agent_answer, reward, loss.item()


# ----------------------------
# Save / load
# ----------------------------
def save_model(path=MODEL_PATH):
    torch.save(policy.state_dict(), path)
    print(f"[+] Model saved to {path}")


def load_model_if_exists(path=MODEL_PATH):
    if os.path.exists(path):
        policy.load_state_dict(torch.load(path, map_location=device))
        policy.train()
        print(f"[+] Loaded existing model from {path}")
    else:
        print("[!] No existing model found, starting fresh.")


# ----------------------------
# Training loop
# ----------------------------
def train_with_ollama(num_steps: int = 200):
    load_model_if_exists()

    running_reward = 0.0
    best_running_reward = -999.0

    for step in range(1, num_steps + 1):
        question, ground_truth = random.choice(TRAIN_QA)

        agent_answer, reward, loss = train_step(question, ground_truth)

        running_reward = 0.95 * running_reward + 0.05 * reward

        if step % 10 == 0:
            print(
                f"Step {step:4d} | Q: {question} | agent: {agent_answer} | gt: {ground_truth} "
                f"| reward={reward:+d} | running_reward={running_reward:+.3f} | loss={loss:.4f}"
            )

        # Simple save heuristic: whenever we significantly improve running_reward
        if running_reward > best_running_reward + 0.05:
            best_running_reward = running_reward
            save_model()


# ----------------------------
# Evaluation: greedy answers after training
# ----------------------------
def eval_greedy():
    if not os.path.exists(MODEL_PATH):
        print("No trained model found, train first.")
        return

    policy.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    policy.eval()
    print("\n[Eval] Greedy responses after training:\n")

    for question, ground_truth in TRAIN_QA:
        tokens = tokenize(question).to(device)
        with torch.no_grad():
            logits = policy(tokens)
            probs = torch.softmax(logits, dim=-1)
            idx = torch.argmax(probs, dim=-1).item()
        answer = ANSWERS[idx]
        print(f"Q: {question}\n → Agent: {answer}   (GT: {ground_truth})\n")


if __name__ == "__main__":
    print("Training RL agent with Ollama as reward (no explicit memory, but strong +1 updates)...")
    train_with_ollama(num_steps=200)

    print("\nDone training. Running eval...")
    eval_greedy()