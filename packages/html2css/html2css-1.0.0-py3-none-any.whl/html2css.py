import re
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate CSS skeleton from HTML')
    parser.add_argument('--input', type=str, required=True, help='Input HTML file path')
    parser.add_argument('--output', type=str, default="index.css", help='Output CSS file path')
    args = parser.parse_args()

    file_path = args.input
    output_path = args.output
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        bb = re.findall(r'<(/?[a-zA-Z0-9]+)([^>]*)>', content)
        hub = ''
        stack = []
        nth = 1
        child = ":nth-child"
        waited_area = []
        waste = ["html", "body"]
        var = ""

    # --- Write CSS Output ---
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("""\
    :root {}
    html {}
    body {}

    @media screen and (max-width: 600px) {
    /* Styles for phones */
    }

    @media screen and (min-width: 601px) and (max-width: 768px) {
    /* Styles for tablets */
    }

    @media screen and (min-width: 769px) and (max-width: 1024px) {
    /* Styles for small laptops/desktops */
    }

    @media screen and (min-width: 1025px) {
    /* Styles for large desktops */
    }
    """)

        for tagname, attributes in bb:
            id_match = re.findall(r'id\s*=\s*"([^"]+)"', attributes)
            class_match = re.findall(r'class\s*=\s*"([^"]+)"', attributes)
            r = len(stack)

            if tagname == "/html":
                break
            elif tagname in ["meta", "link"] or tagname in waste:
                continue
            elif tagname.startswith('/'):
                if stack:
                    stack.pop()
            elif id_match:
                data = f'#{id_match[0]}'
                stack.append(data)
            elif class_match:
                data = f'.{class_match[0]}'
                stack.append(data)
            elif nth > 1:
                if tagname != waited_area:
                    nth = 1
                    waited_area = tagname
                    stack.append(tagname)
                else:
                    nth += 1
                    ans = f'{tagname}{child}({nth})'
                    stack.append(ans)
            else:
                if tagname != waited_area:
                    nth = 1
                    waited_area = tagname
                    stack.append(tagname)
                else:
                    hub = f'{tagname}{child}({nth+1})'
                    stack.append(f'{tagname}{child}({nth})')
                    nth += 1

            if r != len(stack) and not tagname.startswith('/'):
                var = " ".join(stack)
                outfile.write(f"\n{var} {{}}\n")
                if hub:
                    outfile.write(f"{' '.join(stack[:-1])} {hub} {{}}\n")
                    hub = ""

if __name__ == "__main__":
    main()
