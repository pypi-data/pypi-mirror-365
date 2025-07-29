import asyncio
import json
from pathlib import Path

import click

from .docudevs_client import (
    DocuDevsClient,
    TemplateFillRequest,
    UploadCommand,
    UploadDocumentBody,
    UploadFilesBody,
    OcrCommand,
)


def async_command(f):
    """Decorator to run async click commands."""

    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--api-url", default="https://api.docudevs.ai", help="API URL")
@click.option("--token", required=True, help="Authentication token")
@click.pass_context
def cli(ctx, api_url: str, token: str):
    """DocuDevs CLI tool"""
    ctx.ensure_object(dict)
    ctx.obj["client"] = DocuDevsClient(api_url=api_url, token=token)


@cli.command()
@click.argument("files", type=click.Path(exists=True), nargs=-1)
@click.pass_context
@async_command
async def upload_files(ctx, files):
    """Upload multiple files."""
    files_list = [{"file": Path(f).read_bytes(), "filename": Path(f).name} for f in files]
    body = UploadFilesBody(files=files_list)
    result = await ctx.obj["client"].upload_files(body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def upload_document(ctx, file):
    """Upload a single document."""
    body = UploadDocumentBody(file=Path(file).read_bytes(), filename=Path(file).name)
    result = await ctx.obj["client"].upload_document(body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.pass_context
@async_command
async def list_templates(ctx):
    """List all templates."""
    result = await ctx.obj["client"].list_templates()
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("template_id")
@click.pass_context
@async_command
async def metadata(ctx, template_id: str):
    """Get metadata for a template."""
    result = await ctx.obj["client"].metadata(template_id)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("template_id")
@click.pass_context
@async_command
async def delete_template(ctx, template_id: str):
    """Delete template by ID."""
    result = await ctx.obj["client"].delete_template(template_id)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("guid")
@click.argument("command_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def process_document(ctx, guid: str, command_file: str):
    """Process a document with commands from JSON file."""
    with open(command_file) as f:
        command_data = json.load(f)
    body = UploadCommand.from_dict(command_data)
    result = await ctx.obj["client"].process_document(guid, body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("uuid")
@click.pass_context
@async_command
async def result(ctx, uuid: str):
    """Get job result."""
    result = await ctx.obj["client"].result(uuid)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("guid")
@click.pass_context
@async_command
async def status(ctx, guid: str):
    """Get job status."""
    result = await ctx.obj["client"].status(guid)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.argument("request_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def fill(ctx, name: str, request_file: str):
    """Fill a template with data from JSON file."""
    with open(request_file) as f:
        request_data = json.load(f)
    body = TemplateFillRequest.from_dict(request_data)
    result = await ctx.obj["client"].fill(name, body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.pass_context
@async_command
async def list_configurations(ctx):
    """List all named configurations."""
    result = await ctx.obj["client"].list_configurations()
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def get_configuration(ctx, name: str):
    """Get a named configuration."""
    result = await ctx.obj["client"].get_configuration(name)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.argument("command_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def save_configuration(ctx, name: str, command_file: str):
    """Save a named configuration from a JSON file."""
    with open(command_file) as f:
        command_data = json.load(f)
    body = UploadCommand.from_dict(command_data)
    result = await ctx.obj["client"].save_configuration(name, body)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def delete_configuration(ctx, name: str):
    """Delete a named configuration."""
    result = await ctx.obj["client"].delete_configuration(name)
    click.echo(json.dumps(result.body, indent=2))


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO"]), default="DEFAULT", help="OCR type")
@click.option("--format", "ocr_format", type=click.Choice(["plain", "markdown"]), default="plain", help="OCR output format")
@click.pass_context
@async_command
async def ocr(ctx, file: str, ocr: str, ocr_format: str):
    """Upload and process document with OCR-only mode."""
    from io import BytesIO
    import mimetypes
    
    file_path = Path(file)
    mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        document_bytes = BytesIO(f.read())
    
    try:
        guid = await ctx.obj["client"].submit_and_ocr_document(
            document=document_bytes,
            document_mime_type=mime_type,
            ocr=ocr,
            ocr_format=ocr_format
        )
        click.echo(f"Document uploaded and queued for OCR processing. GUID: {guid}")
        click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    cli()
