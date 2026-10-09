"""Runtime configuration loaded from environment variables (or a .env file)."""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass


@dataclass(frozen=True)
class AzureOpenAIConfig:
    endpoint: str
    api_key: str
    api_version: str
    deployment: str

    @classmethod
    def from_env(cls) -> "AzureOpenAIConfig":
        names = {
            "endpoint": "AZURE_OPENAI_ENDPOINT",
            "api_key": "AZURE_OPENAI_API_KEY",
            "api_version": "AZURE_OPENAI_API_VERSION",
            "deployment": "AZURE_OPENAI_DEPLOYMENT",
        }
        missing = [env for env in names.values() if not os.getenv(env)]
        if missing:
            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}. "
                "Copy .env.example to .env and fill in your Azure OpenAI details."
            )
        return cls(**{field: os.environ[env] for field, env in names.items()})
