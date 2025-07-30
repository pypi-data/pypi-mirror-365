---
tags: [gradio-custom-component, ]
title: gradio_headinjector
short_description: A Head injector for css and js
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_headinjector`
<a href="https://pypi.org/project/gradio_headinjector/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_headinjector"></a>  

A head injector for css and js

## Installation

```bash
pip install gradio_headinjector
```

## Usage

```python
import gradio as gr
from gradio_headinjector import HeadInjector

def inject_assets():
    """
    This function prepares the payload of CSS and JS code. It's called by the
    demo.load() event listener when the Gradio app starts.
    """
    # Inline code
    css_code = "body { background-color: #f0f5ff !important; }"
    js_code = "console.log('Hello from an inline JS string!');"

    # Read from files
    try:
        with open("test.css", "r", encoding="utf-8") as f:
            css_code += f.read() + "\n"
        with open("test.js", "r", encoding="utf-8") as f:
            js_code += f.read() + "\n"
    except FileNotFoundError as e:
        print(f"Warning: Could not read asset file: {e}")

    return {"js": js_code, "css": css_code}


with gr.Blocks() as demo:
    gr.Markdown("# Application with HeadInjector")
    gr.Markdown("If the background is light blue and the buttons trigger an alert, it worked!")
    
    # 1. Instantiate the component. It is empty at this point.
    head_injector = HeadInjector()
    
    with gr.Row():
        gr.Button("Button 1")
        gr.Button("Button 2")

    gr.Textbox(label="Check your browser's developer console (F12) for JS messages.")

    # 2. Use the `demo.load()` event to populate the component.
    # This is the reliable pattern: `demo.load` runs the `inject_assets` function
    # and sends its return value to the `head_injector` component.
    demo.load(fn=inject_assets, inputs=None, outputs=[head_injector])


# Launch the application
if __name__ == '__main__':
    demo.launch()
```

## `HeadInjector`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody></tbody></table>




### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
 def predict(
     value: Any
 ) -> typing.Optional[typing.Dict[str, str]][
    typing.Dict[str, str][str, str], None
]:
     return value
 ```
 
