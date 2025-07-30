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