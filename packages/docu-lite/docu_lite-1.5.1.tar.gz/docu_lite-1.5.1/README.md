# 🧾 docu-lite [![PyPI Downloads](https://static.pepy.tech/badge/docu-lite)](https://pepy.tech/projects/docu-lite)

### ⚡ Ultra-light Zero-dependency HTML outline generator for Python.   



- 📖   Browse classes and functions with collapsible docstrings in a tidy, readable format 
- 📘   Specify your own stylesheet(s) or rely on the default (will be generated on run) 
- 🎈   No dependencies, short script
- ⚙️   [Integrate into your GitHub Workflow](https://g1ojs.github.io/docu-lite/add-to-workflow/index.html) to have automatically up-to-date outline(s) in your repo
- 🛠️  Includes a text list of classes and functions useful for creating a delta view of API changes (e.g. using GitHub's compare)
- 👀   [Example live output:](https://g1ojs.github.io/docu-lite/docu-lite-outline.html)
- 👀   [Example live output (documentation mode):](https://g1ojs.github.io/docu-lite/docu-lite-outline-docmode.html)
  
## Screenshots

|User-facing  | Browsable outline | Text file (e.g. for API delta) |
|--------------|-------------------|-------------------------|
|![docu-lite user](https://github.com/user-attachments/assets/3735ad93-4f1e-4c47-a0c8-67e4e6c1bed8)| ![docu-lite browse](https://github.com/user-attachments/assets/a12df5d7-9c04-4c32-856b-81c6e317de25)|![docu-lite text list](https://github.com/user-attachments/assets/d9f39a76-e724-4dd2-8dca-7aace3a99d13)|

## 🛠 Installation

Install using pip: open a command window and type

```
pip install docu-lite
```
## 💡 Usage
Either edit and run docu-lite.py in an IDE, or run from the command line:
```
docu-lite                         # uses or creates docu-lite.ini
docu-lite --config alt.ini        # uses alt.ini, errors if missing
```
Docu-lite will create a docu-lite.ini file if one doesn't exist.

⚙️ Edit the docu-lite.ini file to control how docu-lite runs:
 - **pattern** specifies where to look for input
 - **html** specifies the name of the output html file
 - **css** specifies the name of the input style sheet, which will be referenced from the output html file
 - **text_file** specifies the name of the text results file (text_file =) prevents text file creation
 - **documentation_mode** produces a less detailed output styled for use as or editing into documentation. 
     - ignores code blocks starting with _ (e.g. def _name)
     - hides 'self' in function argument lists
     - provides inner content only for docstrings, not code
     - style sheet dedicated to this mode can be specified in the ini file
 - **ignore_docstrings_with** can be followed by = word to ignore docstrings containing the word (e.g. License, useful to stop license blocks appearing in the output)  


📝 If the specified css file is not found, docu-lite will generate one and reference it in the html

## ⚠️ Known Issues
 - Doesn't cleanly handle all variations of docstring layout. In particular, the single line docstring causes the body below the docstring to appear below it.
 - Doesn't cleanly handle function definitions that span several lines (only first line is shown)

[PyPI link](https://pypi.org/project/docu-lite/)
