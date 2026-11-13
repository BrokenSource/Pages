from datetime import UTC, datetime
from inspect import cleandoc
from pathlib import Path
from typing import Literal

from attrs import Factory, define
from delusion.chat.option.ollama import Ollama
from rich import print

type Languages = Literal[
    "en",
    "br",
]

@define
class Translator:
    chat: Ollama = Factory(Ollama)

    manifest: Path = Path.cwd().joinpath("zensical.toml")

    website: Path = Path.cwd().joinpath("website")
    """Path to the project website directory"""

    def __attrs_post_init__(self):
        if not self.manifest.exists():
            raise RuntimeError

        self.chat.serve()
        self.chat.gemma4("e4b").pull()
        self.chat.temperature(0.0)
        self.chat.context(k=64)

    def make(self, name: str, link: str, lang: str):
        for path in self.website.joinpath("en").rglob("*"):
            relative = path.relative_to(self.website)

            # Skip auto and dirs
            if ("auto" in relative.parts):
                continue
            if path.is_dir():
                continue

            target = self.website.joinpath(link, relative)
            target.parent.mkdir(parents=True, exist_ok=True)

            # Copy files as-is
            if path.suffix != ".md":
                # target.write_bytes(path.read_bytes())
                continue

            with self.chat.branch():
                timestamp = datetime.now(UTC).isoformat()
                self.chat.send(path.read_text(), role="user")
                self.chat.send(cleandoc(f"""
                    # Instructions

                    You are an professional translator.

                    - The user has sent a text file with documentation or readme contents.
                    - You MUST translate the WHOLE file into a target language below.
                    - Copy verbatim structural parts, whitespaces, indentation.
                    - DO NOT rewrite, modify contents, or format the document.
                    - ONLY translate paragraphs, comments, code snippets, visible content.
                    - ALWAYS reword or use more natural expressions when applicable.

                    ## Frontmatter

                    Documents that contain YAML tags at the top must start with, and have a newline after '---', also to be translated into the language, except the 'icon:' field:

                    ```md
                    ---
                    (frontmatter)
                    ---

                    (contents)
                    ```

                    ## Disclaimer

                    At the end of the document, insert the following notice translated naturally into the target language, with a preceding newline:

                    ```md
                    <div align="center"><hr><small>✨ Machine translated with <code>{self.chat.model}</code> model at <code>{timestamp}</code></small></div>
                    ```

                    ## Output

                    Write the final translated document directly, without a preamble or post-notes. Simply start with '---' and end the response with the disclaimer.

                    ## Target Language

                    Translate the document into: {name}
                """), role="system")

                message = self.chat.generate()
                assert message.text is not None

                target.write_text(message.text)

                print(self.chat)

def main():
    translator = Translator()
    translator.make(name="Brazilian Portuguese", link="pt", lang="pt-BR")

if __name__ == "__main__":
    main()
