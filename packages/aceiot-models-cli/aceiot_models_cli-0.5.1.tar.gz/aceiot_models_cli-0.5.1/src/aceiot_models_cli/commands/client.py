"""Client commands using new architecture."""

from typing import Optional

import click
from aceiot_models import ClientCreate

from ..formatters import format_json, print_error, print_success
from ..repl.context import ContextType
from .base import BaseCommand, ContextAwareCommand
from .decorators import command, context_command
from .utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


@command(
    name="clients.list",
    description="List all clients",
    aliases=["ls-clients"]
)
class ListClientsCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List all clients with pagination support."""
    
    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.pass_context
        def list_clients(ctx: click.Context, page: int, per_page: int) -> None:
            """List all clients."""
            try:
                client = self.require_api_client(ctx)
                result = client.get_clients(page=page, per_page=per_page)
                self.format_output(result, ctx, title="Clients")
            except Exception as e:
                self.handle_api_error(e, ctx, "list clients")
        
        return list_clients


@command(
    name="clients.get", 
    description="Get client details"
)
class GetClientCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for a specific client."""
    
    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.argument("client_name")
        @click.pass_context
        def get_client(ctx: click.Context, client_name: str) -> None:
            """Get a specific client by name."""
            try:
                client = self.require_api_client(ctx)
                result = client.get_client(client_name)
                self.format_output(result, ctx, title=f"Client: {client_name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get client")
        
        return get_client


@context_command(
    name="get",
    context_types=[ContextType.CLIENT],
    description="Get current client details",
    auto_inject={"client_name": "client_name"}
)
class GetCurrentClientCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for the current client in context."""
    
    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.pass_context  
        def get_current_client(ctx: click.Context) -> None:
            """Get current client details."""
            # Name will be auto-injected from context
            name = self.current_client
            if not name:
                print_error("No client context set. Use 'use client <name>' first.")
                ctx.exit(1)
            
            try:
                client = self.require_api_client(ctx)
                result = client.get_client(name)
                self.format_output(result, ctx, title=f"Client: {name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get client")
        
        return get_current_client


@command(
    name="clients.create",
    description="Create a new client"
)
class CreateClientCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Create a new client."""
    
    def get_click_command(self) -> click.Command:
        @click.command("create")
        @click.option("--name", required=True, help="Client name")
        @click.option("--nice-name", help="Nice name for display")
        @click.option("--metadata", help="JSON metadata for the client")
        @click.option("--phone", help="Client phone number")
        @click.option("--address", help="Client address")
        @click.pass_context
        def create_client(
            ctx: click.Context,
            name: str,
            nice_name: Optional[str],
            metadata: Optional[str],
            phone: Optional[str],
            address: Optional[str],
        ) -> None:
            """Create a new client."""
            try:
                import json
                
                client_data = ClientCreate(
                    name=name,
                    nice_name=nice_name or name,
                )
                
                # Handle optional fields
                if phone:
                    client_data.phone = phone
                if address:
                    client_data.address = address
                if metadata:
                    try:
                        client_data.metadata = json.loads(metadata)
                    except json.JSONDecodeError as e:
                        print_error(f"Invalid JSON in metadata: {e}")
                        ctx.exit(1)
                
                api_client = self.require_api_client(ctx)
                result = api_client.create_client(client_data)
                
                if ctx.obj["output"] == "json":
                    click.echo(format_json(result))
                else:
                    print_success(f"✓ Client '{name}' created successfully!")
                    click.echo(f"ID: {result.get('id', 'N/A')}")
                    
            except Exception as e:
                self.handle_api_error(e, ctx, "create client")
        
        return create_client