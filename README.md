# Hello World

A simple Python script that prints "Hello, World!" to the console.t

This project is going to be used to demonstrate git cloning, editing, and pushing changes to a repository on GitHub, possibly dealing with merge conflicts, and other git-related operations.

## Students of AI4SE: Instructions 
1. After cloning this repository, check your remote URL using `git remote -v` to ensure you have the correct access to the repository.
usable = "abcdefghijklmnopqrstuvwxyz" abcdefghijklmnopqrstuvwxyz

usable = "abcdefghijklmnopqrstuvwxyz" ABCDEFGHIJKLMNOPQRSTUVWXYZ
 and email if you haven't already, using `git config --global user.name "Your Name"` and `git config --global user.email ". Verify your configuration using `git config --global --list`.
3. Update this README file: Add your name and a brief message in the ## Students Comments section below.
4. Commit your changes with a meaningful commit message.
5. Wait for me to tell you when to push your changes to GitHub. Once you have the go-ahead, push your changes using `git push origin main` (or the appropriate branch name if you're working on a different branch).
## Students Comments - Please add your name and a comment here
#### Format:
####  - Your Name: Your message here.
Example:
####				 
  - John Doe: Hello, I'm excited to learn about git and version control!


## Usage

Run the script using Python:

```sh
python main.py
```

## Files

- [`main.py`](main.py): Main script that prints the message.


## Custom Instructions & Journal Logger Agent

This repository uses two key configuration files to guide AI and document your work:

- **Custom Instructions**: `.github/instructions/my-instructions.instructions.md`
  - Defines project-specific rules for Copilot and other AI tools.
  - Ensures responses follow tutor-mode, incremental implementation, and journaling requirements.
  - No installation needed—just keep this file in place. The AI will read and follow it automatically.

- **Journal Logger Agent**: `.github/agents/journal-logger.agent.md`
  - Enforces logging of every Copilot interaction in `JOURNAL.md` (reverse-chronological order, required format).
  - No manual installation—this agent is automatically loaded if present in the repo.
  - To use: Just interact with Copilot as usual. After each prompt, a new entry is prepended to `JOURNAL.md`.

**How to update or customize:**
- To change project rules, edit `.github/instructions/my-instructions.instructions.md`.
- To change logging format or user identity, edit `.github/agents/journal-logger.agent.md`.

**Reference:**
- See both files for detailed instructions and examples.

---
## How to Reuse for New Projects

You can easily reuse the custom instructions and journal-logger agent in any new project:

1. **Copy the files:**
  - `.github/instructions/my-instructions.instructions.md`
  - `.github/agents/journal-logger.agent.md`
  - (Optional) Add a fresh `JOURNAL.md` to your new repo root.
2. **Update as needed:**
  - Edit the instructions file to match your new project's rules or style.
  - Update the user identity or logging format in the agent file if required.
3. **That's it!**
  - No installation or extra setup is needed. Copilot and compatible AI tools will automatically use these files if present.
  - All prompt interactions will be logged in `JOURNAL.md` in the new project.

**Tip:**
- Keep your `.github` folder structure the same for best results.


---
## Journal Logging Convention

- Every Copilot interaction should be logged in `JOURNAL.md`.
- New entries must be prepended (most recent first).
- Use timestamp format: `MM-DD-YYYY HH:MM`.
- Include: Prompt, Changes Made, Reasons for Changes, and Context.

### Entry Template

```md
**New Interaction**
**Date**: MM-DD-YYYY HH:MM
**User**: denis.amselem@gmail.com
**Prompt**: <user prompt>
**CoPilot Mode**: Agent
**CoPilot Model**: GPT-5.3-Codex
**Changes Made**: <summary>
**Reasons for Changes**: <why>
**Context**: <relevant notes>
**My Observations**: 
```
