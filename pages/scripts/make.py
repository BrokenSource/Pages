import os
import subprocess
from pathlib import Path

import minify

repo = Path.cwd()
site = repo.joinpath("site")
docs = repo.joinpath("website")

def main():

    # Fixme (relaxed): Hardlink readme as index.md when missing
    if not (index := docs.joinpath("index.md")).exists():
        if (readme := repo.joinpath("readme.md")).exists():
            subprocess.check_call(("ln", readme, index))

    # Baseline website build
    subprocess.check_call(("zensical", "build"))

    # Optimize static files
    # Fixme: https://github.com/zensical/backlog/issues/15
    for pattern, mediatype in (
        ("*.html", "text/html"),
        ("*.css",  "text/css"),
        ("*.svg",  "image/svg+xml"),
        # ("*.js",   "application/javascript"),
        ("*.json", "application/json"),
        ("*.xml",  "application/xml"),
    ):
        for file in site.rglob(pattern):
            print(f"Optimizing {file}")
            file.write_text(minify.string(
                string=file.read_text("utf-8"),
                mediatype=mediatype,
            ), "utf-8")

    # Remove unwanted files from theme package
    for unwanted in ("mkdocs_theme.yml", "__init__.py"):
        site.joinpath(unwanted).unlink(missing_ok=True)

    # Move to expected actions/upload-pages-artifact
    if ("GITHUB_ACTIONS" in os.environ):
        site.rename(site.parent.joinpath("_site"))

if __name__ == "__main__":
    main()
