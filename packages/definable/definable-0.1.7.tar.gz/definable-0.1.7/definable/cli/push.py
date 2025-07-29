import click
import os
import tempfile
from pathlib import Path
from typing import Optional
from ..utils.code_packager import CodePackager
from ..api import APIClient
from ..api.exceptions import APIException
from ..utils.yaml_parser import ConfigParser
from ..utils.config_manager import ConfigManager


@click.command()
@click.option('--endpoint', '-e', 
              help='API endpoint URL (or set DEFINABLE_API_ENDPOINT env var)')
@click.option('--api-key', '-k', 
              help='API key for authentication (or set DEFINABLE_API_KEY env var)')
@click.option('--name', '-n', 
              help='Agent name (defaults to name from agent.yaml)')
@click.option('--config', '-c', 
              default='agent.yaml', 
              help='Agent configuration file (default: agent.yaml)')
@click.option('--check', 
              is_flag=True, 
              help='Check connection and package without uploading')
def push_command(endpoint: Optional[str], api_key: Optional[str], name: Optional[str], 
                config: str, check: bool) -> None:
    """Push agent code to remote endpoint"""
    
    # Load stored configuration
    config_manager = ConfigManager()
    cli_args = {
        'endpoint': endpoint,
        'api_key': api_key,
        'name': name
    }
    merged_config = config_manager.get_merged_config(cli_args)
    
    # Get endpoint from CLI args, stored config, or environment (in that order)
    api_endpoint = (endpoint or 
                   merged_config.get('default_endpoint') or 
                   os.getenv('DEFINABLE_API_ENDPOINT'))
    if not api_endpoint:
        click.echo("Error: API endpoint required. Use --endpoint, 'definable config set default_endpoint <url>', or set DEFINABLE_API_ENDPOINT", err=True)
        raise click.Abort()
    
    # Get API key from CLI args, stored config, or environment (in that order)
    auth_key = (api_key or 
               merged_config.get('api_key') or 
               os.getenv('DEFINABLE_API_KEY'))
    if not auth_key:
        click.echo("Error: API key required. Use --api-key, 'definable config set api_key <key>', or set DEFINABLE_API_KEY", err=True)
        raise click.Abort()
    
    try:
        # Get agent name from CLI args, stored config, or agent.yaml (in that order)
        agent_name = (name or 
                     merged_config.get('default_name'))
        
        if not agent_name:
            try:
                config_data = ConfigParser.load_config(config)
                agent_name = config_data.platform.name
            except Exception:
                click.echo("Warning: Could not load agent name from config. Using 'unnamed-agent'")
                agent_name = 'unnamed-agent'
        
        # Initialize packager and check package
        packager = CodePackager()
        package_info = packager.get_package_info()
        
        if not package_info['valid']:
            click.echo(f"Error: {package_info['error']}", err=True)
            raise click.Abort()
        
        click.echo(f"Package info: {package_info['file_count']} files, {package_info['total_size']} bytes")
        
        # Initialize API client
        client = APIClient(base_url=api_endpoint, api_key=auth_key)
        
        # Check connection if requested
        if check:
            click.echo("Checking connection...")
            conn_result = client.check_connection()
            if conn_result['success']:
                click.echo("✓ Connection successful")
                click.echo("✓ Package validation passed")
                return
            else:
                click.echo(f"✗ Connection failed: {conn_result['error']}", err=True)
                raise click.Abort()
        
        # Create temporary package
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_package_path = temp_file.name
        
        try:
            # Package the code
            click.echo("Packaging code...")
            packager.create_package(temp_package_path)
            
            # Upload the package
            click.echo("Uploading package...")
            try:
                upload_response = client.upload_package(
                    package_path=temp_package_path,
                    agent_name=agent_name
                )
                
                click.echo("✓ Push successful")
                if upload_response.deployment_url:
                    click.echo(f"Deployment URL: {upload_response.deployment_url}")
                if upload_response.version:
                    click.echo(f"Version: {upload_response.version}")
                if upload_response.agent_id:
                    click.echo(f"Agent ID: {upload_response.agent_id}")
                    
            except APIException as e:
                click.echo(f"✗ Push failed: {str(e)}", err=True)
                raise click.Abort()
            except Exception as e:
                click.echo(f"✗ Unexpected error: {str(e)}", err=True)
                raise click.Abort()
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_package_path)
            except:
                pass
    
    except Exception as e:
        if not isinstance(e, click.Abort):
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()


# Export for CLI registration
push = push_command