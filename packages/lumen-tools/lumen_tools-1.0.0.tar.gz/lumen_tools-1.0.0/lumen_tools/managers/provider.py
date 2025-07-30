"""
File: /managers/provider.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday July 29th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Any, Dict, List

from lumen_tools.exceptions.exceptions import LumenError

class ProviderManager:
    """
    Manager for provider-specific operations including tool execution.
    
    This manager handles the execution of tool calls from OpenAI chat completions
    and provides a clean interface for running provider actions.
    """
    
    def __init__(self, client):
        """
        Initialize provider manager.
        
        Args:
            client: LumenClient instance for API communication
        """
        self.client = client
    
    async def handle_tool_calls(self, user_id: str, response: Any) -> Dict[str, Any]:
        """
        Handle OpenAI tool calls from a chat completion response.
        Supports multiple concurrent tool calls with comprehensive error handling.
        
        Args:
            user_id: The unique identifier for the user
            response: OpenAI chat completion response object
            
        Returns:
            Dictionary containing execution results for each tool call
            
        Raises:
            ValueError: If user_id is empty or response is invalid
            LumenError: If tool execution fails
        """
        self._validate_user_id(user_id)
        self._validate_response(response)
        
        tool_calls = self._extract_tool_calls(response)
        if not tool_calls:
            return {"message": "No tool calls found in response", "results": {}}
        
        print(f"Processing {len(tool_calls)} tool calls for user {user_id}")
        
        results = await self._execute_tool_calls(tool_calls, user_id)
        
        return self._build_execution_summary(results, len(tool_calls))

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID parameter."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

    def _validate_response(self, response: Any) -> None:
        """Validate OpenAI response object."""
        if not response:
            raise ValueError("Response cannot be empty")

    def _extract_tool_calls(self, response: Any) -> List[Any]:
        """
        Extract tool calls from OpenAI response with robust error handling.
        
        Args:
            response: OpenAI chat completion response
            
        Returns:
            List of tool call objects
            
        Raises:
            ValueError: If response format is invalid
        """
        try:
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    return message.tool_calls
            return []
        except Exception as e:
            raise ValueError(f"Invalid response format: {str(e)}")

    async def _execute_tool_calls(self, tool_calls: List[Any], user_id: str) -> Dict[str, Any]:
        """
        Execute multiple tool calls and collect results.
        
        Args:
            tool_calls: List of tool call objects
            user_id: User ID for execution context
            
        Returns:
            Dictionary mapping tool call IDs to execution results
        """
        results = {}
        
        for i, tool_call in enumerate(tool_calls):
            tool_id = tool_call.id
            function_name = tool_call.function.name
            
            try:
                print(f"Processing tool call {i+1}/{len(tool_calls)}: {function_name}")
                
                arguments = self._parse_tool_arguments(tool_call.function.arguments)
                
                result = await self._execute_single_tool_call(
                    user_id=user_id,
                    function_name=function_name,
                    arguments=arguments,
                )
                
                results[tool_id] = {
                    "tool_call_id": tool_id,
                    "function_name": function_name,
                    "result": result,
                    "status": "success"
                }
                
                print(f"Successfully executed {function_name}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error executing tool call {function_name}: {error_msg}")
                
                results[tool_id] = {
                    "tool_call_id": tool_id,
                    "function_name": function_name,
                    "error": error_msg,
                    "status": "error"
                }
        
        return results

    def _parse_tool_arguments(self, arguments: Any) -> Dict[str, Any]:
        """
        Parse tool call arguments with proper error handling.
        
        Args:
            arguments: Raw arguments from tool call
            
        Returns:
            Parsed arguments dictionary
            
        Raises:
            ValueError: If arguments cannot be parsed
        """
        if isinstance(arguments, str):
            import json
            try:
                return json.loads(arguments)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in tool arguments: {str(e)}")
        
        if isinstance(arguments, dict):
            return arguments
            
        raise ValueError(f"Arguments must be a dictionary or JSON string, got {type(arguments)}")

    async def _execute_single_tool_call(
        self,
        user_id: str,
        function_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a single tool call with comprehensive error handling.
        
        Args:
            user_id: User ID for execution context
            function_name: Name of the function to execute (friendly name)
            arguments: Function arguments
            
        Returns:
            Dictionary containing execution result
            
        Raises:
            ValueError: If function is unknown or arguments are invalid
            LumenError: If execution fails
        """
        action = self.client.tools.FRIENDLY_NAME_TO_ACTION.get(function_name)
        if not action:
            available_functions = list(self.client.tools.FRIENDLY_NAME_TO_ACTION.keys())[:5]
            raise ValueError(
                f"Unknown function name: {function_name}. "
                f"Available functions include: {available_functions}..."
            )
        
        try:
            metadata = self.client.tools.get_action_metadata(action)
        except Exception as e:
            raise ValueError(f"Could not get metadata for action {action}: {str(e)}")
        
        if not isinstance(arguments, dict):
            raise ValueError(f"Arguments must be a dictionary, got {type(arguments)}")
        
        payload = {
            "parameters": arguments,
            "user_id": user_id.strip(),
            "provider": metadata["provider"],
            "service": metadata["service"]
        }
        
        try:
            return await self.client._make_request(
                method="POST",
                endpoint=f"/actions/{function_name}",
                json_data=payload
            )
        except Exception as e:
            raise LumenError(
                f"Failed to execute {function_name} for {metadata['provider']} "
                f"{metadata['service']}: {str(e)}"
            )

    def _build_execution_summary(self, results: Dict[str, Any], total_calls: int) -> Dict[str, Any]:
        """
        Build execution summary from results.
        
        Args:
            results: Dictionary of execution results
            total_calls: Total number of tool calls
            
        Returns:
            Summary dictionary with results and statistics
        """
        successful_calls = sum(1 for r in results.values() if r["status"] == "success")
        failed_calls = total_calls - successful_calls
        
        return {
            "results": results,
            "summary": {
                "total_calls": total_calls,
                "successful": successful_calls,
                "failed": failed_calls
            }
        }