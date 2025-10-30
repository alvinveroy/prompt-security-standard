"""CLI tool for UPSS."""

import asyncio
from pathlib import Path

import click


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """UPSS - Universal Prompt Security Standard CLI"""
    pass


@cli.command()
@click.option(
    "--mode", type=click.Choice(["filesystem", "postgresql"]), default="filesystem"
)
@click.option("--base-path", default="./prompts", help="Base path for prompts")
@click.option("--db-url", help="PostgreSQL connection string")
def init(mode, base_path, db_url):
    """Initialize UPSS configuration."""
    click.echo(f"Initializing UPSS in {mode} mode...")

    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    (base / "system").mkdir(exist_ok=True)
    (base / "user").mkdir(exist_ok=True)
    (base / "fallback").mkdir(exist_ok=True)

    # Create config files
    (base / "metadata.json").touch(exist_ok=True)
    (base / "audit.jsonl").touch(exist_ok=True)
    (base / "roles.json").touch(exist_ok=True)

    # Initialize metadata
    import json

    metadata_file = base / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump({"prompts": {}}, f, indent=2)

    click.echo(f"✓ Created directory structure at {base}")
    click.echo(f"✓ Initialized metadata files")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Add prompts to {base}/system/ or {base}/user/")
    click.echo(f"  2. Use upss discover to find hardcoded prompts")
    click.echo(f"  3. Import with upss migrate")


@cli.command()
@click.option("--path", required=True, help="Path to scan for prompts")
@click.option("--output", default="discovered_prompts.json", help="Output file")
@click.option("--extensions", default=".py,.js,.java", help="File extensions to scan")
def discover(path, output, extensions):
    """Discover hardcoded prompts in codebase."""
    click.echo(f"Scanning {path} for hardcoded prompts...")

    # Placeholder implementation
    import re
    from pathlib import Path

    discovered = []
    exts = extensions.split(",")

    for ext in exts:
        for file_path in Path(path).rglob(f"*{ext}"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Simple pattern matching
                # Look for multi-line strings with "prompt" in variable name
                pattern = r'(\w*prompt\w*)\s*=\s*["\']([^"\']{50,})["\']'
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)

                for var_name, prompt_content in matches:
                    discovered.append(
                        {
                            "file": str(file_path),
                            "variable": var_name,
                            "content": prompt_content[:200],  # First 200 chars
                        }
                    )
            except Exception as e:
                click.echo(f"Warning: Could not read {file_path}: {e}", err=True)

    # Save results
    import json

    with open(output, "w") as f:
        json.dump(discovered, f, indent=2)

    click.echo(f"\n✓ Found {len(discovered)} potential prompts")
    click.echo(f"✓ Results saved to {output}")
    click.echo(
        f"\nReview the discovered prompts and use 'upss migrate' to import them."
    )


@cli.command()
@click.option("--input", required=True, help="Input JSON file from discover")
@click.option("--base-path", default="./prompts", help="UPSS prompts directory")
def migrate(input, base_path):
    """Migrate discovered prompts to UPSS."""
    click.echo(f"Migrating prompts from {input}...")

    import json

    from upss import UPSSClient

    # Load discovered prompts
    with open(input, "r") as f:
        prompts = json.load(f)

    async def do_migrate():
        async with UPSSClient(base_path=base_path) as client:
            success = 0
            failed = 0

            for prompt_data in prompts:
                try:
                    name = prompt_data.get("variable", "unnamed")
                    content = prompt_data.get("content", "")

                    await client.create(
                        name=name,
                        content=content,
                        user_id="migration@cli",
                        version="1.0.0",
                    )
                    success += 1
                    click.echo(f"✓ Migrated: {name}")
                except Exception as e:
                    failed += 1
                    click.echo(f"✗ Failed: {name} - {e}", err=True)

            click.echo(f"\n✓ Migration complete: {success} successful, {failed} failed")

    asyncio.run(do_migrate())


if __name__ == "__main__":
    cli()
