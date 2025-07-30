from __future__ import annotations
from typing import Any, Dict
import gradio as gr
from gradio.components.base import Component
from gradio.events import Dependency

class HTMLInjector(Component):
    """
    An invisible Gradio component to inject custom assets into the application.
    It can inject:
    - CSS styles and JavaScript code into the <head>.
    - HTML content into the end of the <body>.
    It is populated via the Blocks.load() event.
    """
    
    __name__ = "HTMLInjector"

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
        Receives the payload (a dictionary with 'js', 'css', and 'body_html' keys)
        from a backend function and passes it directly to the frontend component.
        """
        if value is None:
            return None
        return value

    def api_info(self) -> Dict[str, Any]:
        """
        Defines the API info for the component.
        """
        return {
            "type": "object", 
            "example": {
                "js": "console.log('Injected JS');", 
                "css": "body { font-family: sans-serif; }",
                "body_html": "<div id='popup'>Hello World</div>"
            }
        }

    def example_payload(self) -> Dict[str, str]:
        """
        Returns an example payload. This is crucial for Gradio to know the
        data structure of the component on initial page load. It should contain
        the keys but with empty values.
        """
        return {"js": "", "css": "", "body_html": ""}
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component