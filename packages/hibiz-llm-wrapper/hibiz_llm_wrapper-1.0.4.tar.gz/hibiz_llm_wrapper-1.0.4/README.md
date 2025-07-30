# Hibiz LLM Wrapper

A comprehensive Python wrapper for Azure OpenAI services, specifically designed for Hibiz Solutions' applications. This library provides seamless integration with Azure OpenAI's Chat Completions and Embeddings APIs while offering robust token usage tracking, database logging, and error handling.

## Features

- **Chat Completions**: Support for text and JSON response types with automatic token calculation
- **Embeddings**: Create embeddings for single or multiple text inputs with comprehensive logging
- **Token Usage Tracking**: Automatic calculation and database logging of input, output, and total tokens
- **Database Integration**: PostgreSQL integration for usage analytics and monitoring
- **Error Handling**: Comprehensive error handling with detailed logging
- **Response Time Tracking**: Automatic measurement and logging of API response times
- **Application Tracking**: Enhanced logging with app_name, module_name, and function_name for detailed usage analytics
- **Parameter Validation**: Automatic validation and sanitization of API parameters

## Installation

```bash
pip install hibiz-llm-wrapper
```

## Quick Start

```python
from hibiz_llm_wrapper import LLMWrapper

# Initialize the wrapper
llm = LLMWrapper(
    service_url="https://your-azure-openai-service.openai.azure.com",
    api_key="your-api-key",
    deployment_name="your-chat-deployment",
    api_version="your-api-version",
    default_model="your-model-name",
    default_embedding_model="your-embedding-model-name"
)

# Send a chat completion request
response = llm.send_request(
    prompt_payload=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="ChatBot",
    module_name="Conversation",
    function_name="handle_greeting"
)

print(response["output_text"])
print(f"Tokens used: {response['total_tokens']}")
```

## API Reference

### LLMWrapper Class

#### Constructor

```python
LLMWrapper(
    service_url: str,
    api_key: str,
    deployment_name: str,
    api_version: str,
    default_model: str = "gpt-4",
    default_embedding_model: str = "text-embedding-ada-002",
    timeout: int = 600
)
```

**Parameters:**
- `service_url`: Azure OpenAI service endpoint URL
- `api_key`: Azure OpenAI API key
- `deployment_name`: Deployment name for chat completions
- `api_version`: API version (e.g., "2024-02-15-preview")
- `default_model`: Default model name for chat completions
- `default_embedding_model`: Default model name for embeddings
- `timeout`: Request timeout in seconds

### Methods

#### send_request()

Send a chat completion request to Azure OpenAI.

```python
send_request(
    prompt_payload: List[Dict[str, Any]],
    customer_id: str,
    organization_id: str,
    app_name: str,
    module_name: str,
    function_name: str,
    model: Optional[str] = None,
    response_type: str = "text",
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `prompt_payload`: List of message dictionaries (OpenAI chat format)
- `customer_id`: Customer identifier for tracking
- `organization_id`: Organization identifier for tracking
- `app_name`: Application name using the service
- `module_name`: Module name within the application
- `function_name`: Specific function name for detailed tracking
- `model`: Model to use (overrides default)
- `response_type`: "text" or "json" for response format
- `**kwargs`: Additional parameters for the API request (see below)

**Supported kwargs Parameters:**

The `send_request` method accepts the following optional parameters through `**kwargs`. All parameters are automatically validated and sanitized:

- `temperature` (float): Controls randomness in the output
  - Range: 0.0 to 2.0
  - Default: 1.0
  - Lower values make output more focused and deterministic

- `top_p` (float): Controls nucleus sampling
  - Range: 0.0 to 1.0
  - Default: 1.0
  - Alternative to temperature for controlling randomness

- `frequency_penalty` (float): Penalizes new tokens based on their frequency
  - Range: -2.0 to 2.0
  - Default: 0.0
  - Positive values reduce repetition

- `presence_penalty` (float): Penalizes new tokens based on their presence
  - Range: -2.0 to 2.0
  - Default: 0.0
  - Positive values encourage talking about new topics

- `max_tokens` (int): Maximum number of tokens in the response
  - Range: 1 to 10,000
  - Default: Model-dependent
  - Controls response length


**Returns:**
```python
{
    "output_text": str,
    "processed_output": Any,
    "response_type": str,
    "input_tokens": int,
    "output_tokens": int,
    "total_tokens": int,
    "response_time_ms": int,
    "model": str,
    "app_name": str,
    "module_name": str,
    "function_name": str,
    "full_response": dict,
    "original_prompt": list
}
```

#### create_embeddings()

Create embeddings for text inputs using Azure OpenAI.

```python
create_embeddings(
    input_texts: Union[str, List[str]],
    customer_id: str,
    organization_id: str,
    app_name: str,
    module_name: str,
    function_name: str,
    model: Optional[str] = None,
    embedding_deployment_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `input_texts`: Single string or list of strings to embed
- `customer_id`: Customer identifier for tracking
- `organization_id`: Organization identifier for tracking
- `app_name`: Application name using the service
- `module_name`: Module name within the application
- `function_name`: Specific function name for detailed tracking
- `model`: Embedding model to use (overrides default)
- `embedding_deployment_name`: Specific deployment name for embeddings
- `**kwargs`: Additional parameters for the embedding API

**Returns:**
```python
{
    "embeddings": Union[List[float], List[List[float]]],
    "input_tokens": int,
    "output_tokens": int,
    "total_tokens": int,
    "response_time_ms": int,
    "model": str,
    "embedding_count": int,
    "input_text_count": int,
    "app_name": str,
    "module_name": str,
    "function_name": str,
    "original_input": Union[str, List[str]]
}
```

#### get_usage_stats()

Retrieve usage statistics from the database.

```python
get_usage_stats(
    customer_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    app_name: Optional[str] = None,
    module_name: Optional[str] = None,
    function_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    request_type: Optional[str] = None
) -> Dict[str, Any]
```

## Usage Examples

### Basic Chat Completion

```python
# Simple text response
response = llm.send_request(
    prompt_payload=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="KnowledgeBot",
    module_name="Geography",
    function_name="get_capital"
)

print(response["output_text"])
```

### Advanced Chat Completion with Parameters

```python
# Chat completion with advanced parameters
response = llm.send_request(
    prompt_payload=[
        {"role": "system", "content": "You are a creative writing assistant."},
        {"role": "user", "content": "Write a short story about a robot."}
    ],
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="CreativeWriting",
    module_name="StoryGeneration",
    function_name="generate_story",
    temperature=0.8,           # More creative responses
    max_tokens=500,           # Limit response length
    top_p=0.9,               # Nucleus sampling
    frequency_penalty=0.2,    # Reduce repetition
    presence_penalty=0.1,     # Encourage new topics
    stop=["\n\n", "THE END"]  # Stop sequences
)

print(response["output_text"])
```

### JSON Response

```python
# Request structured JSON response
response = llm.send_request(
    prompt_payload=[
        {"role": "user", "content": "List 3 programming languages with their use cases in JSON format"}
    ],
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="DevAssistant",
    module_name="Programming",
    function_name="list_languages",
    response_type="json",
    temperature=0.1,  # More deterministic for structured output
    max_tokens=300
)

# Access parsed JSON data
json_data = response["processed_output"]
print(json_data)
```

### Creating Embeddings

```python
# Single text embedding
embedding_response = llm.create_embeddings(
    input_texts="This is a sample text for embedding",
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="SearchEngine",
    module_name="DocumentProcessing",
    function_name="create_document_embedding"
)

print(f"Embedding dimension: {len(embedding_response['embeddings'])}")

# Multiple text embeddings
texts = [
    "First document text",
    "Second document text",
    "Third document text"
]

batch_response = llm.create_embeddings(
    input_texts=texts,
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="SearchEngine",
    module_name="DocumentProcessing",
    function_name="batch_embed_documents"
)

print(f"Created {batch_response['embedding_count']} embeddings")
```

### Using Context Manager

```python
# Automatic resource cleanup
with LLMWrapper(
    service_url="https://your-service.openai.azure.com",
    api_key="your-key",
    deployment_name="your-deployment",
    api_version="your-api-version"
) as llm:
    response = llm.send_request(
        prompt_payload=[{"role": "user", "content": "Hello!"}],
        customer_id="Default Customer",
        organization_id="Default Organization",
        app_name="TestApp",
        module_name="Main",
        function_name="test_function",
        temperature=0.7,
        max_tokens=100
    )
    print(response["output_text"])
```

### Getting Usage Statistics

```python
# Get usage stats for a specific app
stats = llm.get_usage_stats(
    customer_id="Default Customer",
    app_name="ChatBot",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

print(f"Total tokens used: {stats.get('total_tokens', 0)}")

# Get embedding-specific stats
embedding_stats = llm.get_usage_stats(
    organization_id="Default Organization",
    request_type="embedding",
    module_name="DocumentProcessing"
)
```

## Parameter Validation

The library automatically validates all parameters passed through `**kwargs`:

```python
# Valid parameters - will work correctly
response = llm.send_request(
    prompt_payload=[{"role": "user", "content": "Hello!"}],
    customer_id="Default Customer",
    organization_id="Default Organization",
    app_name="TestApp",
    module_name="Main",
    function_name="test_function",
    temperature=1.5,        # Valid: within 0.0-2.0 range
    max_tokens=1000,       # Valid: within 1-10000 range
    top_p=0.8             # Valid: within 0.0-1.0 range
)

# Invalid parameters will be automatically corrected or raise validation errors
try:
    response = llm.send_request(
        prompt_payload=[{"role": "user", "content": "Hello!"}],
        customer_id="Default Customer",
        organization_id="Default Organization",
        app_name="TestApp",
        module_name="Main",
        function_name="test_function",
        temperature=3.0,      # Invalid: exceeds 2.0 maximum
        max_tokens=15000     # Invalid: exceeds 10000 maximum
    )
except ValueError as e:
    print(f"Parameter validation error: {e}")
```

## Enhanced Logging and Tracking

The library automatically logs all requests with detailed information:

- **Request Details**: Model, parameters, response type
- **Token Usage**: Input, output, and total token counts
- **Performance**: Response time in milliseconds
- **Application Context**: App name, module name, function name
- **Parameters Used**: All kwargs parameters and their validated values
- **Status**: Success or failure with error details

This enables comprehensive analytics and monitoring of your Azure OpenAI usage across different applications and modules.

## Error Handling

The library includes comprehensive error handling:

```python
from llm_wrapper.exceptions import APIError, DatabaseError, ValidationError

try:
    response = llm.send_request(
        prompt_payload=[{"role": "user", "content": "Hello!"}],
        customer_id="Default Customer",
        organization_id="Default Organization",
        app_name="TestApp",
        module_name="Main",
        function_name="test_function",
        temperature=0.7,
        max_tokens=500
    )
except APIError as e:
    print(f"API request failed: {e}")
except DatabaseError as e:
    print(f"Database logging failed: {e}")
except ValidationError as e:
    print(f"Parameter validation failed: {e}")
```

## Database Schema

The library automatically creates the necessary database tables for token usage tracking. All usage data is stored with customer, organization, and application context for detailed analytics.

## Requirements

- Python 3.7+
- requests
- PostgreSQL database
- Azure OpenAI service

## Support

This library is developed and maintained exclusively for Hibiz Solutions. For support and questions, please contact the internal development team.

## License

Proprietary - Hibiz Solutions Internal Use Only