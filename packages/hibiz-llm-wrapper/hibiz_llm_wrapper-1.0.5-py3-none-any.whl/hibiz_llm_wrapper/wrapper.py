import requests
import time
from typing import Dict, Any, Optional, List, Union
from .database import DatabaseManager
from .utils import TokenCalculator, validate_parameters
from .exceptions import APIError, DatabaseError

class LLMWrapper:
    
    def __init__(
        self,
        service_url: str,
        api_key: str,
        db_config: Dict[str, Any],
        deployment_name: str,
        api_version: str,
        default_model: str = "gpt-4",
        default_embedding_model: str = "text-embedding-ada-002",
        timeout: int = 600
    ):
        self.service_url = service_url.rstrip('/')
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.default_model = default_model
        self.default_embedding_model = default_embedding_model
        self.timeout = timeout
        
        default_db_config = db_config
        
        # Initialize components with default config
        self.db_manager = DatabaseManager(default_db_config)
        self.token_calculator = TokenCalculator()
        
        # Create tables automatically on initialization
        try:
            self.db_manager.create_tables()
            print("Database tables created/verified successfully")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
    
    def send_request(
        self,
        prompt_payload: List[Dict[str, Any]],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model: Optional[str] = None,
        response_type: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        start_time = time.time()
        model_name = model or self.default_model
        
        # Validate and prepare parameters
        validated_params = validate_parameters(kwargs)
        
        # Prepare request payload for Azure OpenAI
        request_params = {
            "messages": prompt_payload,
            **validated_params
        }
        
        # Set response format based on response_type
        if response_type.lower() == "json":
            request_params["response_format"] = {"type": "json_object"}
            # Ensure the prompt includes JSON instruction for better results
            if not self._has_json_instruction(prompt_payload):
                # Add JSON instruction to the last user message
                self._add_json_instruction(request_params["messages"])
        
        try:
            # Send request to Azure OpenAI API
            response = self._make_api_request(request_params)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response and calculate tokens
            result = self._process_response(
                response,
                prompt_payload,
                customer_id,
                organization_id,
                app_name,
                module_name,
                function_name,
                model_name,
                request_params,
                response_time_ms,
                response_type
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Log failed request
            self._log_failed_request(
                customer_id,
                organization_id,
                app_name,
                module_name,
                function_name,
                model_name,
                request_params,
                str(e),
                response_time_ms
            )
            
            raise APIError(f"Request failed: {e}")
    
    def create_embeddings(
        self,
        input_texts: Union[str, List[str]],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model: Optional[str] = None,
        embedding_deployment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:

        start_time = time.time()
        model_name = model or self.default_embedding_model
        print(f"Using model: {model_name}")
        deployment_name = embedding_deployment_name or model_name
        
        # Normalize input to list
        if isinstance(input_texts, str):
            input_list = [input_texts]
            single_input = True
        else:
            input_list = input_texts
            single_input = False
        
        # Validate input
        if not input_list or any(not text.strip() for text in input_list):
            raise APIError("Input texts cannot be empty")
        
        # Prepare request payload for Azure OpenAI Embeddings API
        request_params = {
            "input": input_list,
            **kwargs
        }
        
        try:
            # Send request to Azure OpenAI Embeddings API
            response = self._make_embedding_api_request(request_params, deployment_name)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process embedding response
            result = self._process_embedding_response(
                response,
                input_list,
                customer_id,
                organization_id,
                app_name,
                module_name,
                function_name,
                model_name,
                request_params,
                response_time_ms,
                single_input
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Log failed embedding request
            self._log_failed_embedding_request(
                customer_id,
                organization_id,
                app_name,
                module_name,
                function_name,
                model_name,
                request_params,
                str(e),
                response_time_ms
            )
            
            raise APIError(f"Embedding request failed: {e}")
    
    def _make_embedding_api_request(self, params: Dict[str, Any], deployment_name: str) -> Dict[str, Any]:
        """Make API request to Azure OpenAI Embeddings endpoint"""
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Construct Azure OpenAI Embeddings URL
        url = f"{self.service_url}/openai/deployments/{deployment_name}/embeddings"
        
        # Add API version as query parameter
        params_with_version = {
            "api-version": self.api_version
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                params=params_with_version,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get("message", response.text)
                except ValueError:
                    error_detail = response.text
                
                raise APIError(f"Azure OpenAI Embeddings API request failed with status {response.status_code}: {error_detail}")
                
        except requests.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")
    
    def _process_embedding_response(
        self,
        response_data: Dict[str, Any],
        input_texts: List[str],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model_name: str,
        request_params: Dict[str, Any],
        response_time_ms: int,
        single_input: bool = False
    ) -> Dict[str, Any]:

        embeddings = []
        if "data" in response_data:
            for item in response_data["data"]:
                if "embedding" in item:
                    embeddings.append(item["embedding"])
        
        if not embeddings:
            raise APIError("No embeddings found in response")

        total_input_text = " ".join(input_texts)
        input_tokens = self.token_calculator.count_tokens(total_input_text, model_name)
        output_tokens = 0
        total_tokens = input_tokens + output_tokens
        
        enhanced_request_params = {
            **request_params,
            "request_type": "embedding",
            "embedding_count": len(embeddings),
            "input_text_count": len(input_texts),
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name
        }
        
        # Log to database
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                app_name=app_name,
                module_name=module_name,
                function_name=function_name,
                request_params=enhanced_request_params,
                response_params=response_data,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                status="success"
            )
        except DatabaseError as e:
            # Log database error but don't fail the request
            print(f"Warning: Failed to log embedding usage to database: {e}")
        
        # Prepare result
        result = {
            "embeddings": embeddings[0] if single_input else embeddings,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "response_time_ms": response_time_ms,
            "model": model_name,
            "embedding_count": len(embeddings),
            "input_text_count": len(input_texts),
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name,
            "original_input": input_texts[0] if single_input else input_texts
        }
        
        return result
    
    def _log_failed_embedding_request(
        self,
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model_name: str,
        request_params: Dict[str, Any],
        error_message: str,
        response_time_ms: int
    ):
        enhanced_request_params = {
            **request_params,
            "request_type": "embedding",
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name
        }
        
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                app_name=app_name,
                module_name=module_name,
                function_name=function_name,
                request_params=enhanced_request_params,
                response_params={"error": error_message},
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                response_time_ms=response_time_ms,
                status="failed"
            )
        except DatabaseError:
            pass  # Don't fail on logging errors
    
    def _has_json_instruction(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if any message contains JSON instruction"""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str) and "json" in content.lower():
                return True
            elif isinstance(content, list):
                # Handle multimodal content (text + images)
                for item in content:
                    if item.get("type") == "text" and "json" in item.get("text", "").lower():
                        return True
        return False
    
    def _add_json_instruction(self, messages: List[Dict[str, Any]]) -> None:
        """Add JSON instruction to the last user message"""
        for i in reversed(range(len(messages))):
            if messages[i].get("role") == "user":
                content = messages[i].get("content", "")
                json_instruction = "\n\nPlease respond with valid JSON format."
                
                if isinstance(content, str):
                    messages[i]["content"] += json_instruction
                elif isinstance(content, list):
                    text_added = False
                    for item in reversed(content):
                        if item.get("type") == "text":
                            item["text"] += json_instruction
                            text_added = True
                            break
                    
                    if not text_added:
                        # No text item found, add one
                        content.append({
                            "type": "text",
                            "text": json_instruction
                        })
                break
    
    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to Azure OpenAI Chat Completions endpoint"""
        headers = {
            "api-key": self.api_key,  # Azure uses api-key instead of Authorization
            "Content-Type": "application/json"
        }
        
        # Construct Azure OpenAI URL
        url = f"{self.service_url}/openai/deployments/{self.deployment_name}/chat/completions"
        
        # Add API version as query parameter
        params_with_version = {
            "api-version": self.api_version
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                params=params_with_version,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get("message", response.text)
                except ValueError:
                    error_detail = response.text
                
                raise APIError(f"Azure OpenAI API request failed with status {response.status_code}: {error_detail}")
                
        except requests.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")
    
    def _extract_text_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text content from messages for token calculation"""
        text_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if isinstance(content, str):
                text_parts.append(f"{role}: {content}")
            elif isinstance(content, list):
                # Handle multimodal content
                text_content = []
                for item in content:
                    if item.get("type") == "text":
                        text_content.append(item.get("text", ""))
                    elif item.get("type") == "image_url":
                        # For images, we'll add a placeholder for token calculation
                        text_content.append("[IMAGE]")
                
                if text_content:
                    text_parts.append(f"{role}: {' '.join(text_content)}")
        
        return "\n".join(text_parts)
    
    def _process_response(
        self,
        response_data: Dict[str, Any],
        prompt_payload: List[Dict[str, Any]],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model_name: str,
        request_params: Dict[str, Any],
        response_time_ms: int,
        response_type: str = "text"
    ) -> Dict[str, Any]:
        """Process chat completion response and log to database"""

        output_text = ""
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice:
                output_text = choice["message"].get("content", "")
            elif "text" in choice:
                output_text = choice.get("text", "")
        
        # Process response based on type
        processed_output = self._process_output_by_type(output_text, response_type)
        
        # Extract text from messages for token calculation
        input_text = self._extract_text_from_messages(prompt_payload)
        
        input_tokens = self.token_calculator.count_tokens(input_text, model_name)
        output_tokens = self.token_calculator.count_tokens(output_text, model_name)
        total_tokens = input_tokens + output_tokens

        enhanced_request_params = {
            **request_params,
            "request_type": "chat_completion",
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name
        }
        
        # Log to database
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                app_name=app_name,
                module_name=module_name,
                function_name=function_name,
                request_params=enhanced_request_params,
                response_params=response_data,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                status="success"
            )
        except DatabaseError as e:
            # Log database error but don't fail the request
            print(f"Warning: Failed to log to database: {e}")
        
        return {
            "output_text": output_text,
            "processed_output": processed_output,
            "response_type": response_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "response_time_ms": response_time_ms,
            "model": model_name,
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name,
            "full_response": response_data,
            "original_prompt": prompt_payload
        }
    
    def _log_failed_request(
        self,
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model_name: str,
        request_params: Dict[str, Any],
        error_message: str,
        response_time_ms: int
    ):

        enhanced_request_params = {
            **request_params,
            "request_type": "chat_completion",
            "app_name": app_name,
            "module_name": module_name,
            "function_name": function_name
        }
        
        try:
            self.db_manager.log_token_usage(
                customer_id=customer_id,
                organization_id=organization_id,
                model_name=model_name,
                app_name=app_name,
                module_name=module_name,
                function_name=function_name,
                request_params=enhanced_request_params,
                response_params={"error": error_message},
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                response_time_ms=response_time_ms,
                status="failed"
            )
        except DatabaseError:
            pass  # Don't fail on logging errors
    
    def _process_output_by_type(self, output_text: str, response_type: str) -> Any:
        """Process output based on the specified response type"""
        if response_type.lower() == "json":
            try:
                import json
                return json.loads(output_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return the raw text with error info
                return {
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_output": output_text
                }
        else:
            # Default to text
            return output_text
    
    def get_usage_stats(
        self,
        customer_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        app_name: Optional[str] = None,
        module_name: Optional[str] = None,
        function_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> Dict[str, Any]:
        from datetime import datetime
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Create filters dict for enhanced filtering
        filters = {}
        if app_name:
            filters["app_name"] = app_name
        if module_name:
            filters["module_name"] = module_name
        if function_name:
            filters["function_name"] = function_name
        if request_type:
            filters["request_type"] = request_type
        
        return self.db_manager.get_usage_stats(
            customer_id=customer_id,
            organization_id=organization_id,
            start_date=start_dt,
            end_date=end_dt,
            filters=filters
        )
    
    def close(self):
        """Close database connections"""
        self.db_manager.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()