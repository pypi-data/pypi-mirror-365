import os
import threading
from dotenv import load_dotenv
from groq import Groq

from HoloAI.HAIUtils.HAIUtils import (
    DEV_MSG,
    mergeInstructions,
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GroqConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self._setClient()
        self._setModels()

    def _setClient(self):
        apiKey = os.getenv("GROQ_API_KEY")
        if not apiKey:
            raise KeyError("Groq API key not found. Please set GROQ_API_KEY in your environment variables.")
        self.groqClient = Groq(api_key=apiKey)

    def _setModels(self):
        self.groqRModel = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.3-70b-versatile")
        self.groqVModel = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

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
        user   = kwargs.get('user')  # can be str, list of str, or structured
        tokens = kwargs.get('tokens', None)  # tokens not directly used but kept for consistency
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

        # Debug
        #print(f"Messages: {messages}")

        response = self.groqClient.chat.completions.create(
            model=model,
            messages=messages
        )
        return response if verbose else response.choices[0].message.content

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

        # 1) Build your dev+system block exactly like in Response()
        devMessage = self.dev
        contents = []
        if system:
            # merge devMessage and system instructions
            merged = f"{devMessage}\n{system}"
            sys_out = formatJsonInput("system", merged)
            if isinstance(sys_out, list):
                contents.extend(sys_out)
            else:
                contents.append(sys_out)
        else:
            # no extra system text → just devMessage
            contents.append(formatJsonInput("system", devMessage))

        # 2) Build proper image payload
        images = []
        for path in paths:
            frames = getFrames(path, collect)
            b64, mimeType, idx = frames[0]
            images.append({
            "type": "image_url",
            "image_url": f"data:image/{mimeType};base64,{b64}"
        })

        # 3) Attach only the single prompt (user) + images
        user_content = [{"type": "text", "text": user}] + images
        input_payload = contents.copy()
        input_payload.append({
            "role": "user",
            "content": user_content
        })

        # 4) Call Groq
        response = self.groqClient.chat.completions.create(
            model=model,
            messages=input_payload
        )
        return response if verbose else response.choices[0].message.content
