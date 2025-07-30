"""
Command line interface for bc2appsource
"""

import os
import sys
import click
from typing import Optional

from .publisher import AppSourcePublisher


@click.group()
@click.version_option()
def cli():
    """BC2AppSource - Publish Business Central apps to Microsoft AppSource"""
    pass


@cli.command()
@click.option(
    "--app-file",
    required=True,
    help="Path to the .app file to publish (supports wildcards)"
)
@click.option(
    "--library-app-file",
    help="Optional path to library .app file"
)
@click.option(
    "--product-name",
    help="AppSource product name"
)
@click.option(
    "--product-id",
    help="Direct AppSource product ID"
)
@click.option(
    "--tenant-id",
    help="APPSOURCE tenant ID (or set APPSOURCE_TENANT_ID env var)"
)
@click.option(
    "--client-id",
    help="APPSOURCE client ID (or set APPSOURCE_CLIENT_ID env var)"
)
@click.option(
    "--client-secret",
    help="APPSOURCE client secret (or set APPSOURCE_CLIENT_SECRET env var)"
)
@click.option(
    "--auto-promote/--no-auto-promote",
    default=True,
    help="Auto-promote submission after upload"
)
@click.option(
    "--wait/--no-wait",
    default=False,
    help="Wait for submission completion"
)
def publish(
    app_file: str,
    library_app_file: Optional[str],
    product_name: Optional[str],
    product_id: Optional[str],
    tenant_id: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
    auto_promote: bool,
    wait: bool
):
    """Publish a Business Central app to Microsoft AppSource"""
    
    # Get credentials from environment if not provided
    tenant_id = tenant_id or os.getenv("APPSOURCE_TENANT_ID")
    client_id = client_id or os.getenv("APPSOURCE_CLIENT_ID")
    client_secret = client_secret or os.getenv("APPSOURCE_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        click.echo("Error: APPSOURCE credentials are required. Provide them via options or environment variables:", err=True)
        click.echo("  --tenant-id or APPSOURCE_TENANT_ID", err=True)
        click.echo("  --client-id or APPSOURCE_CLIENT_ID", err=True)
        click.echo("  --client-secret or APPSOURCE_CLIENT_SECRET", err=True)
        sys.exit(1)
    
    if not product_name and not product_id:
        click.echo("Error: Either --product-name or --product-id must be specified", err=True)
        sys.exit(1)
    
    try:
        publisher = AppSourcePublisher(tenant_id, client_id, client_secret)
        
        click.echo(f"Publishing app: {app_file}")
        if library_app_file:
            click.echo(f"Library app: {library_app_file}")
        
        result = publisher.publish(
            app_file=app_file,
            product_name=product_name,
            product_id=product_id,
            library_app_file=library_app_file,
            auto_promote=auto_promote,
            do_not_wait=not wait
        )
        
        if result.success:
            click.echo(f"✅ Successfully submitted to AppSource!")
            if result.submission_id:
                click.echo(f"Submission ID: {result.submission_id}")
        else:
            click.echo(f"❌ Submission failed: {result.error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--tenant-id",
    help="APPSOURCE tenant ID (or set APPSOURCE_TENANT_ID env var)"
)
@click.option(
    "--client-id",
    help="APPSOURCE client ID (or set APPSOURCE_CLIENT_ID env var)"
)
@click.option(
    "--client-secret",
    help="APPSOURCE client secret (or set APPSOURCE_CLIENT_SECRET env var)"
)
def list_products(
    tenant_id: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str]
):
    """List all AppSource products for the authenticated account"""
    
    # Get credentials from environment if not provided
    tenant_id = tenant_id or os.getenv("APPSOURCE_TENANT_ID")
    client_id = client_id or os.getenv("APPSOURCE_CLIENT_ID")
    client_secret = client_secret or os.getenv("APPSOURCE_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        click.echo("Error: APPSOURCE credentials are required", err=True)
        sys.exit(1)
    
    try:
        publisher = AppSourcePublisher(tenant_id, client_id, client_secret)
        products = publisher.get_products(silent=False)
        
        if products:
            click.echo("AppSource Products:")
            click.echo("-" * 50)
            for product in products:
                click.echo(f"Name: {product.get('name', 'N/A')}")
                click.echo(f"ID: {product.get('id', 'N/A')}")
                click.echo(f"Type: {product.get('productType', 'N/A')}")
                click.echo("-" * 50)
        else:
            click.echo("No products found or unable to retrieve products")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
