import os
import threading
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types

from HoloAI.HAIUtils.HAIUtils import (
    DEV_MSG,
    mergeInstructions,
    isStructured,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GoogleConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("GOOGLE_API_KEY")
        if not apiKey:
            raise KeyError("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")
        self.genClient = genai.Client(api_key=apiKey)

    def _setModels(self):
        self.genRModel = os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash")
        self.genVModel = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")

    # -----------------------------------------------------------------
    # Unified public methods
    # -----------------------------------------------------------------
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
        user   = kwargs.get('user')  # str, list[str], or structured
        verbose = kwargs.get('verbose', False)
        if not model:
            raise ValueError("Model cannot be None or empty.")
        if not user:
            raise ValueError("User input cannot be None or empty.")

        devMessage = self.dev
        contents = []

        # --- system / instructions ---
        if not system:
            # Gemini's system instructions go in config, not as Content
            system_instruction = devMessage
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                system_instruction = devMessage + "\n" + systemContents
            else:
                system_instruction = devMessage + "\n" + system

        # --- user / conversation history ---
        # parseTypedInput returns a list of Content or Part objects properly mapped
        typedMessages = parseTypedInput(user)
        contents.extend(typedMessages)

        # Debug
        # print(f"System Instruction: {system_instruction}")
        # print(f"Contents: {contents}")

        # Build config
        config_args = dict(response_mime_type="text/plain")
        if system_instruction:
            config_args["system_instruction"] = [system_instruction]
        generate_content_config = types.GenerateContentConfig(**config_args)

        # Call Gemini
        response = self.genClient.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response if verbose else response.text

    # -----------------------------------------------------------------
    # Vision support
    # -----------------------------------------------------------------
    #def Vision(self, model, system, user, paths, collect=5, verbose=False):
    def Vision(self, **kwargs):
        model   = kwargs.get('model')
        system  = mergeInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)
        """
        system: Optional system instructions (str or None)
        user: the prompt (str)
        paths: str or list of str (media file paths)
        collect: sample every Nth frame (for videos/animations)
        """
        if isinstance(paths, str):
            paths = [paths]
        if not paths or not isinstance(paths, list):
            raise ValueError("paths must be a string or a list with at least one item.")

        # 1) Encode your images
        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=f"image/{mimeType}",
                        data=base64.b64decode(b64)
                    )
                )
            )

        # 2) Build the chat contents: images first, then the text prompt
        text_part = types.Part(text=user)
        contents = [ types.Content(role="user", parts=images + [text_part]) ]

        # --- system / instructions ---
        devMessage = self.dev
        if not system:
            # Gemini's system instructions go in config, not as Content
            system_instruction = devMessage
        else:
            if isStructured(system):
                systemContents = "\n".join(item['content'] for item in system)
                system_instruction = devMessage + "\n" + systemContents
            else:
                system_instruction = devMessage + "\n" + system

        # 4) Bake into the GenerateContentConfig
        config_args = {
            "response_mime_type": "text/plain",
            "system_instruction": [system_instruction]
        }
        generate_content_config = types.GenerateContentConfig(**config_args)

        # 5) Call Gemini
        response = self.genClient.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response if verbose else response.text
