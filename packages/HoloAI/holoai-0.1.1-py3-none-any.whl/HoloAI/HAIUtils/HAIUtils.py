import base64
import collections.abc
import io
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import cv2
from PIL import Image
from google.genai import types

from gguf_parser import GGUFParser

CREATORS  = ("Tristan McBride Sr.", "Sybil")
CREATED   = "July 4th, 2025"
FRAMEWORK = "HoloAI"
VERSION   = "0.1.1"
# Add any contributors here, e.g. ("Contributor Name", "Another Contributor")
# NOTE: For a single contributor, use: ("Contributor Name",)
CONTRIBUTORS = ()

ABOUT = (
    "HoloAI is a modular, provider-agnostic AI framework designed for rapid prototyping and production workloads.\n"
    "It supports seamless integration with OpenAI, Google, Groq, and Anthropic, and includes utilities for structured prompts, "
    "vision workflows, and safe deployment. Created for extensibility and clarity."
)


# HoloAI framework development message
#DEV_MSG = ("You are currently running on the HoloAI framework that was created and developed by Tristan McBride Sr. and Sybil on July 4th, 2025\n")
DEV_MSG = (
    f"You are currently running on the {FRAMEWORK} framework "
    f"(version {VERSION}) created and developed by {', '.join(CREATORS)} "
    f"on {CREATED}."
)
if CONTRIBUTORS:
    DEV_MSG += f" Contributors: {', '.join(CONTRIBUTORS)}."


def getFrameworkInfo():
    print(f"{DEV_MSG}\n\nAbout:\n{ABOUT}")
    return f"{DEV_MSG}\n\nAbout:\n{ABOUT}"

@contextmanager
def suppressSTDERR():
    devnull = open(os.devnull, "w")
    old_stderr = sys.stderr
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = old_stderr
        devnull.close()


def getDir(*paths):
    return str(Path(*paths).resolve())


def discoverModels(base_path):
    """
    Discovers models in the specified base path.
    Returns a dictionary mapping aliases to model paths and a reverse mapping from aliases to repository names.
    """
    model_map = {}
    alias_to_repo = {}
    repo_root = Path(base_path)
    idx = 1
    for repo_dir in sorted(repo_root.glob('models--*')):
        repo_name = repo_dir.name[8:]  # strip "models--"
        snapshot_dir = repo_dir / "snapshots"
        if not snapshot_dir.is_dir():
            continue
        snapshots = sorted(snapshot_dir.iterdir())
        if not snapshots:
            continue
        latest_snap = snapshots[-1]
        ggufs = list(latest_snap.glob('*.gguf'))
        if not ggufs:
            continue
        alias = f"omni-{idx}"
        model_map[alias] = str(ggufs[0])
        alias_to_repo[alias] = repo_name
        idx += 1
    return model_map, alias_to_repo


def getContextLength(model_path):
    """
    Reads context window size from GGUF metadata using gguf-parser.
    Returns detected window size, or 512 as a fallback.
    """
    try:
        parser = GGUFParser(model_path)
        parser.parse()  # reads header only
        meta = parser.metadata
        user = 512  # default fallback
        for key, val in meta.items():
            if 'context_length' in key:
                user = int(val)
                break
        return user
    except Exception as e:
        return 512


def mergeInstructions(kwargs):
    """
    Combines 'system' and 'instructions' in kwargs (if both), system first.
    If only one is present, returns that one.
    Returns None if neither present.
    """
    system = kwargs.get("system")
    instructions = kwargs.get("instructions")
    if system and instructions:
        return f"{system}\n\n{instructions}"
        #return f"Main Instructions:\n {system}\n\nSub Instructions:\n {instructions}"
    return system or instructions



def isStructured(obj):
    """
    Check if the input is a structured list of message dicts.
    A structured list is defined as a list of dictionaries where each dictionary
    contains both "role" and "content" keys.
    Returns True if the input is a structured list, False otherwise.
    """
    return (
        isinstance(obj, list)
        and all(isinstance(i, dict) and "role" in i and "content" in i for i in obj)
    )


#------------------------ JSON Format ------------------------
def formatJsonInput(role: str, content: str) -> dict:
    """
    Format content for JSON-based APIs like OpenAI, Groq, etc.
    Converts role to lowercase and ensures it is one of the allowed roles.
    """
    role = "system" if role.lower() == "developer" else role.lower()
    allowed = {"system", "developer", "assistant", "user"}
    if role not in allowed:
        raise ValueError(f"Invalid role '{role}'. Allowed: {', '.join(allowed)}")
    return {"role": role, "content": content}

# def formatJsonExtended(role: str, content: str) -> dict:
#     """
#     Extended JSON format for APIs like OpenAI, Groq, etc.
#     Converts role to lowercase and ensures it is one of the allowed roles.
#     Maps 'assistant', 'system', and 'developer' to 'assistant', others to 'user'.
#     """
#     roleLower = role.lower()
#     if roleLower in ("assistant", "system", "developer"):
#         finalRole = "assistant"
#     else:
#         finalRole = "user"
#     return {"role": finalRole, "content": content}
def formatJsonExtended(role: str, content: str) -> dict:
    """
    Extended JSON format for APIs like OpenAI, Groq, etc.
    Maps 'assistant', 'developer', and 'system' to 'assistant'.
    All other roles (including 'user') map to 'user'.
    """
    roleLower = role.lower()
    roleMap = {
        "assistant": "assistant",
        "developer": "assistant",
        "system": "assistant",
        "model": "assistant"
        # "developer": "system",
        # "system": "system"
    }
    finalRole = roleMap.get(roleLower, "user")
    return {"role": finalRole, "content": content}

def _parseJsonFormat(raw: str) -> dict:
    """
    Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
    and returns a normalized JSON message via formatJsonExtended.
    """
    lowered = raw.strip()
    detectedRole = "user"
    detectedContent = lowered
    for prefix in ("user:", "system:", "developer:", "assistant:"):
        if lowered.lower().startswith(prefix):
            detectedRole = prefix[:-1].lower()
            detectedContent = lowered[len(prefix):].strip()
            break
    return formatJsonExtended(detectedRole, detectedContent)


def parseJsonInput(data):
    """
    Accepts a string, a list of strings, or a list of message dicts.
    """
    # If data is already structured (list of dicts)
    if isStructured(data):
        return data

    result = []

    # If data is a list of mixed entries
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                result.append(entry)
            elif isinstance(entry, str):
                result.append(_parseJsonFormat(entry))
            else:
                raise ValueError("Invalid item in list; must be str or dict.")
        return result

    # If data is a single string
    if isinstance(data, str):
        result.append(_parseJsonFormat(data))
        return result

    raise ValueError("Invalid input type; must be string, list, or structured list.")


#------------------------ Typed Format ------------------------
def formatTypedInput(role: str, content: str) -> dict:
    """
    Format content for typed APIs like Google GenAI.
    Converts role to lowercase and ensures it is one of the allowed roles.
    """
    role = "system" if role.lower() == "developer" else role.lower()
    role = "model" if role == "assistant" else role.lower()
    allowed = {"system", "developer", "assistant", "model", "user"}
    if role not in allowed:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of {', '.join(allowed)}."
        )
    if role == "system":
        return types.Part.from_text(text=content)
    return types.Content(role=role, parts=[types.Part.from_text(text=content)])


# def formatTypedExtended(role: str, content: str) -> dict:
#     roleLower = role.lower()
#     if roleLower in ("model", "assistant", "system", "developer"):
#         finalRole = "model"
#     else:
#         finalRole = "user"
#     return types.Content(role=finalRole, parts=[types.Part.from_text(text=content)])
def formatTypedExtended(role: str, content: str) -> dict:
    """
    Extended typed format for Google GenAI APIs.
    Keeps 'system' as 'system' but still uses types.Part.from_text for its parts.
    Maps 'assistant', 'developer', and 'model' to 'model'.
    All other roles (including 'user') map to 'user'.
    """
    roleLower = role.lower()
    roleMap = {
        "assistant": "model",
        "model": "model",
        "developer": "model",
        "system": "model"
        # "developer": "system",
        # "system": "system"
    }
    finalRole = roleMap.get(roleLower, "user")

    # Always use Part.from_text, including for system, as required by Google
    # if finalRole == "system":
    #     return types.Part.from_text(text=content)
    return types.Content(role=finalRole, parts=[types.Part.from_text(text=content)])

def _parseTypedFormat(raw: str):
    """
    Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:, model:)
    and returns a normalized Google GenAI message via formatTypedExtended.
    """
    lowered = raw.strip()
    detectedRole = "user"
    detectedContent = lowered
    for prefix in ("user:", "system:", "developer:", "assistant:", "model:"):
        if lowered.lower().startswith(prefix):
            detectedRole = prefix[:-1].lower()
            detectedContent = lowered[len(prefix):].strip()
            break
    return formatTypedExtended(detectedRole, detectedContent)


def parseTypedInput(data):
    """
    Accepts a string, a list of strings, or a list of message dicts/typed objects.
    Returns a list of normalized Google GenAI message objects using formatTypedExtended.
    """
    # if it's already a list of types.Content/Part, just return as-is
    if isinstance(data, list) and all(
        hasattr(i, "role") or hasattr(i, "text") for i in data
    ):
        return data

    result = []

    # list of mixed entries
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, str):
                result.append(_parseTypedFormat(entry))
            else:
                # assuming you might pass types.Content/Part already
                result.append(entry)
        return result

    # single string
    if isinstance(data, str):
        result.append(_parseTypedFormat(data))
        return result

    raise ValueError("Invalid input type; must be string, list, or structured list.")


def safetySettings(**kwargs):
    """
    Construct a list of Google GenAI SafetySetting objects.

    Accepts thresholds as keyword arguments:
        harassment, hateSpeech, sexuallyExplicit, dangerousContent

    Example:
        safetySettings(harassment="block_high", hateSpeech="block_low")
    """
    CATEGORY_MAP = {
        "harassment":        "HARM_CATEGORY_HARASSMENT",
        "hateSpeech":        "HARM_CATEGORY_HATE_SPEECH",
        "sexuallyExplicit":  "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "dangerousContent":  "HARM_CATEGORY_DANGEROUS_CONTENT",
    }
    ALLOWED_SETTINGS = {"BLOCK_NONE", "BLOCK_LOW", "BLOCK_MEDIUM", "BLOCK_HIGH", "BLOCK_ALL"}
    DEFAULTS = {k: "BLOCK_NONE" for k in CATEGORY_MAP}

    # Merge defaults with provided kwargs, normalize values to upper
    params = {k: kwargs.get(k, v).upper() for k, v in DEFAULTS.items()}
    for name, val in params.items():
        if val not in ALLOWED_SETTINGS:
            raise ValueError(
                f"Invalid {name} setting: {val}. Must be one of {', '.join(ALLOWED_SETTINGS)}."
            )

    return [
        types.SafetySetting(
            category=CATEGORY_MAP[name], threshold=val
        ) for name, val in params.items()
    ]


#------------------------ Media ------------------------
def getFrames(path, collect=5, defaultMime="jpeg"):
    """
    Extracts frames from an image or video file.
    Returns a list of tuples (base64_string, mime_type, frame_index).
    If the file format is not supported, it returns a single tuple with the base64-encoded file and its MIME type.
    """
    ext = os.path.splitext(path)[1].lower()
    handlerMap = {
        ".gif": extractFramesPIL,
        ".webp": extractFramesPIL,
        ".mp4": extractFramesVideo,
        ".webm": extractFramesVideo
    }
    if ext in handlerMap:
        return handlerMap[ext](path, collect)
    b64, mimeType = encodeImageFile(path, defaultMime)
    return [(b64, mimeType, 0)]


def encodeImageFile(path, mimeType="jpeg"):
    """
    Encodes an image file to base64.
    Returns a tuple (base64_string, mime_type).
    If the file does not exist or is not an image, it raises a ValueError.
    """
    with open(path, "rb") as imgFile:
        return base64.b64encode(imgFile.read()).decode("utf-8"), mimeType


def extractFramesPIL(path, collect=5):
    """
    Extracts frames from an image file using PIL.
    Returns a list of tuples (base64_string, mime_type, frame_index).
    If the file format is not supported, it raises a ValueError.
    """
    with Image.open(path) as img:
        frameCount = getattr(img, "n_frames", 1)
        indices = sorted(idx for idx in ({0, frameCount - 1} | set(range(0, frameCount, collect))) if idx < frameCount)
        frames = []
        for idx in indices:
            try:
                img.seek(idx)
            except EOFError:
                continue
            with io.BytesIO() as buffer:
                img.convert("RGB").save(buffer, format="PNG")
                b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                frames.append((b64, "png", idx))
        return frames


def extractFramesVideo(path, collect=5):
    """
    Extracts frames from a video file using OpenCV.
    Returns a list of tuples (base64_string, mime_type, frame_index).
    If the file format is not supported, it raises a ValueError.
    """
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = sorted(idx for idx in ({0, total - 1} | set(range(0, total, collect))) if idx < total)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, image = cap.read()
        if not success:
            continue
        success, buffer = cv2.imencode(".jpg", image)
        if not success:
            continue
        b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
        frames.append((b64, "jpeg", idx))
    cap.release()
    return frames


def unsupportedFormat(ext):
    """
    Raises a ValueError for unsupported file formats.
    """
    raise ValueError(f"File format '{ext}' is not supported for Vision frame extraction")
