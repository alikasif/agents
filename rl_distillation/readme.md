# RL Distillation Agent

A reinforcement learning-based knowledge distillation framework that trains a compact LLM (student) using insights from a larger LLM (teacher).

## 🎯 Overview

This project implements an AI-powered knowledge distillation pipeline where a small, efficient language model learns from a larger, more capable model through a question-answer reinforcement learning loop.

### How It Works

```
┌─────────────────┐         Question         ┌─────────────────┐
│                 │ ─────────────────────────▶│                 │
│   Teacher LLM   │                           │   Student LLM   │
│    (Large)      │                           │    (Tiny)       │
│                 │◀─────────────────────────│                 │
└────────┬────────┘    Compare Answers        └────────┬────────┘
         │                                             │
         │                                             │
         ▼                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RL Distillation Agent                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Generate question                                     │  │
│  │  2. Ask Teacher LLM → Get reference answer                │  │
│  │  3. Ask Student LLM → Get student answer                  │  │
│  │  4. Compare answers:                                      │  │
│  │     ✓ Correct → Reward the Student                        │  │
│  │     ✗ Wrong   → Teach the Student (update weights)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **Reinforcement Learning Loop**: Uses reward signals to guide the student model's learning
- **Automatic Evaluation**: Compares student responses against teacher responses
- **Adaptive Teaching**: Provides corrective training when the student makes mistakes
- **Reward Mechanism**: Positive reinforcement when the student produces correct answers
- **Knowledge Compression**: Distills knowledge from large models into smaller, deployable models

## 🚀 Key Components

| Component | Description |
|-----------|-------------|
| **Teacher LLM** | Large, pre-trained language model that provides reference answers |
| **Student LLM** | Smaller, lightweight model being trained |
| **Question Generator** | Generates diverse questions for the training loop |
| **Answer Comparator** | Evaluates the similarity between teacher and student answers |
| **Reward Function** | Computes reward signals based on answer quality |
| **Training Loop** | Orchestrates the entire distillation process |

## 📋 Prerequisites

- Python 3.9+
- PyTorch 2.0+
- Transformers library
- Access to Teacher LLM (API or local)
- GPU recommended for training

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/rl_distillation.git
cd rl_distillation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Basic Training

```python
from rl_distillation import DistillationAgent

# Initialize the agent
agent = DistillationAgent(
    teacher_model="gpt-4",
    student_model="./models/tiny_llm",
    reward_threshold=0.8
)

# Start distillation training
agent.train(
    num_episodes=1000,
    questions_per_episode=50
)

# Save the trained student model
agent.save_student("./models/distilled_tiny_llm")
```

### Configuration

```yaml
# config.yaml
teacher:
  model_name: "gpt-4"
  api_key: "your-api-key"
  
student:
  model_path: "./models/tiny_llm"
  learning_rate: 1e-5
  
training:
  num_episodes: 1000
  batch_size: 32
  reward_threshold: 0.8
  
evaluation:
  similarity_metric: "semantic"  # or "exact", "bleu"
```

## 🔄 Training Loop

1. **Question Generation**: Generate or sample a question from the dataset
2. **Teacher Response**: Query the large LLM to get the reference answer
3. **Student Response**: Query the student LLM to get its answer
4. **Evaluation**: Compare answers using semantic similarity or exact match
5. **Feedback**:
   - If **correct** (similarity > threshold): Apply positive reward
   - If **wrong** (similarity < threshold): Apply corrective training with teacher's answer

## 📊 Metrics

| Metric | Description |
|--------|-------------|
| **Answer Accuracy** | Percentage of correct student answers |
| **Reward Score** | Cumulative reward over training episodes |
| **Knowledge Transfer Rate** | Speed of learning from teacher |
| **Model Size Reduction** | Ratio of student to teacher parameters |

## 🎯 Use Cases

- **Edge Deployment**: Train small models for mobile/embedded devices
- **Cost Reduction**: Replace expensive API calls with local inference
- **Latency Optimization**: Faster response times with compact models
- **Domain Specialization**: Distill domain-specific knowledge into efficient models

## 🗂️ Project Structure

```
rl_distillation/
├── src/
│   ├── agent.py           # Main distillation agent
│   ├── teacher.py         # Teacher LLM interface
│   ├── student.py         # Student LLM model
│   ├── reward.py          # Reward function implementation
│   ├── evaluator.py       # Answer comparison logic
│   └── trainer.py         # Training loop orchestration
├── models/
│   └── tiny_llm/          # Student model checkpoints
├── data/
│   └── questions/         # Question datasets
├── config/
│   └── config.yaml        # Configuration files
├── tests/
│   └── test_agent.py      # Unit tests
├── requirements.txt
└── readme.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 References

- [Knowledge Distillation](https://arxiv.org/abs/1503.02531) - Hinton et al.
- [Reinforcement Learning from Human Feedback](https://arxiv.org/abs/2203.02155)
- [DistilBERT](https://arxiv.org/abs/1910.01108) - Sanh et al.
