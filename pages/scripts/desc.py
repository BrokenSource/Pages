"""
Generate SEO meta descriptions for all pages.

Search engines, specially Bing, **REALLY** want them to exist via webmasters
consoles "--" a missed opportunity for more tokenmaxxing, hire me for it.
"""
from inspect import cleandoc
from pathlib import Path

import frontmatter
from delusion.chat.option.ollamax import Ollama
from pydantic import BaseModel, Field


class Description(BaseModel):
    text: str = Field(
        description="The final descriptive, keyword-rich text that talks about the page contents.",
        examples=[
            "Overview of the project's architecture, supported platforms, core features, design goals, and links to the main documentation sections.",
            "Install the software using the recommended package manager, source builds, or precompiled binaries with platform-specific requirements and setup steps.",
            "Configure display permissions, required system packages, and operating system specific settings needed for a successful installation.",
            "Troubleshoot installation and runtime problems using diagnostic commands, common error explanations, compatibility guidance, and recovery steps.",
            "Release history documenting new features, compatibility improvements, bug fixes, behavioral changes, and notable updates across software versions.",
            "Reference documentation describing available classes, methods, parameters, return values, usage patterns, and implementation details.",
            "Module documentation explaining its purpose, public interfaces, configuration options, supported workflows, and integration points.",
            "Configure application behavior using documented settings, environment variables, configuration files, and supported customization options.",
            "Command-line reference describing available commands, arguments, options, examples, and expected behavior.",
            "Architecture overview describing the project's internal components, execution flow, responsibilities, and relationships between subsystems.",
            "Work in progress page on running the project in Docker containers from Github Container Registry.",
        ]
    )


def main():
    chat = Ollama().serve()
    chat.gemma4("12b").pull()
    chat.temperature(0.25)
    chat.context(k=64)

    # Add project context
    for readme in (Path("website/index.md"), Path("readme.md")):
        if readme.exists():
            chat.send(f"User provides the project Readme for context at {readme.resolve()}:", role="system")
            chat.send(readme.read_text(), role="user")
            break

    # Add website context
    if (manifest := Path("zensical.toml")).exists():
        chat.send(f"User provides the MkDocs Configuration file for context at {manifest.resolve()}:", role="system")
        chat.send(manifest.read_text(), role="user")

    # Walk through all pages
    for markdown in Path.cwd().rglob("*.md"):
        if markdown.name == "readme.md":
            continue

        post = frontmatter.load(markdown)

        # Skip non-documentation
        if not post.metadata:
            continue

        with chat.branch():
            print(f"Markdown {markdown}")

            # Context
            chat.send(role="system", text=f"User provides the Documentation Markdown for summarization at {markdown.resolve()}:")
            chat.send(role="user",   text=markdown.read_text())

            # Summarization
            chat.send(role="system", text=cleandoc("""
                You are an editor specializing in technical documentation.

                The user has provided a Markdown documentation page. Read it as rendered documentation rather than as Markdown source.

                Your task is to understand only the current page and produce a concise semantic summary describing its subject, purpose, intended audience, major concepts, workflows, and technical topics. Preserve important terminology such as commands, package names, APIs, configuration options, feature names, and platform names whenever they are essential to understanding the page.

                The project Readme and MkDocs configuration exist only as background context. They help establish terminology and project context but must never contribute information that is not present on the current page.

                Ignore navigation, frontmatter, badges, tables of contents, generated indexes, repeated boilerplate, licensing information, and other structural or decorative content that is not part of the documentation itself.

                If the page contains little information or is explicitly marked as work in progress, summarize its stated purpose and intended scope without inventing missing sections, future functionality, or undocumented features. Explicitly state it's a work in progress.

                Describe the page itself rather than the project as a whole unless the page is intentionally a project overview.

                Produce a factual semantic summary intended only as input for a later SEO editing step.
            """))

            chat.generate()

            # Generate description
            chat.send(role="system", text=cleandoc(f"""
                ## Instructions

                You are an editor specializing in technical documentation and technical SEO.

                Using only the semantic summary generated previously, write the HTML <meta name="description"> for the current documentation page.

                The description must accurately represent the page and distinguish it from other pages in the same documentation. Describe the information available on this page rather than the project in general, and optimize for readers deciding whether this page answers their search query.

                Write a single sentence of approximately 150-160 characters using clear, direct language and naturally occurring technical keywords. Prefer active voice. Begin naturally with the page title or primary topic whenever doing so improves readability. Preserve important technical terminology and avoid unnecessary filler.

                Do not invent information, speculate about undocumented functionality, repeat keywords unnaturally, use marketing language, or begin with generic phrases such as "Learn about", "Learn how to", "Discover", "Explore", "Welcome", "This page", or "Documentation for". Do not use colons or ellipses.

                Return only the structured output matching the schema below.

                Schema:
                {Description.model_json_schema()}

                The response must begin with '{{' and not a Markdown code block.
            """))
            message = chat.generate(schema=Description)
            post.metadata["description"] = message.model.text
            print(message.model)

        # Consistent metadata organization
        for key in ("title", "icon", "description", "tags"):
            if key in post.metadata:
                post.metadata[key] = post.metadata.pop(key)

        # Safe: Only changes meta yaml
        markdown.write_text(frontmatter.dumps(post=post, sort_keys=False) + '\n')

if __name__ == "__main__":
    main()
