import os
import threading

from HoloAI.HAIUtils.HAIUtils import (
    DEV_MSG,
    mergeInstructions,
)


class BaseConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.dev = DEV_MSG

        self.initialized = True

    # ---------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------
    def getResponse(self, **kwargs):
        """
        Get a response from the configured model.
        :param kwargs: Keyword arguments to customize the request.
            - model: The model to use (optional).
            - system: System instructions (optional).
            - user: User input (optional).
            - verbose: Whether to return verbose output (default: False).
        :return: A response object.
        """
        model  = kwargs.get('model') # or self.genRModel
        #system = kwargs.get('system') or kwargs.get('instructions')
        system = mergeInstructions(kwargs)
        user   = kwargs.get('user') or kwargs.get('input')
        verbose = kwargs.get('verbose', False)
        return self.Response(model=model, system=system, user=user, verbose=verbose)

    def getVision(self, **kwargs):
        """
        Get a vision response from the configured model.
        :param kwargs: Keyword arguments to customize the request.
            - model: The model to use (optional).
            - system: System instructions (optional).
            - user: User input (optional).
            - paths: List of image paths (default: empty list).
            - collect: Number of frames to collect (default: 5).
            - verbose: Whether to return verbose output (default: False).
        :return: A vision response object.
        """
        model   = kwargs.get('model') # or self.genVModel
        #system = kwargs.get('system') or kwargs.get('instructions')
        system  = mergeInstructions(kwargs)
        user    = kwargs.get('user') or kwargs.get('input')
        paths   = kwargs.get('paths', [])
        collect = kwargs.get('collect', 5)
        verbose = kwargs.get('verbose', False)
        return self.Vision(model=model, system=system, user=user, paths=paths, collect=collect, verbose=verbose)