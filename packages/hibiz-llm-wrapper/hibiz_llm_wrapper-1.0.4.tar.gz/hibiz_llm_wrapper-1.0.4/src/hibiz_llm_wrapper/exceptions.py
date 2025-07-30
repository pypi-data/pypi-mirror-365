class LLMWrapperError(Exception):
    pass

class DatabaseError(LLMWrapperError):
    pass

class APIError(LLMWrapperError):
    pass

class TokenizationError(LLMWrapperError):
    pass