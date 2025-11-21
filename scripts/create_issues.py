import re
import subprocess
import json
import sys
import os
import time

TODO_FILE = "docs/setup/TODO.md"
REPO = "joluc/homelab"
PROJECT_TITLE = "Homelab Setup"

def run_gh_command(args):
    """Runs a gh command and returns the output."""
    cmd = ["gh"] + args
    # print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def create_project():
    """Creates a GitHub user project or returns existing one."""
    print(f"Checking for existing project '{PROJECT_TITLE}'...")
    out = run_gh_command([
        "project", "list",
        "--owner", "joluc",
        "--format", "json"
    ])
    projects = json.loads(out)['projects']
    for p in projects:
        if p['title'] == PROJECT_TITLE:
            print(f"Project '{PROJECT_TITLE}' already exists: {p['url']}")
            return p

    print(f"Creating project '{PROJECT_TITLE}'...")
    out = run_gh_command([
        "project", "create",
        "--owner", "joluc",
        "--title", PROJECT_TITLE,
        "--format", "json"
    ])
    project_data = json.loads(out)
    return project_data

def parse_todo_file():
    """Parses the TODO file into sections and subtasks."""
    with open(TODO_FILE, "r") as f:
        content = f.read()

    sections = []
    parts = re.split(r'(^## Phase .*$)', content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        title = parts[i].strip().replace("## ", "")
        raw_body = parts[i+1].strip()

        # Parse body for top-level items
        items = []
        lines = raw_body.split('\n')
        current_item = None

        intro_text = []

        for line in lines:
            # Check for top-level item: "- [ ] " or "* [ ] " at start of line
            match = re.match(r'^[-*] \[ \] (.*)', line)
            if match:
                if current_item:
                    items.append(current_item)
                current_item = {
                    "title": match.group(1).strip(),
                    "body": ""
                }
            elif current_item:
                current_item["body"] += line + "\n"
            else:
                intro_text.append(line)

        if current_item:
            items.append(current_item)

        sections.append({
            "title": title,
            "intro": "\n".join(intro_text).strip(),
            "items": items
        })

    return sections

def find_issue(title):
    """Finds an open issue by title."""
    out = run_gh_command([
        "issue", "list",
        "--repo", REPO,
        "--search", f"{title} in:title",
        "--state", "open",
        "--json", "number,url,title"
    ])
    issues = json.loads(out)
    for issue in issues:
        if issue['title'] == title:
            return issue
    return None

def create_issue(title, body, labels):
    """Creates an issue in the repo."""
    print(f"Creating issue: {title}")
    # gh issue create returns the URL of the created issue on stdout
    url = run_gh_command([
        "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
        "--label", ",".join(labels)
    ])
    # Extract number from URL (e.g., https://github.com/joluc/homelab/issues/1)
    number = url.split("/")[-1]
    return {"url": url, "number": number}

def update_issue(number, body, labels=None):
    """Updates an issue body and labels."""
    print(f"Updating issue #{number}...")
    cmd = [
        "issue", "edit",
        str(number),
        "--repo", REPO,
        "--body", body
    ]
    if labels:
        cmd.extend(["--add-label", ",".join(labels)])

    run_gh_command(cmd)

def ensure_label(name, color, description):
    """Ensures a label exists."""
    # Check if label exists
    # We can just try to create it and ignore error if it exists, or check list.
    # `gh label create` fails if exists.
    # Let's just try to create it.
    print(f"Ensuring label '{name}'...")
    subprocess.run(["gh", "label", "create", name, "--color", color, "--description", description, "--repo", REPO], capture_output=True)

def add_issue_to_project(project_number, issue_url):
    """Adds an issue to the project."""
    # print(f"Adding issue to project...")
    run_gh_command([
        "project", "item-add",
        str(project_number),
        "--owner", "joluc",
        "--url", issue_url
    ])

def main():
    if not os.path.exists(TODO_FILE):
        print(f"File {TODO_FILE} not found.")
        sys.exit(1)

    project = create_project()
    project_number = project['number']
    print(f"Using Project: {project['url']} (Number: {project_number})")

    # Ensure base labels
    ensure_label("kind:phase", "0E8A16", "Top-level phase tracking")
    ensure_label("kind:task", "1D76DB", "Individual task")
    ensure_label("setup", "0E8A16", "Setup related tasks")
    ensure_label("documentation", "0075ca", "Documentation improvements")

    sections = parse_todo_file()
    print(f"Found {len(sections)} sections.")

    for section in sections:
        print(f"\nProcessing Phase: {section['title']}")

        # Extract Phase Number
        phase_match = re.search(r'Phase (\d+)', section['title'])
        phase_num = phase_match.group(1) if phase_match else None
        phase_label = f"phase:{phase_num}" if phase_num else None

        if phase_label:
            ensure_label(phase_label, "FBCA04", f"Phase {phase_num}")

        parent_labels = ["setup", "documentation", "kind:phase"]
        if phase_label:
            parent_labels.append(phase_label)

        # 1. Get or Create Parent Issue
        parent_issue = find_issue(section['title'])
        if not parent_issue:
            parent_issue = create_issue(section['title'], section['intro'], parent_labels)
        else:
            print(f"Found existing parent issue #{parent_issue['number']}")
            # Update labels for existing parent
            update_issue(parent_issue['number'], section['intro'], parent_labels) # Update body temporarily to just intro, will append tasks later

        add_issue_to_project(project_number, parent_issue['url'])

        # 2. Create Child Issues
        child_refs = []
        for item in section['items']:
            clean_title = item['title'].replace("**", "").replace(":", "")

            # Improved child body
            child_body = f"""{item['body']}

Parent Issue: #{parent_issue['number']}"""
            child_labels = ["setup", "documentation", "kind:task"]
            if phase_label:
                child_labels.append(phase_label)

            # Check if child already exists linked to this parent?
            # For now, we are just creating new ones if we run this again, which is bad.
            # But the user asked to "Improve", implying we might update existing ones if we could find them.
            # Since we didn't store state, finding them is hard.
            # However, `find_issue` works by title.

            existing_child = find_issue(clean_title)
            if existing_child:
                 print(f"Updating existing child issue #{existing_child['number']}")
                 update_issue(existing_child['number'], child_body, child_labels)
                 child = existing_child
                 child['url'] = existing_child['url'] # Ensure URL is present
            else:
                child = create_issue(clean_title, child_body, child_labels)
                add_issue_to_project(project_number, child['url'])

            child_refs.append(f"- [ ] #{child['number']} {clean_title}")

            time.sleep(1)

        # 3. Update Parent Issue with list of children
        new_parent_body = f"{section['intro']}\n\n### Tasks\n" + "\n".join(child_refs)
        # We already updated labels above, so just body here
        update_issue(parent_issue['number'], new_parent_body)

if __name__ == "__main__":
    main()
