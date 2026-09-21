# Function Review

After creating or modifying a function, delegate the changed function to `DescriptionManager` before considering the task complete. Have it check the function's description, docstring clarity, parameter and return documentation, and consistency of type annotations with nearby code.

Keep the review focused on the changed function. Report actionable findings with file and line references, and do not make unrelated documentation or typing changes automatically.

# README Documentation

After creating or modifying a project directory, source file, or Python function, delegate the affected scope to `ProjectDocumentationManager` before considering the task complete. Have it update `README.md` with verified project, directory, file, function, setup, usage, and logging information, including the contents page.

Keep README updates limited to verified repository information. Preserve sections for other projects in the repository and do not invent undocumented behavior.

Follow the [Google developer documentation style guide](https://developers.google.com/style)
for README changes, unless a project-specific convention in this file requires
otherwise:

- Use a clear, concise, task-focused style and prefer active voice.
- Use present tense for descriptions of current behavior.
- Address the reader directly when instructions require an action.
- Use sentence case for headings and avoid unnecessary introductory text.
- Keep paragraphs short. Use numbered lists for procedures and bulleted lists
	for related items.
- Use descriptive link text rather than displaying raw URLs, except in code,
	configuration values, or command examples.
- Format file paths, commands, code elements, configuration keys, and literal
	values as code.
- Define abbreviations on first use when they are not familiar to the intended
	audience, and use terminology consistently afterward.
- State limitations, prerequisites, and unsupported behavior explicitly.
- Do not use promotional claims, vague qualifiers, unexplained jargon, or
	undocumented assumptions.