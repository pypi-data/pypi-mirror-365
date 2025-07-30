"""
Universal Tracing Middleware for Agentic Setups
===============================================

This module provides a simple tracing interface using Langfuse.
"""

import os
from functools import wraps
from typing import Optional, Any
import asyncio
from langfuse import Langfuse

# Global agent name - auto-read from environment variable
_AGENT_NAME = os.getenv('AGENT_NAME')

# Global session ID for grouping traces
_CURRENT_SESSION_ID = None

# Global Langfuse client
_client = Langfuse()

def set_agent_name(name: str):
    """Set the agent name that will be used to tag all traces."""
    global _AGENT_NAME
    _AGENT_NAME = name

def set_session_id(session_id: str):
    """
    Set the session ID that will be used to group all subsequent traces.
    This should be called before starting any traces that you want grouped together.
    
    Args:
        session_id: The session identifier to use for grouping traces
    """
    global _CURRENT_SESSION_ID
    _CURRENT_SESSION_ID = session_id

def get_session_id() -> Optional[str]:
    """Get the current session ID."""
    return _CURRENT_SESSION_ID

def clear_session_id():
    """Clear the current session ID."""
    global _CURRENT_SESSION_ID
    _CURRENT_SESSION_ID = None

def trace(name: Optional[str] = None, tags: Optional[List[str]] = None, **kwargs):
    """
    A decorator that provides automatic tracing using Langfuse.
    
    Args:
        name: Optional name for the trace/span. If not provided, uses function name.
        **kwargs: Additional keyword arguments that will be passed to Langfuse's observe decorator
                 after the middleware adds agent name tag and session ID.
    
    Returns:
        Decorated function with tracing enabled.
    """
    from langfuse import observe
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **func_kwargs):
            # Add agent name as tag and session ID if available
            trace_kwargs = kwargs.copy()
            if _AGENT_NAME:
                trace_kwargs['tags'] = [_AGENT_NAME]
            if _CURRENT_SESSION_ID:
                trace_kwargs['session_id'] = _CURRENT_SESSION_ID
            
            return await observe(name=name or func.__name__, **trace_kwargs)(func)(*args, **func_kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **func_kwargs):
            # Add agent name as tag and session ID if available
            trace_kwargs = kwargs.copy()
            if _AGENT_NAME:
                trace_kwargs['tags'] = [_AGENT_NAME]
            if _CURRENT_SESSION_ID:
                trace_kwargs['session_id'] = _CURRENT_SESSION_ID
            
            return observe(name=name or func.__name__, **trace_kwargs)(func)(*args, **func_kwargs)
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def flush():
    """Flush traces to Langfuse."""
    _client.flush() 