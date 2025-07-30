from __future__ import annotations
from typing import Any, Dict
import gradio as gr
from gradio.components.base import Component
from gradio.events import Dependency

class HeadInjector(Component):
    """
    An invisible Gradio component to inject custom CSS styles and JavaScript code
    into the <head> of the application's HTML document. It is populated
    via the Blocks.load() event.
    """
    
    # The name of the component, used by the frontend to find the Svelte implementation.
    # Gradio converts PascalCase (HeadInjector) to kebab-case (head-injector).
    __name__ = "HeadInjector"

    def __init__(self, **kwargs):
        """
        Initializes the component. It's a simple, invisible component.
        Data is passed to it later via an event listener (e.g., demo.load).
        """
        super().__init__(visible=False, **kwargs)

    def preprocess(self, payload: Any) -> Any:
        """
        This component does not process any input from the frontend, so this method is a no-op.
        """
        return payload

    def postprocess(self, value: Dict[str, str] | None) -> Dict[str, str] | None:
        """
        Receives the payload (a dictionary with 'js' and 'css' keys) from a
        backend function and passes it directly to the frontend component.
        """
        if value is None:
            return None
        return value

    def api_info(self) -> Dict[str, Any]:
        """
        Defines the API info for the component.
        """
        return {"type": "object", "example": {"js": "console.log(1)", "css": "body {color: red}"}}

    def example_payload(self) -> Dict[str, str]:
        """
        Returns an example payload. This is crucial for Gradio to know the
        data structure of the component on initial page load, before any
        events are fired.
        """
        return {"js": "console.log(1)", "css": "body {color: red}"}
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component