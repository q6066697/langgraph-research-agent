"""Test setup: fake credentials so importing agent.py/api.py needs no real keys or network.

These are set before api.py is imported. load_dotenv() does not override variables
that are already present, so a local .env never leaks real keys into the tests.
"""
import os

os.environ["PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
os.environ["TAVILY_API_KEY"] = "test-tavily-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-test"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-test"
os.environ["LANGFUSE_HOST"] = "http://localhost:3000"
os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
