# main.py

# create_project_structure.py

import os

REQUIREMENTS_DIR = ".requirements"
RESOURCES_DIR = ".resources"
REQUIREMENTS_MD = "requirements-01.md"
KNOWLEDGE_BASE_MD = "knowledgebase.md"

REQUIREMENTS_AREAS = [
    ("data_sources", "Data source examples"),
    ("integrations", "Integration examples"),
    ("api_examples", "API examples"),
    ("infra_examples", "Infrastructure examples")
]

def prompt_for_multiple_subfolders(area_desc):
    subfolders = {}
    print(f"\nAdd subfolders for {area_desc}.")
    print("You can create multiple subfolders. Type 'q' to stop adding.")

    while True:
        folder_name = input(f"  Enter a subfolder name (or 'q' to finish): ").strip()
        if folder_name.lower() == 'q':
            break
        if folder_name:
            # Check for duplicate folder names
            if folder_name in subfolders:
                print(f"    Folder '{folder_name}' already exists. Please choose a different name.")
                continue

            link_desc = input(f"    Enter a short description for '{folder_name}' (for linking): ").strip()
            subfolders[folder_name] = link_desc if link_desc else folder_name
            print(f"    Added: {folder_name}")

    if subfolders:
        print(f"  Created {len(subfolders)} subfolder(s) for {area_desc}")
    else:
        print(f"  No subfolders created for {area_desc}")

    return subfolders

def prompt_requirements_folders():
    selected = {}

    # First, ask about predefined requirement areas
    for area, desc in REQUIREMENTS_AREAS:
        answer = input(f"Do you have any {desc}? (y/n): ").strip().lower()
        if answer == "y":
            subfolders = prompt_for_multiple_subfolders(desc)
            if subfolders:
                selected[area] = subfolders

    # Then allow custom requirement areas
    print("\nAdd custom requirement areas.")
    while True:
        answer = input("Do you want to add a custom requirement area? (y/n): ").strip().lower()
        if answer == "n":
            break
        elif answer == "y":
            area_name = input("  Enter the requirement area name: ").strip()
            if not area_name:
                continue
            area_desc = input(f"    Enter a description for '{area_name}': ").strip()
            if not area_desc:
                area_desc = area_name

            subfolders = prompt_for_multiple_subfolders(area_desc)
            if subfolders:
                selected[area_name] = subfolders

            # After adding one custom area, ask if they want to add more
            continue_answer = input("Do you want to add another custom requirement area? (y/n): ").strip().lower()
            if continue_answer != "y":
                break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

    return selected

def prompt_resources_folders():
    selected = {}
    print("\nAdd resource folders.")
    while True:
        answer = input("Do you want to add a resource folder? (y/n): ").strip().lower()
        if answer == "n":
            break
        elif answer == "y":
            folder_name = input("  Enter the resource folder name: ").strip()
            if not folder_name:
                continue
            link_desc = input(f"    Enter a short description for '{folder_name}' (for linking): ").strip()
            selected[folder_name] = link_desc if link_desc else folder_name

            # After adding one resource folder, ask if they want to add more
            continue_answer = input("Do you want to add another resource folder? (y/n): ").strip().lower()
            if continue_answer != "y":
                break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    return selected

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("=== .requirements folder setup ===")
    req_selected = prompt_requirements_folders()
    print("\n=== .resources folder setup ===")
    res_selected = prompt_resources_folders()

    # Create .requirements and selected subfolders
    create_folder(REQUIREMENTS_DIR)
    total_req_subfolders = 0
    for main_folder, subfolders in req_selected.items():
        main_path = os.path.join(REQUIREMENTS_DIR, main_folder)
        create_folder(main_path)
        for subfolder in subfolders:
            create_folder(os.path.join(main_path, subfolder))
            total_req_subfolders += 1

    # Create .resources and selected resource folders
    create_folder(RESOURCES_DIR)
    for folder in res_selected:
        create_folder(os.path.join(RESOURCES_DIR, folder))

    # Build links for requirements-01.md and knowledgebase.md
    req_links = ""
    for main_folder, subfolders in req_selected.items():
        if subfolders:
            req_links += f"\n### {main_folder.replace('_', ' ').title()}\n"
            for subfolder, desc in subfolders.items():
                req_links += f"- [{desc}](../{REQUIREMENTS_DIR}/{main_folder}/{subfolder}/)\n"
    if res_selected:
        req_links += "\n## Linked Resources\n"
        for folder, desc in res_selected.items():
            req_links += f"- [{desc}](../{RESOURCES_DIR}/{folder}/)\n"

    res_links = ""
    if res_selected:
        res_links += "\n## Example Resources\n"
        for folder, desc in res_selected.items():
            res_links += f"- [{desc}](./{folder}/)\n"

    # requirements-01.md content
    REQUIREMENTS_MD_CONTENT = f"""Read and understand the knowledge base in the [knowledgebase](../{RESOURCES_DIR}/{KNOWLEDGE_BASE_MD}) file.

# Requirements
Create a ... and ensure the following requirements are met:

Key:
Requirement ID: Area-ID
Description: Describe the requirement
User Story: Describe your identity and your use case for this feature/requirement
Expected Behavior: What do you expect to occur so you can accomplish your user story

| Requirement ID | Description | User Story | Expected Behavior |
|---------------|-------------|------------|-------------------|
| **SALES-001** | Total Sales Performance Overview | As a **Sales Manager**, I want to see the total sales amount across all channels (Internet + Reseller) so that I can understand our overall revenue performance. | Create a combined [Total Sales Amount] measure that sums the sales from Internet and Reseller with proper relationship handling through shared dimensions. |

# Connections:
{req_links}

# Development Rules

Use source 1 to ...

# Conventions

- Follow the global development rules in the [knowledgebase](../{RESOURCES_DIR}/{KNOWLEDGE_BASE_MD}) file.
- Reference requirements by their ID in all code and documentation.
- Document all new resources in the appropriate subfolder and update the knowledge base.
"""

    # knowledgebase.md content
    KNOWLEDGE_BASE_MD_CONTENT = f"""## Who are you

You are an expert project assistant and developer.
Act as a professional in your field, using the specific tools and best practices described in this knowledge base.

## Learning

### Python Packages

When creating Python packages, strictly follow the official Python packaging instructions:
- Open and learn from the following link:
  - https://packaging.python.org/en/latest/

### Sensitive Code

When creating sensitive code, always:
- Open and learn from the documentation links:
  - [Add your security documentation links here]

## Global Development Rules

- All code must be type-annotated and documented.
- Use feature branches and reference requirements in PRs.
- Write unit and integration tests for all new features.
- Document all new resources in the appropriate subfolder and update this knowledge base.
- Follow the conventions and requirements outlined in [requirements-01.md](../{REQUIREMENTS_DIR}/{REQUIREMENTS_MD}).

## File type 1 format rules

- All markdown files must use consistent heading levels and bullet styles.
- Code files must include docstrings and follow the project style guide.
- Data files must be documented in [file-type1](./file-type1/).

{res_links}
"""

    # Create requirements-01.md in .requirements
    create_file(os.path.join(REQUIREMENTS_DIR, REQUIREMENTS_MD), REQUIREMENTS_MD_CONTENT)

    # Create knowledgebase.md in .resources
    create_file(os.path.join(RESOURCES_DIR, KNOWLEDGE_BASE_MD), KNOWLEDGE_BASE_MD_CONTENT)

    print("\nProject structure created successfully.")
    print(f"Created {len(req_selected)} requirement area(s) with {total_req_subfolders} total subfolder(s).")
    print(f"Created {len(res_selected)} resource folder(s).")
    print("You can now drag your relevant files into the created folders.")

if __name__ == "__main__":
    main()
