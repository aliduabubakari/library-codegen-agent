from typing import List, Optional
from openai import AzureOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from ..utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class AzureLLMClient:
    """Client for Azure OpenAI API."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
        )
        self.deployment = settings.azure_openai_deployment
        self.model = settings.azure_openai_model
        self.temperature = settings.temperature
    
    async def generate(
        self,
        messages: List[BaseMessage],
        max_completion_tokens: int = 4000,
        stream: bool = False
    ) -> str:
        """Generate completion from Azure OpenAI."""
        # Convert LangChain messages to OpenAI format
        openai_messages = self._convert_messages(messages)
        
        logger.info(f"Generating completion with {len(openai_messages)} messages")
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=openai_messages,
                temperature=self.temperature,
                max_completion_tokens=max_completion_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                content = response.choices[0].message.content
                logger.info(f"Generated {len(content)} characters")
                return content
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def _convert_messages(self, messages: List[BaseMessage]) -> List[dict]:
        """Convert LangChain messages to OpenAI format."""
        openai_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                role = "user"
            
            openai_messages.append({
                "role": role,
                "content": message.content
            })
        
        return openai_messages
    
    def _handle_stream(self, response):
        """Handle streaming response."""
        full_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                logger.debug(f"Stream chunk: {content}")
        
        return full_content
    
    async def generate_with_json(
        self,
        messages: List[BaseMessage],
        max_completion_tokens: int = 4000
    ) -> dict:
        """Generate completion and parse as JSON."""
        import json
        
        # Add JSON instruction to last message
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, HumanMessage):
                last_message.content += "\n\nRespond with valid JSON only."
        
        response = await self.generate(messages, max_completion_tokens)
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in response")
                return {}
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {}