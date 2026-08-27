from textnode import TextNode, TextType
from htmlnode import *
from markdown_blocks import *
from inline_markdown import *
from textnode import *

import sys
import os
import shutil
from pathlib import Path
from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType
from htmlnode import ParentNode, LeafNode
from inline_markdown import text_to_textnodes
from textnode import text_node_to_html_node

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(n) for n in text_nodes]

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            children.append(ParentNode("p", text_to_children(block)))
        elif block_type == BlockType.HEADING:
            # Determine level based on number of '#'
            level = len(block.split(" ")[0])
            children.append(ParentNode(f"h{level}", text_to_children(block.lstrip("# "))))
        elif block_type == BlockType.CODE:
            # Code block is usually <pre><code>...</code></pre>
            content = block.strip("```")
            children.append(ParentNode("pre", [LeafNode("code", content)]))
        elif block_type == BlockType.QUOTE:
            new_text = " ".join([line.lstrip("> ") for line in block.split("\n")])
            children.append(ParentNode("blockquote", text_to_children(new_text)))
        elif block_type == BlockType.ULIST:
            items = [ParentNode("li", text_to_children(line.lstrip("- "))) for line in block.split("\n")]
            children.append(ParentNode("ul", items))
        elif block_type == BlockType.OLIST:
            items = [ParentNode("li", text_to_children(line[3:])) for line in block.split("\n")]
            children.append(ParentNode("ol", items))
            
    return ParentNode("div", children)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, "r") as f:
        markdown_content = f.read()
    with open(template_path, "r") as f:
        template_content = f.read()
        
    html_content = markdown_to_html_node(markdown_content).to_html()
    title = extract_title(markdown_content)
    
    page = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # --- FIX: The Replacement Logic ---
    # We must ensure basepath starts with / and ends with / to prevent double slashes
    # Example: if basepath is "/REPO_NAME/", result is "/REPO_NAME/index.css"
    # Example: if basepath is "/", result is "/index.css"
    clean_basepath = f"/{basepath.strip('/')}/" if basepath != "/" else "/"
    
    # We replace 'href="/' with 'href="/REPO_NAME/'
    # Note: We use .replace('href="/', f'href="{clean_basepath}')
    page = page.replace('href="/', f'href="{clean_basepath}')
    page = page.replace('src="/', f'src="{clean_basepath}')
    # ----------------------------------
    
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(page)


def copy_contents(src, dst):
    # 1. Clean the destination directory
    if os.path.exists(dst):
        print(f"Cleaning destination: {dst}")
        shutil.rmtree(dst)
    
    # 2. Recreate the destination directory
    os.makedirs(dst)
    
    # 3. Recursive copy function
    def copy_recursive(source_path, dest_path):
        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            d = os.path.join(dest_path, item)
            
            if os.path.isfile(s):
                print(f"Copying file: {s} -> {d}")
                shutil.copy(s, d)
            elif os.path.isdir(s):
                print(f"Copying directory: {s} -> {d}")
                os.makedirs(d, exist_ok=True)
                copy_recursive(s, d)

    copy_recursive(src, dst)

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    raise Exception("No h1 header found")

# Unit tests
def test_extract_title():
    assert extract_title("# Hello") == "Hello"
    assert extract_title("## Not a title\n#  World  ") == "World"
    try:
        extract_title("No header here")
    except Exception as e:
        assert str(e) == "No h1 header found"

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    # Iterate through all files and directories in the content directory
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)

        if os.path.isfile(from_path):
            # Only process .md files
            if from_path.endswith(".md"):
                # Change the destination extension to .html
                dest_path = dest_path.replace(".md", ".html")
                generate_page(from_path, template_path, dest_path, basepath)
        else:
            # If it's a directory, create it in public and recurse
            os.makedirs(dest_path, exist_ok=True)
            generate_pages_recursive(from_path, template_path, dest_path, basepath)

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    static_dir = "static"
    docs_dir = "docs"
    
    # 1. Clean and copy static files
    if os.path.exists(static_dir):
        copy_contents(static_dir, docs_dir)
    else:
        print(f"Source directory '{static_dir}' not found.")
    
    # 2. Generate content pages recursively
    if os.path.exists(static_dir):
        copy_contents(static_dir, docs_dir)
    else:
        print(f"Content directory '{content_dir}' not found.")
    generate_pages_recursive("content", "template.html", docs_dir, basepath)

if __name__ == "__main__":
    main()