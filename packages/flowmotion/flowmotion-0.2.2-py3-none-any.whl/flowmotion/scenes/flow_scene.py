from manim import *
from ..core.flow_motion import FlowMotion


class FlowScene(FlowMotion, Scene):
    """
    Custom scene with a ribbon header, hamburger icon, and title support.
    """

    def __init__(self, **kwargs):
        # Configure global settings
        config.background_color = "#181818"
        config.pixel_width = 1920
        config.pixel_height = 1080
        config.verbosity = "ERROR"
        config.progress_bar = "none"

        FlowMotion.__init__(self)
        Scene.__init__(self, **kwargs)

    def init_terminal_theme(
        self, title="Default Terminal Title", direction=LEFT, font="JetBrains Mono"
    ):
        bar_color = "#121212"
        bar = Rectangle(
            width=config.frame_width, height=0.5, color=bar_color, fill_opacity=1
        )
        bar.shift(UP * (config.frame_height - bar.height) / 2)

        ctrl_button_colors = ["#FF5F56", "#FFBD2E", "#27C93F"]  # Red, Yellow, Green
        buttons = VGroup()

        for button_color in ctrl_button_colors:
            circle = Circle(radius=0.06, color=button_color, fill_opacity=1)
            buttons.add(circle)

        buttons.arrange(-direction, buff=0.175)
        buttons.move_to(
            bar.get_edge_center(direction) - direction * buttons.width * 0.8
        )

        title_text = Text(rf"{title.upper()}", font=font, color="#DFDCD3")
        title_text.move_to(bar).scale_to_fit_height(0.125)

        terminal_group = VGroup(bar, buttons, title_text)
        return (self.FlowAction.ADD, terminal_group)

    def create_intro(self):
        lines = [
            "> Initializing system memory... OK",
            "> Loading SenanOS v0.1.12... Done",
            "> Mounting workspace: /home/senan/youtube... OK",
            "> Launching Production Shell...",
            "> Welcome back, senan",
            "> _",
        ]
        group = VGroup()
        for line in lines:
            text_obj = Text(
                line,
                color=GREEN,
                font="JetBrains Mono",
                font_size=18,
            )
            group.add(text_obj)

        group.arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UL).shift(
            DOWN * 0.325
        )
        anim = [AddTextLetterByLetter(mobj, time_per_char=0.01) for mobj in group]
        return (self.FlowAction.PLAY, Succession(*anim))

    def flow(self, *args, **kwargs):
        """
        Accepts tuples of (Action, target) and performs the appropriate behavior.

        - (SKIP, _) => skips
        - (PLAY, Animation) => self.play()
        - (ADD, Mobject) => self.add()
        - (REMOVE, Mobject) => self.remove()
        """
        for item in args:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError(
                    f"Each item must be a (Action, target) tuple, got: {item}"
                )

            action, target = item

            # Handle SKIP
            if action == self.FlowAction.SKIP:
                continue

            # PLAY: animation
            elif action == self.FlowAction.PLAY:
                if not isinstance(target, Animation):
                    raise TypeError(f"Expected Animation for PLAY, got {type(target)}")
                self.play(target, **kwargs)

            # ADD: mobject
            elif action == self.FlowAction.ADD:
                self.add(target)

            # REMOVE: mobject
            elif action == self.FlowAction.REMOVE:
                self.remove(target)

            else:
                raise ValueError(f"Unknown action: {action}")
