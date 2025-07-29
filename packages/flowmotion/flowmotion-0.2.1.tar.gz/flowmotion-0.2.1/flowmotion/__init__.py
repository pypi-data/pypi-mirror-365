from .core import FlowGroup, FlowPointer
from .blocks import FlowBlock, FlowCode, FlowText
from .structs import FlowArray, FlowStack
from .scenes import FlowScene

__all__ = [
    "FlowGroup",
    "FlowArray",
    "FlowStack",
    "FlowPointer",
    "FlowScene",
    # Content Blocks
    "FlowBlock",
    "FlowCode",
    "FlowText",
]

__version__ = "0.2.1"
print(f"FlowMotion v{__version__}\n")
