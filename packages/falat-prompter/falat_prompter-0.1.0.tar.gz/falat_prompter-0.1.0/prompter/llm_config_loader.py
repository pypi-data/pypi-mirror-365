import os
import yaml
import configparser
from typing import Dict, Any


def load_llm_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load LLM config from INI, ENV, or YAML files.
    Priority: INI > ENV > YAML
    """
    # 1. Try INI
    if config_path and config_path.endswith('.ini') and os.path.exists(config_path):
        parser = configparser.ConfigParser()
        parser.read(config_path)
        config = {s: dict(parser.items(s)) for s in parser.sections()}
        # Flatten if there's a [DEFAULT] section
        if parser.defaults():
            config.update(parser.defaults())
        return config

    # 2. Try ENV variables (prefix: LLM_)
    env_config = {}
    for key, value in os.environ.items():
        if key.startswith('LLM_'):
            # e.g. LLM_OPENAI_API_KEY -> openai.api_key
            parts = key[4:].lower().split('_', 1)
            if len(parts) == 2:
                section, subkey = parts
                env_config.setdefault(section, {})[subkey] = value
            else:
                env_config[parts[0]] = value
    if env_config:
        return env_config

    # 3. Try YAML
    if config_path and config_path.endswith(('.yaml', '.yml')) and os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)

    raise FileNotFoundError("No valid LLM config found in INI, ENV, or YAML.")
