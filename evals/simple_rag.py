
from semantic_store import SemanticStore
import asyncio
import os
from pydantic import Field

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes import ProcessBuilder
from semantic_kernel.processes.kernel_process import KernelProcessStep, KernelProcessStepContext, KernelProcessStepState
from semantic_kernel.processes.local_runtime.local_kernel_process import KernelProcessEvent, start
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory

class CommonEvents(Enum):
    StartWorkflow = "StartWorkflow"
    DocIndexed = "DocIndexed"
    UserInputReceived = "UserInputReceived"
    DBResponseReceived = "DBResponseReceived"
    LLMResponse = "LLMResponse"


class DocumentStoreState(BaseModel):
    """State for the DocumentStoreStep."""

    document_indexed: bool = False


class DocumentStoreStep(KernelProcessStep[DocumentStoreState]):
    state: DocumentStoreState = Field(default_factory=DocumentStoreState)


    async def activate(self, state: KernelProcessStepState[DocumentStoreState]):
        """Activates the step and sets the state."""

        state.state = state.state or DocumentStoreState()
        self.state = state.state
        self.state.document_indexed = False


    @kernel_function(name="DOC_INDEXED")
    async def store_document(self, context: KernelProcessStepContext,  doc_path: str) -> None:
        
        if not self.state:
            raise ValueError("State has not been initialized")
        
        SemanticStore().store_documents(doc_path)
        await context.emit_event(process_event=CommonEvents.DocIndexed, data=None)


class UserInputState(BaseModel):
    """State for the DocumentStoreStep."""

    user_input: str = Field(default="", description="User query on the document")
    

class UserInputStep(KernelProcessStep[UserInputState]):
    state: UserInputState = Field(default_factory=UserInputState)

    async def activate(self, state: KernelProcessStepState[UserInputState]):
        """Activates the step and sets the state."""

        state.state = state.state or UserInputState()
        self.state = state.state
        self.state.user_input = None

    @kernel_function(name="GET_USER_INPUT")
    async def user_input(self, context: KernelProcessStepContext) -> str:

        if not self.state:
            raise ValueError("State has not been initialized")
        
        input_text = input("Enter your query: ")
        if "exit" in input_text:
            await context.emit_event(process_event=CommonEvents.UserInputReceived, data=None)
            return

        # Emit the user input event
        await context.emit_event(process_event=CommonEvents.UserInputReceived, data=input_text)
        print(f"emitted user input event with data: {input_text}")


class SemanticStoreQueryState(BaseModel):
    """State for the DocumentStoreStep."""

    db_output: str = Field(default="", description="output from vector DB")
    

class SemanticStoreQueryStep(KernelProcessStep[SemanticStoreQueryState]):
    state: SemanticStoreQueryState = Field(default_factory=SemanticStoreQueryState)


    async def activate(self, state: KernelProcessStepState[SemanticStoreQueryState]):
        """Activates the step and sets the state."""

        state.state = state.state or SemanticStoreQueryState()
        self.state = state.state
        self.state.db_output = None

    @kernel_function(name="GET_FROM_DB")
    async def get_from_db(self, context: KernelProcessStepContext, user_input: str, kernel: "Kernel") -> str:
        print(f"Querying DB with: {user_input}")

        if not self.state:
            raise ValueError("State has not been initialized")

        result = SemanticStore().query(user_input)

        # Emit the user input event
        await context.emit_event(process_event=CommonEvents.DBResponseReceived, data={"db_results": result, "user_input": user_input})


class LLMResponseState(BaseModel):
    """State for the DocumentStoreStep."""

    llm_response: str = Field(default="", description="output from llm")
    

class LLMResponseStep(KernelProcessStep[LLMResponseState]):
    state: LLMResponseState = Field(default_factory=LLMResponseState)


    async def activate(self, state: KernelProcessStepState[LLMResponseState]):
        """Activates the step and sets the state."""

        state.state = state.state or LLMResponseState()
        self.state = state.state
        self.state.llm_response = None

    @kernel_function(name="GET_FROM_LLM")
    async def get_from_llm(self, context: KernelProcessStepContext, data: dict, kernel: "Kernel") -> str:
        

        if not self.state:
            raise ValueError("State has not been initialized")

        # Get chat completion service and generate a response
        chat_service: ChatCompletionClientBase = kernel.get_service(service_id="default")
        settings = chat_service.instantiate_prompt_execution_settings(service_id="default")

        chat_history = ChatHistory()
        chat_history.add_system_message("You are a helpful assistant. Use the context to answer the question. Do not make up answers. If you don't know the answer, just say that you don't know. Be concise.")
        chat_history.add_user_message(f"user query: {data["user_input"]}")
        chat_history.add_user_message(f"context: {data["db_results"]}")
        response = await chat_service.get_chat_message_contents(chat_history=chat_history, settings=settings)

        if response is None:
            raise ValueError("Failed to get a response from the chat completion service.")

        answer = response[0].content

        # Emit the user input event
        await context.emit_event(process_event=CommonEvents.LLMResponse, data=answer)


# A process step to publish documentation
class PrintResultStep(KernelProcessStep):
    
    @kernel_function(name="PRINT_RESULT")
    async def print_result(self, docs: str) -> None:
        print(f"{PrintResultStep.__name__}\n\t \nDB Results:\n\n{docs}")


class IntroStep(KernelProcessStep):

    @kernel_function(name="PRINT_INTRO_MESSAGE")
    async def print_intro_message(self, context: KernelProcessStepContext, doc_path: str):
        print("Welcome to Processes in Semantic Kernel.\n")
        await context.emit_event(process_event=CommonEvents.StartWorkflow, data=doc_path)


def build_kernel_process():

    # Create the process builder
    process_builder = ProcessBuilder(name="RAG")

    # Add the steps
    intro_step = process_builder.add_step(IntroStep)
    doc_store_step = process_builder.add_step(DocumentStoreStep)
    user_input_step = process_builder.add_step(UserInputStep)
    db_query_step = process_builder.add_step(SemanticStoreQueryStep)
    llm_response_step = process_builder.add_step(LLMResponseStep)
    result_print_step = process_builder.add_step(PrintResultStep)
    

    process_builder.on_input_event(event_id=CommonEvents.StartWorkflow).send_event_to(target=intro_step, function_name="PRINT_INTRO_MESSAGE")

    intro_step.on_event(event_id=CommonEvents.StartWorkflow).send_event_to(target=doc_store_step, function_name="DOC_INDEXED")
    
    doc_store_step.on_event(event_id=CommonEvents.DocIndexed).send_event_to(target=user_input_step, function_name="GET_USER_INPUT")

    user_input_step.on_event(event_id=CommonEvents.UserInputReceived).send_event_to(target=db_query_step, function_name="GET_FROM_DB", parameter_name="user_input")
        
    db_query_step.on_event(event_id=CommonEvents.DBResponseReceived).send_event_to(target=llm_response_step, function_name="GET_FROM_LLM", parameter_name="data")

    llm_response_step.on_event(event_id=CommonEvents.LLMResponse).send_event_to(target=result_print_step, function_name="PRINT_RESULT")

    result_print_step.on_function_result(function_name="PRINT_RESULT").send_event_to(target=user_input_step, function_name="GET_USER_INPUT")

    # Build the process
    kernel_process = process_builder.build()
    return kernel_process
    

async def run():

     # Configure the kernel with an AI Service and connection details, if necessary
    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(ai_model_id=os.getenv("OPENAI_MODEL"), service_id="default"))
    kernel_process = build_kernel_process()

    # Start the process
    async with await start(
        process=kernel_process,
        kernel=kernel,
        initial_event=KernelProcessEvent(id=CommonEvents.StartWorkflow, data=".\\evals\\data\\Chapter_2_Routing.pdf"),
    ) as process_context:
        _ = await process_context.get_state()


if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(run())