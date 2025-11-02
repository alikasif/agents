from dspy import MIPROv2
import dspy
from dotenv import load_dotenv


load_dotenv(override=True)
gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified


class ClassifySupportMessage(dspy.Signature):    
    message: str = dspy.InputField()
    category: str = dspy.OutputField()  # Billing, Technical Issue, Shipping, Account
    

class SupportClassifier(dspy.Module):
    def __init__(self):
        self.predict = dspy.Predict(ClassifySupportMessage)
    
    def forward(self, message: str):
        return self.predict(message=message).category

model = SupportClassifier()

print(model("I want to update my credit card details"))

trainset = [
    {"message": "I want to update my credit card details", "category": "Billing"},
    {"message": "App crashes every time I log in", "category": "Technical Issue"},
    {"message": "My order never arrived", "category": "Shipping"},
    {"message": "Please delete my account permanently", "category": "Account"},
]

dspy_dataset = [
        dspy.Example({
            "message": d['message'],
            "category": d['category'],
        }).with_inputs("message")
        for d in trainset
    ]

trainset = dspy_dataset[:int(len(dspy_dataset) * 0.5)]


def validate_answer(example, pred):
    print(f"\n\nexample {example} pred: {pred}\n\n")
    return example.category.lower() == pred.lower()


miprov2 = MIPROv2(metric=validate_answer, num_threads=1)

print(f"\nstarting optimization")
optimized_model = miprov2.compile(student=model, 
                                  trainset=trainset, 
                                  minibatch_size=1, 
                                  requires_permission_to_run=False, 
                                  provide_traceback=False)

print(f"\ncompleted optimization {optimized_model}")

print(optimized_model("I canceled last week but was still charged"))

