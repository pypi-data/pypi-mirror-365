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

        self.ribbon = None
        self.ribbon_color = "#121212"
        self.hamburger = None
        self.title = None

        self.colors = {"RED": "#FF5F56", "YELLOW": "#FFBD2E", "GREEN": "#27C93F"}

        self.ribbon = self.add_ribbon()
        self.hamburger = self.add_hamburger()

    def add_ribbon(self):
        """
        Create and add the top ribbon bar.
        """
        width = config.frame_width
        ribbon = Rectangle(
            width=width, height=0.5, color=self.ribbon_color, fill_opacity=1
        )
        ribbon.shift(UP * (config.frame_height / 2 - ribbon.height / 2))
        self.add(ribbon)
        return ribbon

    def add_hamburger(self):
        """
        Create and add colored control dots (like a Mac window).
        """
        group = VGroup()
        for _, color in self.colors.items():
            circle = Circle(radius=0.06, color=color, fill_opacity=1)
            group.add(circle)

        group.arrange(RIGHT, buff=0.175)
        group.to_corner(UL, buff=0.2).shift(RIGHT * 0.1)
        self.add(group)
        return group

    def add_title(
        self, title="Sample Video Preview Title", custom_font="JetBrains Mono"
    ):
        """
        Add a title to the ribbon.

        Args:
            title (str): Title text.
            custom_font (str): Font to use (default: JetBrains Mono).
        """
        if self.ribbon:
            title_text = Text(rf"{title.upper()}", font=custom_font, color="#DFDCD3")
            title_text.move_to(self.ribbon).scale_to_fit_height(0.125)
            self.title = title_text
            self.add(self.title)

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
