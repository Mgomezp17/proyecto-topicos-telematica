#!/usr/bin/env python3
import asyncio
import os

import click
from api_client_external import GridDFSClientExternal
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from utils.file_utils import FileUtils

console = Console()


@click.group()
@click.option("--namenode", default="http://localhost:8000", help="URL del NameNode")
@click.pass_context
def cli(ctx, namenode):
    """GridDFS - Sistema de archivos distribuido por bloques"""
    ctx.ensure_object(dict)
    ctx.obj["client"] = GridDFSClientExternal(namenode)


@cli.command()
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.pass_context
def register(ctx, username, email, password):
    """Registra un nuevo usuario"""

    async def _register():
        client = ctx.obj["client"]
        success = await client.register(username, email, password)
        if success:
            rprint("[green]Usuario registrado exitosamente[/green]")
        else:
            rprint("[red]Error al registrar usuario[/red]")

    asyncio.run(_register())


@cli.command()
@click.argument("username")
@click.argument("password")
@click.pass_context
def login(ctx, username, password):
    """Inicia sesión"""

    async def _login():
        client = ctx.obj["client"]
        success = await client.login(username, password)
        if success:
            rprint("[green]Inicio de sesión exitoso[/green]")
        else:
            rprint("[red]Error de autenticación[/red]")

    asyncio.run(_login())


@cli.command()
@click.pass_context
def logout(ctx):
    """Cierra sesión"""

    async def _logout():
        client = ctx.obj["client"]
        await client.logout()
        rprint("[yellow]Sesión cerrada[/yellow]")

    asyncio.run(_logout())


@cli.command()
@click.pass_context
def whoami(ctx):
    """Muestra información del usuario actual"""

    async def _whoami():
        client = ctx.obj["client"]
        user = await client.get_current_user()
        if user:
            rprint(f"[green]Usuario: {user['username']}[/green]")
            rprint(f"[green]Email: {user['email']}[/green]")
        else:
            rprint("[red]No autenticado[/red]")

    asyncio.run(_whoami())


@cli.command()
@click.argument("local_file")
@click.argument("remote_file")
@click.pass_context
def put(ctx, local_file, remote_file):
    """Sube un archivo al sistema GridDFS"""

    async def _put():
        client = ctx.obj["client"]
        success = await client.put_file(local_file, remote_file)
        if success:
            rprint(
                f"[green]Archivo {local_file} subido exitosamente como {remote_file}[/green]"
            )
        else:
            rprint("[red]Error subiendo archivo[/red]")

    asyncio.run(_put())


@cli.command()
@click.argument("remote_file")
@click.argument("local_file")
@click.pass_context
def get(ctx, remote_file, local_file):
    """Descarga un archivo del sistema GridDFS"""

    async def _get():
        client = ctx.obj["client"]
        success = await client.get_file(remote_file, local_file)
        if success:
            rprint(
                f"[green]Archivo {remote_file} descargado exitosamente como {local_file}[/green]"
            )
        else:
            rprint("[red]Error descargando archivo[/red]")

    asyncio.run(_get())


@cli.command()
@click.option("--directory", "-d", default="/", help="Directorio a listar")
@click.pass_context
def ls(ctx, directory):
    """Lista archivos en un directorio"""

    async def _ls():
        client = ctx.obj["client"]
        files = await client.list_files(directory)

        if not files:
            rprint(f"[yellow]No hay archivos en {directory}[/yellow]")
            return

        table = Table(title=f"Archivos en {directory}")
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="green")
        table.add_column("Ruta", style="blue")
        table.add_column("Tamaño", style="yellow")
        table.add_column("Bloques", style="magenta")
        table.add_column("Creado", style="white")

        for file in files:
            size_str = FileUtils.format_file_size(file["size"])
            table.add_row(
                str(file["id"]),
                file["filename"],
                file["filepath"],
                size_str,
                str(file["num_blocks"]),
                file["created_at"],
            )

        console.print(table)

    asyncio.run(_ls())


@cli.command()
@click.argument("remote_file")
@click.pass_context
def rm(ctx, remote_file):
    """Elimina un archivo del sistema GridDFS"""

    async def _rm():
        client = ctx.obj["client"]
        success = await client.delete_file(remote_file)
        if success:
            rprint(f"[green]Archivo {remote_file} eliminado exitosamente[/green]")
        else:
            rprint("[red]Error eliminando archivo[/red]")

    asyncio.run(_rm())


@cli.command()
@click.argument("dirpath")
@click.pass_context
def mkdir(ctx, dirpath):
    """Crea un directorio"""

    async def _mkdir():
        client = ctx.obj["client"]
        success = await client.create_directory(dirpath)
        if success:
            rprint(f"[green]Directorio {dirpath} creado exitosamente[/green]")
        else:
            rprint("[red]Error creando directorio[/red]")

    asyncio.run(_mkdir())


@cli.command()
@click.argument("dirpath")
@click.pass_context
def rmdir(ctx, dirpath):
    """Elimina un directorio"""

    async def _rmdir():
        client = ctx.obj["client"]
        success = await client.remove_directory(dirpath)
        if success:
            rprint(f"[green]Directorio {dirpath} eliminado exitosamente[/green]")
        else:
            rprint("[red]Error eliminando directorio[/red]")

    asyncio.run(_rmdir())


@cli.command()
@click.pass_context
def status(ctx):
    """Muestra el estado del sistema"""

    async def _status():
        client = ctx.obj["client"]

        # Verificar autenticación
        user = await client.get_current_user()
        if user:
            rprint(f"[green]✓ Autenticado como: {user['username']}[/green]")
        else:
            rprint("[red]✗ No autenticado[/red]")

        # Verificar conexión con NameNode
        try:
            import httpx

            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"{client.namenode_url}/health")
                if response.status_code == 200:
                    rprint(
                        f"[green]✓ NameNode conectado: {client.namenode_url}[/green]"
                    )
                else:
                    rprint(
                        f"[red]✗ NameNode no disponible: {client.namenode_url}[/red]"
                    )
        except Exception as e:
            rprint(f"[red]✗ Error conectando al NameNode: {e}[/red]")

    asyncio.run(_status())


if __name__ == "__main__":
    cli()
