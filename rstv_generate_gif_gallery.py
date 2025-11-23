import os
import urllib.parse

import rstv_config

def generate_media_html(folder_path):
    item_name = os.path.basename(folder_path)
    # Generate HTML content for a folder
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RetroStrange GIFs: {item_name}</title>
        <style>
            body {{
                font-family: monospace;
                margin: 20px 40px 20px 40px;
            }}
            h1 {{
                text-align: center;
                font-size: 3.5em;
                line-height: 1.5em;
            }}
            ul {{
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                grid-gap: 10px;
            }}
            li {{
                text-align: center;
                font-size: 2em;
            }}
            p {{
                font-size: 1.8em;
                line-height: 1em;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <h1>GIFs for "{item_name}"</h1>
        <p>Back to <a href="https://retrostrange.com/gifs">RetroStrange GIFs Gallery</a> main</p>
        <ul>
    """

    # List all GIFs in the folder
    gif_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.gif')]

    for gif_file in gif_files:
        html_content += f"            <li><a href=\"{gif_file}.html\"><img src=\"{gif_file}\" alt=\"{gif_file}\"></a></li>\n"

    # Close HTML tags
    html_content += """
        </ul>
        <p>Brought to you by <a href="https://retrostrange.com">RetroStrange</a>. Watch shows like this on <a href="https://live.retrostrange.com">RetroStrange TV</a> and <a href="http://patreon.com/philnelson">support us on Patreon</a>.</p>
    </body>
    </html>
    """

    return html_content

def generate_individual_html(file_path, folder):
    item_name = os.path.basename(file_path)
    # Generate HTML content for a folder
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RetroStrange GIFs: {item_name[:-10]}</title>
        <meta property="og:image:secure_url" content="https://retrostrange.com/gifs/{urllib.parse.quote(folder)}/{urllib.parse.quote(file_path)}"
            class="black-bgcolor" />

        <meta property="og:image:type" content="image/gif" class="black-bgcolor" />

        <meta property="og:image:width" content="300" class="black-bgcolor" />

        <meta property="og:image:height" content="300" class="black-bgcolor" />
        <style>
            body {{
                font-family: monospace;
                margin: 20px 40px 20px 40px;
            }}
            h1 {{
                text-align: center;
                font-size: 3.5em;
                line-height: 1.5em;
            }}
            h2 {{
                text-align: center;
                font-size: 2.5em;
                line-height: 2.2em;
            }}
            ul {{
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                grid-gap: 10px;
            }}
            li {{
                text-align: center;
                font-size: 2em;
            }}
            p {{
                font-size: 1.8em;
                line-height: 1em;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
            
            input[type=text] {{
                width: 70%;
                height: 40px;
                font-size: 1em;
            }}
            
            footer p {{
                text-align: center;
                padding-top: 60px;
            }}
        </style>
    </head>
    <body>
        <h1>GIF from "{item_name[:-10]}"</h1>
        <p>Back to <a href="https://retrostrange.com/gifs">RetroStrange GIFs Gallery</a> main page</p>
        <p>Back "<a href="https://retrostrange.com/gifs/{folder}/{folder}.html">{folder}</a>" section</p>
        <img src="{file_path}" />
        <p>Download or share this file:</p>
        <input type="text" value="https://retrostrange.com/gifs/{urllib.parse.quote(folder)}/{urllib.parse.quote(file_path)}" />
        <footer>
        <p>Brought to you by <a href="https://retrostrange.com">RetroStrange</a>. Watch shows like this on <a href="https://live.retrostrange.com">RetroStrange TV</a> and <a href="http://patreon.com/philnelson">support us on Patreon</a>.</p>
        </footer>
    </body>
    </html>
    """

    return html_content

def generate_root_html(directory_path, folder_names):
    print("Generating index page...")
    # Generate HTML content for the root page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RetroStrange GIFs Gallery</title>
        <style>
            body {
                font-family: monospace;
                margin: 20px 40px 20px 40px;
            }
            h1 {
                text-align: center;
                font-size: 3.5em;
                line-height: 1.5em;
            }
            h2 {
                text-align: center;
                font-size: 2.5em;
                line-height: 2.2em;
            }
            ul {
                
            }
            li {
                font-size: 1.8em;
                line-height: 1.5em;
                padding: 6px 6px 6px 0;
            }
            p {
                font-size: 2em;
                line-height: 1.5em;
            }
        </style>
    </head>
    <body>
        <h1><a href="https://retrostrange.com">RetroStrange</a> GIFs Gallery</h1>
        <p>10 automatically-generated GIFs from each item in the RetroStrange Media Catalog as seen on <a href="https://live.retrostrange.com">RetroStrange TV</a>. <em>Please do not hotlink the GIFs,</em> but do download, use and share however else you want.</p>
        <ul>
    """

    # List all folder names and link to their respective pages
    for folder_name in folder_names:
        folder_page_link = f"<a href=\"{folder_name}/{folder_name}.html\">{folder_name}</a>"
        html_content += f"            <li>{folder_page_link}</li>\n"

    # Close HTML tags
    html_content += """
        </ul>
        <p>Brought to you by <a href="https://retrostrange.com">RetroStrange</a>. Watch shows like this on <a href="https://live.retrostrange.com">RetroStrange TV</a> and <a href="http://patreon.com/philnelson">support us on Patreon</a>.</p>
    </body>
    </html>
    """

    # Write the root HTML file
    root_html_path = os.path.join(directory_path, "index.html")
    with open(root_html_path, "w") as root_html_file:
        root_html_file.write(html_content)

def generate_html_pages(root_directory):
    print("Generating media pages...")
    # List all directories in the root directory
    subdirectories = [d for d in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, d))]
    subdirectories.sort()

    for subdirectory in subdirectories:
        if not subdirectory.startswith("."):
            # Generate HTML for each subdirectory
            subdirectory_path = os.path.join(root_directory, subdirectory)
            html_content = generate_media_html(subdirectory_path)
            
            print(f"Generating {subdirectory}")
    
            # Write the HTML file for the subdirectory
            html_file_path = os.path.join(subdirectory_path, f"{subdirectory}.html")
            with open(html_file_path, "w") as html_file:
                html_file.write(html_content)
                
            # Get all GIFs in the folder
            gif_files = [file for file in os.listdir(subdirectory_path) if file.lower().endswith('.gif')]
            gif_files.sort(reverse = True)
            
            for gif_file in gif_files:
                individual_html_content = generate_individual_html(gif_file, subdirectory)
                individual_html_file_path = os.path.join(subdirectory_path, f"{gif_file}.html")
                with open(individual_html_file_path, "w") as individual_html_file:
                    individual_html_file.write(individual_html_content)

    # Generate HTML for the root page
    generate_root_html(root_directory, subdirectories)

# Replace 'your_directory_path' with the path to your directory containing folders with GIFs
generate_html_pages(rstv_config.gifs_path)
