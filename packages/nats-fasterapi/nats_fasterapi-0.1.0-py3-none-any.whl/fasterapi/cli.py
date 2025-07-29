import click
from fasterapi.scaffolder.generate_project import create_project
from fasterapi.scaffolder.generate_crud import create_crud_file
from fasterapi.scaffolder.generate_schema import create_schema_file

@click.group()
def cli():
    """FasterAPI CLI — scaffold FastAPI apps with ease"""
    pass

@cli.command()
@click.argument("name")
def new(name):
    """Create a new FastAPI project."""
    create_project(name)

@cli.command()
@click.argument("name")
def make_crud(name):
    """Generate CRUD repository functions for a schema."""
    create_crud_file(name)
    
@cli.command()
@click.argument("name")
def make_schema(name):
    """Generate Pydantic classes templates for a schema."""
    create_schema_file(name)

if __name__ == "__main__":
    cli()
