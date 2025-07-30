
import gradio as gr
from app import demo as app
import os

_docs = {'HeadInjector': {'description': "An invisible Gradio component to inject custom CSS styles and JavaScript code\ninto the <head> of the application's HTML document. It is populated\nvia the Blocks.load() event.", 'members': {'__init__': {}, 'postprocess': {'value': {'type': 'typing.Optional[typing.Dict[str, str]][\n    typing.Dict[str, str][str, str], None\n]', 'description': None}}, 'preprocess': {'return': {'type': 'Any', 'description': None}, 'value': None}}, 'events': {}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'HeadInjector': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_headinjector`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_headinjector/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_headinjector"></a>  
</div>

A head injector for css and js
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_headinjector
```

## Usage

```python
import gradio as gr
from gradio_headinjector import HeadInjector

def inject_assets():
    \"\"\"
    This function prepares the payload of CSS and JS code. It's called by the
    demo.load() event listener when the Gradio app starts.
    \"\"\"
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
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `HeadInjector`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["HeadInjector"]["members"]["__init__"], linkify=[])




    gr.Markdown("""

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
""", elem_classes=["md-custom", "HeadInjector-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          HeadInjector: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
