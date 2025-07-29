"""Decorators for command registration."""

from functools import wraps
from typing import Any, Callable, Optional, Type, Union

import click

from ..repl.context import ContextType
from .base import BaseCommand, CommandMetadata, CommandScope, command_registry


def command(
    name: str,
    description: str = "",
    scope: CommandScope = CommandScope.BOTH,
    aliases: Optional[list[str]] = None,
    parent: Optional[str] = None,
) -> Callable:
    """Decorator to register a command class."""
    if not name:
        raise ValueError("Command name cannot be empty")
    
    def decorator(cls: Type[BaseCommand]) -> Type[BaseCommand]:
        # Create metadata
        metadata = CommandMetadata(
            name=name,
            description=description or cls.__doc__ or "",
            scope=scope,
            aliases=aliases or [],
            parent_command=parent,
            command_class=cls,
        )
        
        # Register command
        command_registry.register(metadata)
        
        # Store metadata on class
        cls._command_metadata = metadata
        
        return cls
    
    return decorator


def context_command(
    name: str,
    context_types: list[ContextType],
    description: str = "",
    auto_inject: Optional[dict[str, str]] = None,
    aliases: Optional[list[str]] = None,
) -> Callable:
    """Decorator for context-aware commands."""
    
    def decorator(cls: Type[BaseCommand]) -> Type[BaseCommand]:
        # Create metadata
        metadata = CommandMetadata(
            name=name,
            description=description or cls.__doc__ or "",
            scope=CommandScope.CONTEXT,
            context_types=context_types,
            aliases=aliases or [],
            requires_context=True,
            auto_inject_args=auto_inject or {},
            command_class=cls,
        )
        
        # Register command
        command_registry.register(metadata)
        
        # Store metadata on class
        cls._command_metadata = metadata
        
        return cls
    
    return decorator


def repl_command(
    name: str,
    description: str = "",
    aliases: Optional[list[str]] = None,
) -> Callable:
    """Decorator for REPL-only commands."""
    
    def decorator(func: Callable) -> Callable:
        # For simple REPL commands that are just functions
        metadata = CommandMetadata(
            name=name,
            description=description,
            scope=CommandScope.REPL,
            aliases=aliases or [],
        )
        
        # Register command
        command_registry.register(metadata)
        
        # Store the function for later use
        func._command_metadata = metadata
        
        return func
    
    return decorator


def click_command_adapter(
    name: str,
    click_cmd: click.Command,
    scope: CommandScope = CommandScope.BOTH,
    context_types: Optional[list[ContextType]] = None,
    auto_inject: Optional[dict[str, str]] = None,
) -> None:
    """Adapter to register existing click commands."""
    
    class ClickCommandWrapper(BaseCommand):
        """Wrapper for existing click commands."""
        
        def get_click_command(self) -> click.Command:
            return click_cmd
    
    # Create metadata
    metadata = CommandMetadata(
        name=name,
        description=click_cmd.help or "",
        scope=scope,
        context_types=context_types or [],
        command_class=ClickCommandWrapper,
        click_command=click_cmd,
        auto_inject_args=auto_inject or {},
    )
    
    # Register command
    command_registry.register(metadata)