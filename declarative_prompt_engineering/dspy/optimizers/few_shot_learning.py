import dspy
from dotenv import load_dotenv
from dspy.teleprompt import BootstrapFewShot
from typing import Literal


load_dotenv(override=True)
gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified


class TextSentimentAnalyzer(dspy.Signature):
    """Analyze and classify the sentiment of a given text into positive, negative, or neutral categories."""

    input_text: str = dspy.InputField(description="The text to analyze for sentiment")
    sentiment_class: Literal["positive", "negative", "neutral"] = dspy.OutputField(description="The classified sentiment")


# Create a sentiment analyzer module
sentiment_analyzer = dspy.Predict(TextSentimentAnalyzer)

# Test the analyzer
initial_test = sentiment_analyzer(input_text="This product exceeded my expectations!")
print(f"\nAnalyzed Sentiment: {initial_test.sentiment_class}")


# Training dataset with detailed product reviews
training_dataset = [
    dspy.Example(input_text="The features of this software are incredibly intuitive and well-designed!", sentiment_class="positive").with_inputs("input_text"),
    dspy.Example(input_text="The system crashes frequently and customer support is unresponsive.", sentiment_class="negative").with_inputs("input_text"),
    dspy.Example(input_text="The product works as advertised, meets basic requirements.", sentiment_class="neutral").with_inputs("input_text"),
    dspy.Example(input_text="Outstanding performance and exceeded all our business needs!", sentiment_class="positive").with_inputs("input_text"),
    dspy.Example(input_text="Poor documentation and difficult integration process.", sentiment_class="negative").with_inputs("input_text"),
    dspy.Example(input_text="Basic functionality works, but nothing extraordinary.", sentiment_class="neutral").with_inputs("input_text"),
]


# Validation dataset for testing
validation_dataset = [
    dspy.Example(input_text="Revolutionary product that transformed our workflow!", sentiment_class="positive").with_inputs("input_text"),
    dspy.Example(input_text="Significant performance issues and reliability concerns.", sentiment_class="negative").with_inputs("input_text"),
]


# Define validation metric
def evaluate_sentiment_accuracy(example, prediction, trace=None):
    """Evaluate if the predicted sentiment matches the expected sentiment."""
    return example.sentiment_class == prediction.sentiment_class


# Create enhanced module with Chain of Thought reasoning
class EnhancedSentimentAnalyzer(dspy.Module):
    """Advanced sentiment analyzer with chain-of-thought reasoning capabilities."""
    
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(TextSentimentAnalyzer)

    def forward(self, input_text):
        """Process input text and return sentiment analysis with reasoning."""
        return self.analyze(input_text=input_text)


# Initialize the BootstrapFewShot optimizer
sentiment_optimizer = BootstrapFewShot(
    metric=evaluate_sentiment_accuracy,
    max_bootstrapped_demos=3,
    max_labeled_demos=3
)

# Create base analyzer instance
base_analyzer = EnhancedSentimentAnalyzer()

# Compile the optimized analyzer
optimized_analyzer = sentiment_optimizer.compile(
    student=base_analyzer,
    trainset=training_dataset    
)

# Test both analyzers with a complex example
test_sample = "The new features have revolutionized our workflow, though there are minor bugs to fix."

# Test base analyzer
base_result = base_analyzer(test_sample)
print(f"\nInput Text: {test_sample}")
print(f"\nBase Analysis Result: {base_result.sentiment_class}")
print(f"\nReasoning Process: {base_result.reasoning}")

# Test optimized analyzer
optimized_result = optimized_analyzer(input_text=test_sample)
print(f"\nOptimized Analysis Result: {optimized_result.sentiment_class}")
print(f"\nEnhanced Reasoning: {optimized_result.reasoning}")