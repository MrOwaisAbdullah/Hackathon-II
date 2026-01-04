import os
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ChatKit imports
from chatkit.server import ChatKitServer, Response, stream_text
from chatkit.store import Store

# Qdrant imports (using rag-pipeline-builder patterns)
from qdrant_client import QdrantClient

# OpenAI Agents SDK imports (using openai-agents-sdk-gemini patterns)
from agents import (
    Agent, 
    Runner, 
    AsyncOpenAI, 
    OpenAIChatCompletionsModel, 
    set_default_openai_client,
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    trace,
    set_tracing_disabled
)
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "document_chunks")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Disable tracing unless you have an OpenAI API Key
set_tracing_disabled(True)

# --- Setup Clients ---

# 1. Qdrant Client (rag-pipeline-builder)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 2. OpenAI Client pointing to Gemini (openai-agents-sdk-gemini)
# Using Google's OpenAI-compatible endpoint
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(external_client)

# Define the Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash-lite", 
    openai_client=external_client,
)

# --- Guardrails (openai-agents-sdk-gemini) ---

class SafetyCheck(BaseModel):
    is_safe: bool = Field(description="Is the content safe?")
    reason: str = Field(description="Reason for decision")

guardrail_agent = Agent(
    name="Guardrail",
    model=model,
    output_type=SafetyCheck,
    instructions="Check if the input is harmful. Return JSON."
)

@input_guardrail
async def safety_guardrail(ctx: RunContextWrapper, agent: Agent, input_data: str) -> GuardrailFunctionOutput:
    print(f"[Guardrail] Checking: {input_data[:50]}...")
    # For speed, you might skip LLM check on every token, but here is the pattern:
    # result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    # if not result.final_output.is_safe:
    #      return GuardrailFunctionOutput(tripwire_triggered=True, output_info="Unsafe content")
    return GuardrailFunctionOutput(tripwire_triggered=False, output_info=None)

# --- RAG Logic (rag-pipeline-builder) ---

async def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant chunks from Qdrant using embeddings.
    Note: Requires an embedding model. For this demo, we assume
    embeddings are handled or we use a simple text search if supported,
    but typically you'd embed the query first.
    """
    try:
        # Mock embedding for demo purposes if no embedding model is configured in env
        # In production: embedder.embed(query)
        # query_vector = ...
        
        # Simulating a search call:
        # results = qdrant_client.search(
        #     collection_name=QDRANT_COLLECTION,
        #     query_vector=query_vector, 
        #     limit=top_k
        # )
        # return "\n".join([h.payload['text'] for h in results])
        
        return "No context retrieved (Configure Embedding Model)"
    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""

# --- ChatKit Server Implementation ---

class CustomChatKitServer(ChatKitServer):
    def __init__(self, store: Store):
        super().__init__(store)

    async def respond(self, message_id: str) -> Response:
        # 1. Get message
        message = await self.store.get_message(message_id)
        user_query = message.get('content', '')
        
        # 2. RAG Retrieval
        context = await retrieve_context(user_query)
        
        # 3. Agent Logic with Context
        agent = Agent(
            name="RAG Assistant",
            instructions=f"""
            You are a helpful assistant using Gemini 2.0.
            
            Context from Knowledge Base:
            {context}
            
            Answer the user's question based on the context if relevant.
            """,
            model=model,
            input_guardrails=[safety_guardrail]
        )

        # 4. Stream Response
        async def stream_generator() -> AsyncGenerator[str, None]:
            async for event in Runner.run_streamed(agent, user_query):
                if event.type == "agent_step_stream":
                    for chunk in event.output:
                        if chunk.content:
                            yield from stream_text(chunk.content)
        
        return StreamingResponse(
            stream_generator(), 
            media_type="application/x-ndjson"
        )

# --- FastAPI App ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.init()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = Store(db_path="chatkit.db")
server = CustomChatKitServer(store)

@app.post("/chatkit/respond")
async def handle_respond(request: Request):
    body = await request.json()
    return await server.respond(body.get("message_id"))

@app.post("/chatkit/sessions")
async def create_session(request: Request):
    session = await store.create_session(user_id="test-user")
    return {"clientToken": "mock-token", "sessionId": session["id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)