import os
import threading
from dotenv import load_dotenv
import anthropic

from HoloAI.HAIUtils.HAIUtils import (
    mergeInstructions,
    isStructured,
    formatJsonInput,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class AnthropicConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("ANTHROPIC_API_KEY")
        if not apiKey:
            raise KeyError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment variables.")
        self.anthClient = anthropic.Anthropic(api_key=apiKey)

    def _setModels(self):
        self.anthRModel = os.getenv("ANTHROPIC_TEXT_MODEL", "claude-sonnet-4-20250514")
        self.anthVModel = os.getenv("ANTHROPIC_VISION_MODEL", "claude-opus-4-20250514")

    # ---------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------
    ## # Public methods are now unified in the BaseConfig class
    # def getResponse(self, **kwargs):
    #     model  = kwargs.get('model') # or self.genRModel
    #     #system = kwargs.get('system') or kwargs.get('instructions')
    #     system = mergeInstructions(kwargs)
    #     user   = kwargs.get('user') or kwargs.get('input')
    #     verbose = kwargs.get('verbose', False)
    #     return self.Response(model=model, system=system, user=user, verbose=verbose)

    # def getVision(self, **kwargs):
    #     model   = kwargs.get('model') # or self.genVModel
    #     #system = kwargs.get('system') or kwargs.get('instructions')
    #     system  = mergeInstructions(kwargs)
    #     user    = kwargs.get('user') or kwargs.get('input')
    #     paths   = kwargs.get('paths', [])
    #     collect = kwargs.get('collect', 5)
    #     verbose = kwargs.get('verbose', False)
    #     return self.Vision(model=model, system=system, user=user, paths=paths, collect=collect, verbose=verbose)

    # ---------------------------------------------------------
    # Response generation
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        model  = kwargs.get('model')
        system = kwargs.get('system')
        user   = kwargs.get('user')
        tokens = kwargs.get('tokens', 1024)
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        devMessage = self.dev
        messages = []

        # --- system / instructions ---
        if not system:
            messages.append(formatJsonInput("system", devMessage))
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                messages.append(formatJsonInput("system", devMessage + "\n" + systemContents))
            else:
                messages.append(formatJsonInput("system", devMessage + "\n" + system))

        # --- user memories / latest ---
        messages.extend(parseJsonInput(user))

        # Anthropic's API expects messages as dicts in the list
        response = self.anthClient.messages.create(
            model=model,
            max_tokens=tokens,
            messages=messages
        )
        return response if verbose else response.content

    # ---------------------------------------------------------
    # Vision support
    # ---------------------------------------------------------
    #def Vision(self, model, system, user, paths, collect=5, verbose=False):
    def Vision(self, **kwargs):
        model   = kwargs.get('model')
        system  = mergeInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        devMessage = self.dev
        contents = []
        if not system:
            contents.append(formatJsonInput("system", devMessage))
        else:
            merged = f"{devMessage}\n{system}"
            sys_out = formatJsonInput("system", merged)
            if isinstance(sys_out, list):
                contents.extend(sys_out)
            else:
                contents.append(sys_out)

        images = []
        for path in paths:
            frames = getFrames(path, collect)
            for b64, mimeType, idx in frames:
                images.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{mimeType}",
                        "data": b64
                    }
                })

        user_content = images.copy()
        if user:
            user_content.append({
                "type": "text",
                "text": user
            })
        contents.append({
            "role": "user",
            "content": user_content
        })

        response = self.anthClient.messages.create(
            model=model,
            max_tokens=1024,
            messages=contents
        )
        return response if verbose else response.content
