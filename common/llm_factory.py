"""
LLM Factory for creating language models from configuration.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain.llms.base import LLM
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI


class LLMFactory:
    """Factory class for creating LLM instances from configuration."""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize the LLM factory.

        Args:
            env_file: Path to the .env file (default: ".env")
        """
        self.env_file = env_file
        self._load_env()

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        # Load from project root directory
        project_root = self._find_project_root()
        env_path = os.path.join(project_root, self.env_file)

        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            print(f"Warning: {env_path} not found. Using system environment variables.")

    def _find_project_root(self) -> str:
        """Find the project root directory by looking for pyproject.toml."""
        current_dir = os.path.dirname(os.path.abspath(__file__))

        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        # If not found, return current working directory
        return os.getcwd()

    def get_model_name(self) -> str:
        """Get the model name from environment variables."""
        return os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    def get_api_key(self) -> Optional[str]:
        """Get the API key from environment variables."""
        return os.getenv("LLM_API_KEY")

    def get_base_url(self) -> Optional[str]:
        """Get the base URL from environment variables."""
        return os.getenv("LLM_BASE_URL")

    def get_model_type(self) -> str:
        """Get the model type from environment variables."""
        return os.getenv("LLM_TYPE", "openai").lower()

    def create_llm(self, **kwargs) -> LLM:
        """
        Create an LLM instance based on configuration.

        Args:
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            LLM instance

        Raises:
            ValueError: If required configuration is missing
        """
        model_type = self.get_model_type()

        if model_type == "openai":
            return self._create_openai_llm(**kwargs)
        elif model_type == "ollama":
            return self._create_ollama_llm(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _create_openai_llm(self, **kwargs) -> ChatOpenAI:
        """Create an OpenAI LLM instance."""
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError("LLM_API_KEY is required for OpenAI models")

        model_name = self.get_model_name()
        base_url = self.get_base_url()

        llm_kwargs = {"model": model_name, "api_key": api_key, **kwargs}

        if base_url:
            llm_kwargs["base_url"] = base_url

        return ChatOpenAI(**llm_kwargs)

    def _create_ollama_llm(self, **kwargs) -> OllamaLLM:
        """Create an Ollama LLM instance."""
        model_name = self.get_model_name()
        base_url = self.get_base_url()

        llm_kwargs = {"model": model_name, **kwargs}

        if base_url:
            llm_kwargs["base_url"] = base_url

        return OllamaLLM(**llm_kwargs)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as a dictionary."""
        return {
            "model_name": self.get_model_name(),
            "api_key": self.get_api_key(),
            "base_url": self.get_base_url(),
            "model_type": self.get_model_type(),
        }


# Convenience function for quick LLM creation
def create_llm(**kwargs) -> LLM:
    """
    Convenience function to create an LLM instance.

    Args:
        **kwargs: Additional arguments to pass to the LLM constructor

    Returns:
        LLM instance
    """
    factory = LLMFactory()
    return factory.create_llm(**kwargs)


# Example usage
if __name__ == "__main__":
    # Create LLM factory
    factory = LLMFactory()

    # Print current configuration
    print("Current configuration:")
    for key, value in factory.get_config().items():
        if key == "api_key" and value:
            print(f"  {key}: {value[:8]}...")
        else:
            print(f"  {key}: {value}")

    # Create LLM instance
    try:
        llm = factory.create_llm()
        print(f"\nCreated LLM: {type(llm).__name__}")
        print(llm.invoke("Hello, who are you?"))
    except ValueError as e:
        print(f"\nError creating LLM: {e}")
