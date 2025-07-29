
import os
import re
import threading
from datetime import datetime
from dotenv import load_dotenv

from .HAIUtils.HAIUtils import (
    getFrameworkInfo,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    parseInstructions,
    parseModels,
    isStructured,
    safetySettings,
    getFrames
)

load_dotenv()

PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}

def isKeySet(envKey):
    return os.getenv(envKey) is not None


MODEL_PREFIX_MAP = {
    ("gpt", "o1", "o3"): "openai",
    ("claude",): "anthropic",
    ("llama", "meta-llama", "gemma2"): "groq",
    ("gemini", "gemma",): "google",
}

providerMap = {}

if isKeySet("OPENAI_API_KEY"):
    from .HAIConfigs.OpenAIConfig import OpenAIConfig
    providerMap["openai"] = OpenAIConfig()

if isKeySet("ANTHROPIC_API_KEY"):
    from .HAIConfigs.AnthropicConfig import AnthropicConfig
    providerMap["anthropic"] = AnthropicConfig()

if isKeySet("GOOGLE_API_KEY"):
    from .HAIConfigs.GoogleConfig import GoogleConfig
    providerMap["google"] = GoogleConfig()

if isKeySet("GROQ_API_KEY"):
    from .HAIConfigs.GroqConfig import GroqConfig
    providerMap["groq"] = GroqConfig()


class HoloAI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloAI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.providerMap = providerMap

        self.initialized = True

    def getFrameworkInfo(self):
        """
        Returns a string with framework information.
        """
        return getFrameworkInfo()

    def listProviders(self):
        """
        Returns a list of available model providers.
        This is based on the keys of the providerMap dictionary.
        """
        return list(self.providerMap.keys())

    def _inferModelProvider(self, model: str):
        """
        Infers the provider based on the model name.
        Returns the provider name as a string, or None if not found.
        """
        return next(
            (provider for prefixes, provider in MODEL_PREFIX_MAP.items()
             if any(model.startswith(prefix) for prefix in prefixes)),
            None
        )

    def _getProviderConfig(self, model: str):
        """
        Returns the config instance strictly based on model's inferred provider.
        Raises if provider cannot be inferred.
        """
        provider = self._inferModelProvider(model)
        if provider and provider in self.providerMap:
            return self.providerMap[provider]
        raise ValueError(f"Cannot infer provider from model '{model}'. Valid providers: {list(self.providerMap.keys())}")

    # def HoloCompletion(self, **kwargs):
    #     """
    #     Main entry point for HoloAI completion requests.
    #     Get a Response or a Vision response from the configured model.
    #     This method checks if the input contains image paths and routes to Vision if so.
    #     :param kwargs: Keyword arguments to customize the request.
    #         - model: (str) The model to use (Required).
    #         - system/instructions: (str) System prompt or additional instructions (Optional).
    #         - user/input: (str or list) The main user input (Required). 
    #             Accepts a single prompt string or a message history (list of messages). 
    #             Both 'user' and 'input' are interchangeable; use either (Preferred: input).
    #         - skills: (list) Skills to use (Optional).
    #         - tools: (list) Tools to use (Optional).
    #         - tokens: (int) Max tokens to use (Optional (default: 369)).
    #         - verbose: (bool) Return verbose output (Optional (default: False)).
    #     :return: A Response object or a Vision object if image paths are found.
    #     """
    #     kwargs = {k.lower(): v for k, v in kwargs.items()}
    #     model = kwargs.get("model")
    #     raw   = kwargs.get("input") or kwargs.get("user")
    #     system = parseInstructions(kwargs)
    #     verbose = kwargs.get("verbose", False)
    #     if not model or raw is None:
    #         raise ValueError("HoloCompletion needs both a model and input/user")

    #     # ————— 1) Isolate the *last* user message, not the whole history —————
    #     if isinstance(raw, list):
    #         last = raw[-1]
    #         text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
    #     else:
    #         text = str(raw)

    #     # ————— 2) Find any image paths in that single prompt —————
    #     image_paths = self._extractImagePaths(text)
    #     #print(f"[DEBUG] Found image paths: {image_paths}")

    #     if image_paths:
    #         # strip off everything after the last path (so 'What is in this image? ' remains)
    #         img = image_paths[-1]
    #         prompt_only = re.split(re.escape(img), text)[0].strip()
    #         #print(f"[HoloCompletion] Vision → prompt='{prompt_only}', paths={image_paths}")
    #         return self.Vision(
    #             model=model,
    #             system=system, #kwargs.get("instructions") or kwargs.get("system"),
    #             user=prompt_only,
    #             paths=image_paths,
    #             collect=5,
    #             verbose=verbose
    #         )

    #     #("[HoloCompletion] Response")
    #     return self.Response(**kwargs)
    def HoloCompletion(self, **kwargs):
        """
        Main entry point for HoloAI completion requests.
        Checks if the input contains image paths and routes to Vision if so.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional, default: 369).
            - verbose: (bool) Return verbose output (Optional, default: False).
        :return: A Response object, or a Vision object if image paths are found.
        """
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        # Accept either model or models, but always normalize to a dict
        models = kwargs.get("models") or kwargs.get("model")
        raw = kwargs.get("input") or kwargs.get("user")
        system = parseInstructions(kwargs)
        verbose = kwargs.get("verbose", False)
        if models is None or raw is None:
            raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

        # Use your parseModels util
        models = parseModels(models)

        # ————— 1) Isolate the *last* user message, not the whole history —————
        if isinstance(raw, list):
            last = raw[-1]
            text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
        else:
            text = str(raw)

        # ————— 2) Find any image paths in that single prompt —————
        image_paths = self._extractImagePaths(text)

        if image_paths:
            img = image_paths[-1]
            prompt_only = re.split(re.escape(img), text)[0].strip()
            return self.Vision(
                model=models['vision'],
                system=system,
                user=prompt_only,
                paths=image_paths,
                collect=5,
                verbose=verbose
            )

        # If no image, run text/response as usual, using the 'response' model
        kwargs['model'] = models['response']
        return self.Response(**kwargs)


    def Response(self, **kwargs):
        """
        Get a Response from the configured model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills to use (Optional).
            - tools: (list) Tools to use (Optional).
            - tokens: (int) Max tokens to use (Optional (default: 369)).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        #print(f"\n[Response Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getResponse(**kwargs)

    def Vision(self, **kwargs):
        """
        Get a Vision response from the configured model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens: (int) Max tokens to use (Optional (default: 369)).
            - paths: (list) List of image paths (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        #print(f"\n[Vision Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getVision( **kwargs)

    #------------- Utility Methods -------------#
    def isStructured(self, obj):
        """
        Check if the input is a structured list of message dicts.
        A structured list is defined as a list of dictionaries where each dictionary
        contains both "role" and "content" keys.
        Returns True if the input is a structured list, False otherwise.
        """
        return isStructured(obj)

    def formatInput(self, value):
        """
        Formats the input value into a list.
        - If `value` is a string, returns a list containing that string.
        - If `value` is already a list, returns it as is.
        - If `value` is None, returns an empty list.
        """
        return [value] if isinstance(value, str) else value

    def formatConversation(self, convo, user):
        """
        Returns a flat list representing the full conversation:
        - If `convo` is a list, appends the user input (str or list) to it.
        - If `convo` is a string, creates a new list with convo and user input.
        """
        if isinstance(convo, str):
            convo = [convo]
        if isinstance(user, str):
            return convo + [user]
        elif isinstance(user, list):
            return convo + user
        else:
            raise TypeError("User input must be a string or list of strings.")


    def formatJsonInput(self, role: str, content: str) -> dict:
        """
        Format content for JSON-based APIs like OpenAI, Groq, etc.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatJsonInput(role=role, content=content)

    def formatJsonExtended(self, role: str, content: str) -> dict:
        """
        Extended JSON format for APIs like OpenAI, Groq, etc.
        Maps 'assistant', 'developer', 'model' and 'system' to 'assistant'.
        All other roles (including 'user') map to 'user'.
        """
        return formatJsonExtended(role=role, content=content)

    def parseJsonInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized message objects using formatJsonExtended.
        """
        return parseJsonInput(data)

    def formatTypedInput(self, role: str, content: str) -> dict:
        """
        Format content for typed APIs like Google GenAI.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatTypedInput(role=role, content=content)

    def formatTypedExtended(self, role: str, content: str) -> dict:
        """
        Extended typed format for Google GenAI APIs.
        Maps 'assistant', 'developer', 'system' and 'model' to 'model'.
        All other roles (including 'user') map to 'user'.
        """
        return formatTypedExtended(role=role, content=content)

    def parseTypedInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized Google GenAI message objects using formatTypedExtended.
        """
        return parseTypedInput(data)

    def safetySettings(self, **kwargs):
        """
        Construct a list of Google GenAI SafetySetting objects.

        Accepts thresholds as keyword arguments:
            harassment, hateSpeech, sexuallyExplicit, dangerousContent

        Example:
            safetySettings(harassment="block_high", hateSpeech="block_low")
        """
        return safetySettings(**kwargs)

    def _extractImagePaths(self, text: str):
        """
        Extracts image file paths from a given text.
        Supports both Windows and Unix-style paths.
        Returns a list of matched image paths.
        """
        win = r'([A-Za-z]:(?:\\|/).*?\.(?:png|jpe?g|gif|webp))'
        unix= r'(/[^ ]*?/.*?\.(?:png|jpe?g|gif|webp))'
        matches = re.findall(f"{win}|{unix}", text, re.IGNORECASE)
        # flatten tuple pairs
        return [p for pair in matches for p in pair if p]






# # Test prompts

# What is in this image? C:\Users\TechU\OneDrive\Pictures\Screenshot 2024-06-09 022121.png

# Compare these two images. Describe what is in each and highlight differences and similarities, C:\Users\TechU\OneDrive\Pictures\Screenshot 2024-06-09 022121.png, C:\Users\TechU\OneDrive\Pictures\Screenshot 2024-06-19 144830.png

# from HoloAI import HoloAI
# from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env file if it exists

# OPENAI    = "gpt-4.1"               # your OpenAI vision-capable model
# GROG      = "meta-llama/llama-4-scout-17b-16e-instruct"  # groq vision-capable model
# GOOGLE    = "gemini-2.5-flash"      # google vision-capable model
# ANTHROPIC = "claude-sonnet-4-20250514"  # anthropic vision-capable model


# class HoloEngine:
#     def __init__(self):
#         self.client = HoloAI()
#         self.model = GROG
#         self.memories = []

#     def currentTime(self):
#         return datetime.now().strftime("%I:%M %p")

#     def currentDate(self):
#         return datetime.now().strftime("%B %d, %Y")

#     def addMemory(self, user, response, maxTurns=10):
#         self.memories.append(f"user:{user}")
#         self.memories.append(f"assistant:{response}")
#         if len(self.memories) > maxTurns * 2:
#             self.memories = self.memories[-maxTurns*2:]

#     # when you need to setup high-level instructions and want them split from the subset instructions for the AI
#     # - System: High-level description of the AI's role and capabilities
#     # - Instructions: Subset of information that the AI should use to respond to the user
#     def config1(self) -> str:
#         currentUser = "Tristan McBride Sr."
#         system = f"You are a helpful AI assistant named Holo. You are designed to assist with various tasks and provide information based on user queries. Your responses should be clear, concise, and informative. You can also analyze images and provide insights based on their content."
#         instructions =  f"The current user is {currentUser} and the current date and time is {self.currentDate()} {self.currentTime()}."
#         return system, instructions

#     # when you need to setup basic instructions for the AI
#     # - System: Description of the AI's role and capabilities and other information
#     def config2(self) -> str:
#         currentUser = "Tristan McBride Sr."
#         system = f"You are a helpful AI assistant named HoloAI. The current user is {currentUser} and the current date and time is {self.currentDate()} {self.currentTime()}."
#         return system

#     # Complete Capabilities e.g. text, image all in one function great for chat bots, voice assistants, etc.
#     def HoloCompletion(self, user: str) -> str:
#         system, instructions = self.config1()
#         #system = self.config2()
#         msgs = self.client.formatConversation(self.memories, user)
#         #msgs = user # if you want to use the user input directly without conversation history
#         resp = self.client.HoloCompletion(
#             model=self.model,
#             system=system,
#             instructions=instructions, # optional, use if you want to provide additional instructions
#             input=msgs,
#             #verbose=True # uncomment to see the full response structure
#         )
#         if resp:
#             self.addMemory(user, resp)
#         return resp

#     # Just text completion, great for chat bots, voice assistants, etc. but no image capabilities
#     def Response(self, user: str) -> str:
#         system, instructions = self.config1()
#         #system = self.config2()
#         msgs = self.client.formatConversation(self.memories, user)
#         #msgs = user # if you want to use the user input directly without conversation history
#         resp = self.client.Response(
#             model=self.model,
#             system=system,
#             instructions=instructions, # optional, use if you want to provide additional instructions
#             input=msgs,
#             #verbose=True # uncomment to see the full response structure
#         )
#         if resp:
#             self.addMemory(user, resp)
#         return resp

#     # Just image completion, great for image analysis, comparisons, etc.
#     # paths: List of image paths to analyze, e.g. ["C:/path/to/image1.png"] or ["C:/path/to/image1.png", "C:/path/to/image2.png"]
#     # collect arg: Sets the number of frames to collect for video analysis, default is 5 e.g. 
#     # the first frame, then every 5th frame is collected including the last frame
#     def Vision(self, user: str, paths: list, collect=5) -> str:
#         system, instructions = self.config1()
#         #system = self.config2()
#         # msgs = self.client.formatConversation(self.memories, user) # if you want to use conversation history 
#         msgs = user
        
#         resp = self.client.Vision(
#             model=self.model,
#             system=system,
#             instructions=instructions, # optional, use if you want to provide additional instructions
#             input=msgs,
#             paths=paths,
#             collect=collect 
#             #verbose=True # uncomment to see the full response structure
#         )
#         if resp:
#             self.addMemory(user, resp)
#         return resp

#     # def runChatSession(self):
#     #     while True:
#     #         prompt = input("You: ")
#     #         reply = self.HoloCompletion(prompt)
#     #         print(f"\nHoloAI:\n{reply}\n")

# # if __name__ == "__main__":
# #     HoloEngine().runChatSession()



# RUN_OPTION= "HoloCompletion"  # Change to "HoloCompletion", "Response" or "Vision" as needed
# IMAGE_1= r"C:\Users\TechU\OneDrive\Pictures\Screenshot 2024-06-09 022121.png" # Replace with your image path r"C:/path/to/image1.png"
# IMAGE_2= r"C:\Users\TechU\OneDrive\Pictures\Screenshot 2024-06-19 144830.png" # Replace with your image path r"C:/path/to/image2.png"
# IMAGE_PATHS = IMAGE_1 # or [IMAGE_1, IMAGE_2]  # List of image paths for Vision functionality



# if __name__ == "__main__":
#     engine = HoloEngine()
#     if RUN_OPTION == "HoloCompletion":
#         print("Welcome to HoloAI Chat Session!")
#         try:
#             while True:
#                 prompt = input("You: ")
#                 reply = engine.HoloCompletion(prompt)
#                 print(f"\nHoloAI:\n{reply}\n")
#         except KeyboardInterrupt:
#             print("\nSession ended. Goodbye!")
#     elif RUN_OPTION == "Response":
#         print("Welcome to HoloAI Text Response Session!")
#         try:
#             while True:
#                 prompt = input("You: ")
#                 reply = engine.Response(prompt)
#                 print(f"\nHoloAI:\n{reply}\n")
#         except KeyboardInterrupt:
#             print("\nSession ended. Goodbye!")

#     elif RUN_OPTION == "Vision":
#         print("Welcome to HoloAI Vision Session!")
#         try:
#             while True:
#                 prompt = input("You: ")
#                 reply = engine.Vision(prompt, IMAGE_PATHS)
#                 print(f"\nHoloAI:\n{reply}\n")
#         except KeyboardInterrupt:
#             print("\nSession ended. Goodbye!")
