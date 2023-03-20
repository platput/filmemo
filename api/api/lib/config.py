import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def get_env(env_key: str) -> str:
    """
    Gets the os environment variable value
    Args:
        env_key: Environment variable name

    Returns:
        String value of the env key
    """
    return os.environ.get(env_key)
