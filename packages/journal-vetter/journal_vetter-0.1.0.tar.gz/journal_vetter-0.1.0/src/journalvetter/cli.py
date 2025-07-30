import click
from .core import do_vet_journals
from .config import load_config
from pathlib import Path
import shutil

#This file defines how the user can interact with the CLI

def clear_resources(resources_dir: Path):
    if not resources_dir.exists():
        return
    for item in resources_dir.iterdir():
        item.unlink()

#Specifically, the user can override the yaml's impact-factor, cell-line, research-field, modeling type & 
#provide their pdf files for parsing & analysis
@click.command()
@click.option("--config", default="config.yaml", help="Path to YAML config file")
@click.option("--impact-factor", help="Override desired impact factor range")
@click.option("--cell-line", help="Override desired cell line")
@click.option("--field", help="Override desired research field")
@click.option("--model-type", help="Override desired modeling type")
@click.option(
    "--download", "-d",
    multiple=True,
    help="local path of a PDF to fetch into the resources directory"
)
def run(config, field, impact_factor, cell_line, model_type, download):
    """Run the Journal Vetting pipeline."""
    main(config, field, impact_factor, cell_line, model_type, download, mode="cli")

#load our config file & populate necessary paths (resources & output)
def main(config_path="config.yaml", field=None, impact_factor=None, cell_line=None, model_type=None, download=None, mode="library"):
    cfg = load_config()
    config_file_path = Path(config_path).resolve()
    config_dir = config_file_path.parent
    resources_path = (config_dir / cfg["paths"]["resources_dir"]).resolve()
    output_file = (config_dir / cfg["paths"]["output_file"]).resolve()
    print("Reading from resources at:", resources_path)

#download provided pdfs from filepaths (NO URLs)
    clear_resources(resources_path)
    for src in download:
        src_path = Path(src).expanduser().resolve()
        if not src_path.is_file():
            raise click.BadParameter(f"File not found: {src}")
        dest = resources_path / src_path.name
        dest.write_bytes(src_path.read_bytes())
        click.echo(f"✔️  Copied {src_path} → {dest}")

#call our main logic (->core.py)
    do_vet_journals(
        cfg,
        config_file_path,
        resources_path,
        output_file,
        field,
        impact_factor,
        cell_line,
        model_type,
        mode
    )

if __name__ == "__main__":
    run()
