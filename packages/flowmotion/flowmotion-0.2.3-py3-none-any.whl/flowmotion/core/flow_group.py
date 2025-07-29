from manim import *

from .flow_motion import FlowMotion


class FlowGroup(FlowMotion, VGroup):
    """
    Group container for flowmotion objects with playback control.

    Inherits from FlowMotion and Manim's VGroup.
    """

    def __init__(self):
        """
        Initialize an empty FlowGroup.
        """
        FlowMotion.__init__(self)
        VGroup.__init__(self)

    def choose_text_type(self, value, **kwargs):
        """
        Render value using Tex for numbers or Text for strings.

        Args:
            value (Any): Value to display.
            kwargs: Additional rendering options.

        Returns:
            VMobject: Rendered text object.
        """
        if isinstance(value, (int, float)):
            return Tex(str(value), **kwargs)
        else:
            return Text(str(value), **kwargs).scale(0.7)

    def show(self, mute=False):
        """
        Show the group with or without animation.

        Args:
            mute (bool): If True, skips animation.

        Returns:
            tuple: FlowAction and visual object.
        """
        if mute:
            return (self.FlowAction.ADD, self)
        else:
            return (self.FlowAction.PLAY, Write(self))

    def hide(self, mute=False):
        """
        Hide the group with or without animation.

        Args:
            mute (bool): If True, skips animation.

        Returns:
            tuple: FlowAction and visual object.
        """
        if mute:
            return (self.FlowAction.ADD, self)
        else:
            return (self.FlowAction.PLAY, FadeOut(self))
