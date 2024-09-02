import os

import rstv_config

def generate_html(folder_path):
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
                font-size: 2em;
                line-height: 2.2em;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <h1>{item_name}</h1>
        <ul>
    """

    # List all GIFs in the folder
    gif_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.gif')]

    for gif_file in gif_files:
        html_content += f"            <li><a href=\"{gif_file}\"><img src=\"{gif_file}\" alt=\"{gif_file}\"></a></li>\n"

    # Close HTML tags
    html_content += """
        </ul>
        <p>Brought to you by <a href="https://retrostrange.com">RetroStrange</a>. Watch our 24/7 stream on <a href="https://live.retrostrange.com">RetroStrange TV</a>.</p>
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
            }
            
            ul {
                
            }
            
            li {
                font-size: 2em;
                line-height: 2.2em;
                padding: 6px 6px 6px 0;
            }
            
            p {
                font-size: 2em;
                line-height: 2.2em;
            }
        </style>
    </head>
    <body>
        <h1><a href="https://retrostrange.com">RetroStrange</a> GIFs Gallery</h1>
        <p>7 automatically-generated GIFs from each item in the RetroStrange Media Catalog as seen on <a href="https://live.retrostrange.com">RetroStrange TV</a>. <em>Please do not hotlink the GIFs,</em> but do download, use and share however else you want.</p>
        <ul>
    """

    # List all folder names and link to their respective pages
    for folder_name in folder_names:
        folder_page_link = f"<a href=\"{folder_name}/{folder_name}.html\">{folder_name}</a>"
        html_content += f"            <li><img src=\"{folder_name}/{folder_name}.1.gif\" />{folder_page_link}</li>\n"

    # Close HTML tags
    html_content += """
        </ul>
        <p>Brought to you by <a href="https://retrostrange.com">RetroStrange</a>. Watch our 24/7 stream on <a href="https://live.retrostrange.com">RetroStrange TV</a>.</p>
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
        
        # Generate HTML for each subdirectory
        subdirectory_path = os.path.join(root_directory, subdirectory)
        html_content = generate_html(subdirectory_path)
        
        print(f"Generating {subdirectory}")

        # Write the HTML file for the subdirectory
        html_file_path = os.path.join(subdirectory_path, f"{subdirectory}.html")
        with open(html_file_path, "w") as html_file:
            html_file.write(html_content)

    # Generate HTML for the root page
    generate_root_html(root_directory, subdirectories)

# Replace 'your_directory_path' with the path to your directory containing folders with GIFs
generate_html_pages(rstv_config.gifs_path)
