"""
    This is a demo of docu-lite semi-automatic documentation, using this same 
    file as the input test case. To try it on your own files,
    change the appropriate settings in docu-lite.ini
"""
import html
import glob
import os
import configparser
import argparse
import sys

def get_config():
    DEFAULT_INI = "[input] \npattern = ./*.py\n\n[output]\nhtml = docu-lite-outline.html\ncss = docu-lite-style.css\ntext_list = docu-lite-list.txt\n[options]\ndocumentation_mode = off\nignore_docstrings_with = "
    DEFAULT_INI_FILE = "docu-lite.ini"

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", default = DEFAULT_INI_FILE)
    args, _ = parser.parse_known_args()
    config_filepath = args.config
    print(config_filepath, DEFAULT_INI_FILE, config_filepath != DEFAULT_INI_FILE)

    if not os.path.exists(config_filepath):
        if config_filepath != DEFAULT_INI_FILE:
            print(f"Config file not found: {config_filepath}. Is there a typo?")
            sys.exit(1)
        else:
            print(f"No config file found — creating default '{config_filepath}'")
            with open(config_filepath, "w") as f:
                f.write(DEFAULT_INI)

    print(f"Reading options from {config_filepath}")
    config = configparser.ConfigParser()
    config.read(config_filepath)
    return config

def get_config_option(config, section, option, default):
    if (config.has_option(section, option)):
        return config.get(section, option)
    else:
        return default

def get_config_vars():
    config = get_config()
    input_pattern = get_config_option(config, "input", "pattern", "./*.py")
    output_html_file = get_config_option(config, "output", "html", "docu-lite.html")
    output_text_list_file = get_config_option(config, "output", "text_list", "docu-lite-list.txt")
    style_sheet_file = get_config_option(config, "output", "css", "docu-lite.css")
    documentation_mode = get_config_option(config, "options", "documentation_mode", "off")        
    ignore_docstrings_with = get_config_option(config, "options", "ignore_docstrings_with", "")
    
    print(f"Running with options: \n \n[input]\npattern = {input_pattern}\n[output]\nhtml = {output_html_file}\ntext_list = {output_text_list_file}"
          +f"css = {style_sheet_file}\ndocumentation_mode = {documentation_mode}\nignore_docstrings_with = {ignore_docstrings_with}\n")
    return input_pattern, output_html_file, output_text_list_file, style_sheet_file, documentation_mode, ignore_docstrings_with 

def ensure_css_exists(style_sheet_file, documentation_mode):
    """
    look for specified or default css, if not found write a new one and use that
    """
    
    DEFAULT_CSS_DOCS = "* {margin-left:2rem; background: rgb(255, 255, 240);  font-family: system-ui, sans-serif; color:rgb(50, 60, 20);}  \
        \n.filename {font-weight:bold; font-size:2.5rem;}  \
        \n.signature {font-weight:bold;} \
        \n.class {color:rgb(50,100,200); font-size:1.5rem;} \
        \n.def {color:rgb(60, 70, 30); } \
        \n.content {color:rgb(10,10,10); padding-left: 2rem; margin-top:5px; }  \
        \n.docstring {color:rgb(0, 100, 0); }"

    DEFAULT_CSS = DEFAULT_CSS_DOCS
    
    try:
        with open(style_sheet_file, "r", encoding="utf-8") as f:
            pass
    except (FileNotFoundError, OSError):
        print(f"Couldn't open style sheet {style_sheet_file}: creating default\n")
        with open(style_sheet_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CSS if (documentation_mode=="off") else DEFAULT_CSS_DOCS)


class docobj:
    """
    structure to contain information about each object in the document
    """
    def __init__(self, signature):
        self.signature = signature.strip()                              # first line of the object including the def, class etc
        self.indent_spaces = len(signature) - len(signature.lstrip())   # number of spaces up to first letter in signature line
        self.indent_level = 0                                           # indent level of this object
        self.object_type = self.signature.split(" ")[0]                 # see object_signatures=[] in get_doc_objects for possible values
        self.content_start = 0                                          # index of line file_lines one after first line of object
        self.content_end = 0                                            # index of line file_lines containing last line of object
        self.nextobj_index = 0
        self.icon = ''

def get_doc_objects(file_lines):
        """
        converts document into list of objects
        """
        object_signatures = ['class','def','docstring','body']
        objects = []
        indent_level = 0
        indent_spaces = 0

        """
        replace all opening docstring markers with 'docstring' and closing tags with 'body'
        so 'body' means otherwise unclassified content following a docstring
        and in the example css is given the same style as unclassified content following def and class
        """
        in_docstring = False
        for line_no, line in enumerate(file_lines):
            if(not '"""' in line):
                continue
            #print(f"in docstring: {in_docstring}")
            #print(f"raw line: {line}")
            if(line.strip().startswith('"""')):
                replacement_tag = 'docstring ' if not in_docstring else 'body '
                file_lines[line_no] = line.replace('"""',replacement_tag,1)
                in_docstring = not in_docstring
            if(file_lines[line_no].rstrip().endswith('"""')):
                #print(f"extra closer: {file_lines[line_no]}")
                file_lines[line_no] = file_lines[line_no].replace('"""','body ',1) # 'body' should ideally be on next line alone
                in_docstring = False           
            #print(f"new line: {file_lines[line_no]}\n")
            
        """
        find and create document objects and tell them the line numbers
        that their content starts and ends at
        """
        for line_no, line in enumerate(file_lines):
            for p in object_signatures:
                if line.strip().startswith(p):
                    obj = docobj(line)
                    obj.content_start = line_no + 1         # start of this object
                    if(len(objects) > 0):           
                        objects[-1].content_end = line_no -1 # end of previous object
                    objects.append(obj)
        if(len(objects)>1):
            objects[-1].content_end = len(file_lines) - 1         # end of last object in document

        # tell the object what its indent level is within the document
        indents =[0]
        for obj in objects:
            if(obj.indent_spaces > indents[-1]):
                indents.append(obj.indent_spaces)
            obj.indent_level = indents.index(obj.indent_spaces)
        
        # 'move' any docstring content in the signature into the content,
        # and remove the 'docstring ' tag
        # NEEDS another look - do this with deep copy move so it will be clearer
        for obj in objects:
            if(obj.object_type == 'docstring'):
                if(len(file_lines[obj.content_start]) >0):  # but don't introduce a blank line to the beginning
                    obj.content_start -= 1 
                obj.signature = obj.signature.split(" ")[0]
                file_lines[obj.content_start] = file_lines[obj.content_start].replace('docstring ','',1)

        # tell each object the line number of the next object
        for i, obj in enumerate(objects[:-1]):
            obj.nextobj_index = i + 1

        # add 'notes' icon to objects where next child is a docstring
        for i, obj in enumerate(objects[:-1]):
            nextobj = objects[obj.nextobj_index]
            if (nextobj.object_type == 'docstring' and nextobj.indent_level > obj.indent_level):
                obj.icon = '🧾' 

        return objects


def _ignore_docstrings_with(doc_objects, file_lines, pattern):
    for obj in doc_objects:
        if (not obj.object_type == 'docstring'):
            continue
        text = file_lines[obj.content_start: obj.content_end + 1]
        text = ''.join(text)
        if (pattern in text):
            print(f"  ..ignoring docstring at lines {obj.content_start} to {obj.content_end}")
            obj.object_type = 'ignore'
    return doc_objects

def _signature_html(obj_type, obj_signature, open_details = True):
    # write the signature of the object with a summary / details tag
    htm = "<details><summary>" if open_details else "<div>"
    htm += f"<span class ='{obj_type} {'signature'}'>{obj_signature}</span>"
    htm += "</summary>" if open_details else "</div>"
    return htm + "\n"

def _content_html(object_type, content_lines):
    # write 'content' inside <pre></pre>
    htm = f"<pre class ='{object_type} content'>"
    for i, line in enumerate(content_lines):
        if(i==0 and len(line.strip()) ==0):
            continue
#        htm += f"{i}:{len(line.strip())}: '{html.escape(line)}'"
        htm += f"{html.escape(line)}"
    htm += "</pre>\n"
    return htm

def _close_details(n_times):
    return "</details>\n" * n_times

def object_list_to_HTML(file_lines, doc_objects, documentation_mode):
    """
        converts list of doc_objects into HTML
    """
    doc_html = ""
    associate_docstring = False
    for i,obj in enumerate(doc_objects):
        if(obj.object_type == 'ignore'):
            continue
        if(documentation_mode == 'on'):    
            if(len(obj.signature.split(" "))>1): # ignore names starting with _ in doc mode
               if(obj.signature.split(" ")[1].startswith("_")):
                  continue
            sig_line = obj.signature.replace('def ','&nbsp&nbsp&nbsp').replace('(self)','()').replace('(self, ','(').replace('(self,','(')
            if(obj.object_type not in ['body','docstring']):
                doc_html += "<hr>"
                doc_html += _signature_html(obj.object_type, sig_line, open_details = False)
                associate_docstring = True
            if(obj.object_type == "docstring" and associate_docstring):
                associate_docstring = False # this is a workaround (pending using true object tree) to prevent multiple & sometimes non-local docstrings appearing
                doc_html += _content_html(obj.object_type, file_lines[obj.content_start : obj.content_end + 1])
        else:
            doc_html += _signature_html(obj.object_type, obj.icon + ' ' + obj.signature, open_details = True)
            doc_html += _content_html(obj.object_type, file_lines[obj.content_start : obj.content_end + 1])
            nextobj = doc_objects[obj.nextobj_index]
            doc_html += _close_details(obj.indent_level - nextobj.indent_level + 1)
    return doc_html
            
def main():
    from importlib.metadata import version
    try:
        __version__ = version("docu-lite")
    except:
        __version__ = ""
    soft_string = f"Docu-lite {__version__} by Alan Robinson: github.com/G1OJS/docu-lite/"
    print(f"{soft_string}\n")

    # get input params
    input_pattern, output_html_file, output_text_list_file, style_sheet_file, documentation_mode, ignore_docstrings_with = get_config_vars()

    # start the output html
    ensure_css_exists(style_sheet_file,documentation_mode)
    output_html =  f"<!DOCTYPE html><html lang='en'>\n<head>\n<title>{output_html_file}</title>"
    output_html += f"<link rel='stylesheet' href='./{style_sheet_file}' />"

    # start html body and loop through input files
    output_html += "<body>\n"
    print(f"Scanning for input files in {input_pattern}")
    n_files_processed = 0
    signatures = []
    for filepath in glob.glob(input_pattern):
        filename = os.path.basename(filepath)
        print(f"Found file: {filename}")
        with open(filepath,"r") as f:
            file_lines = f.readlines()
        if(len(file_lines) ==0):
            print(f"File: {filename} has no content - skipping")
            continue
        doc_objects = get_doc_objects(file_lines)
        if(ignore_docstrings_with != ''):
            doc_objects =  _ignore_docstrings_with(doc_objects, file_lines, ignore_docstrings_with)
        output_html += f"<br><div class = 'filename'>{filename}</div><br>"
        output_html += object_list_to_HTML(file_lines, doc_objects, documentation_mode)
        n_files_processed +=1

        # gather signatures for alphabetic list
        for obj in doc_objects:
            if((obj.signature == "docstring") or (obj.signature == "body")):
                continue
            signatures.append(obj.signature)
            
    # write footer
    output_html += f"\n<br><br><span style = 'font-size:0.8em;color:#666;border-top:1px solid #ddd; "
    output_html += f"font-style:italic'>Made with {soft_string}</span>"

    if (n_files_processed == 0):
        print(f"\nWarning: didn't process any files from {input_pattern}, please check the input path")

    # write alphabetic_list
    if(len(signatures)>1 and output_text_list_file !=''):
        signatures.sort()
        with open(output_text_list_file , "w") as f:
            for sig in signatures:
                f.write(f"{sig}\n")
        print(f"\nSignatures list written to {output_text_list_file}")


    # close html body and write the file
    output_html += "</body>\n"
    with open(output_html_file, "w", encoding="utf-8") as f:
        f.write(output_html)
    print(f"\nOutline written to {output_html_file}, linked to style sheet {style_sheet_file}")

if __name__ == "__main__":
    main()

