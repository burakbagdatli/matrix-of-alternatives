from typing import Dict, List, get_type_hints
from bokeh.layouts import layout
from bokeh.models.widgets import Toggle, Paragraph, RangeSlider
from bokeh.plotting import curdoc


class BasicCategory:
    number: int
    name: str
    gui_name: str
    choices: List[str]

    def __init__(self, number: int, name: str, gui_name: str,
                 choices: List[str]):
        self.number = number
        self.name = name
        self.gui_name = gui_name
        self.choices = choices
        self.text = Paragraph(text=self.gui_name, width=150)


class BasicChoice:
    number: int
    name: str
    gui_name: str
    options: List[str]

    def __init__(self, number: int, name: str, gui_name: str,
                 options: List[str]):
        self.number = number
        self.name = name
        self.gui_name = gui_name
        self.options = options
        self.text = Paragraph(text=self.gui_name, width=150)
        self.make_children_incompatible()

    def make_children_incompatible(self):
        """ Makes all options under the choice strictly incompatible with
            each other."""
        for _, child in self.options.items():
            for _, opt in self.options.items():
                if opt != child:
                    child.incompatibilities.append(opt)


class BasicOption:
    """ Basic option class. If you need to add further attributes to your
    options, create your class and inherit from this. """
    number: int
    name: str
    gui_name: str
    selected: bool
    incompatibilities: List[str]

    def __init__(self, number: int, name: str, gui_name: str = "",
                 selected: bool = False, incompatibilities: List[str] = []):
        self.number = number
        self.name = name
        self.gui_name = gui_name if gui_name else name
        self.selected = selected
        self.incompatibilities = incompatibilities
        self.incompatibility_count = 0
        self.button = Toggle(label=self.gui_name, width=200, button_type="primary")
        self.button.on_click(self.button_function)

    def button_function(self, state):
        """ Disables incompatible options. """
        if state:  # styling
            self.button.button_type = "success"
        else:
            self.button.button_type = "primary"
        for incomp_opt in self.incompatibilities:  # incompatibility logic
            if state:
                incomp_opt.incompatibility_count += 1
                incomp_opt.button.disabled = True
            else:
                incomp_opt.incompatibility_count -= 1
                if incomp_opt.incompatibility_count == 0:
                    incomp_opt.button.disabled = False


class BasicFilter:
    number: int
    name: str
    gui_name: str
    full_range: List[int]
    step: int
    options: List

    def __init__(self, number:int, name: str, gui_name: str = "",
                 full_range: List[int] = [0, 1], step: int = 1,
                 options: List = []):
        self.number = number
        self.name = name
        self.gui_name = gui_name if gui_name else name
        self.full_range = full_range
        self.step = step
        self.options = options
        self.slider = RangeSlider(title=gui_name, start=full_range[0],
                                  end=full_range[1], step=step,
                                  value=full_range)
        self.slider.on_change("value", self.slider_function)

    def slider_function(self, attr, old, new):
        for opt in self.options:
            opt_limit = getattr(opt, self.name)
            if opt_limit["incompatible"]:
                if new[0] <= opt_limit["limit"] <= new[1]:
                    opt_limit["incompatible"] = False
                    opt.incompatibility_count -= 1
                    if opt.incompatibility_count == 0:
                        opt.button.disabled = False
            else:
                if not (new[0] <= opt_limit["limit"] <= new[1]):
                    opt_limit["incompatible"] = True
                    opt.incompatibility_count += 1
                    opt.button.disabled = True


class BasicReader:
    """ This is a shell that initializes what is needed at a minimum from the
    input files. Depending on the real input files, specialize this reader """
    def __init__(self, cat_file, chs_file, opt_file, flt_file):
        self.files = {"Categories": cat_file, "Choices": chs_file,
                      "Options": opt_file, "Filters": flt_file}
        self.options = {}
        self.choices = {}
        self.categories = {}
        self.filters = {}


class BasicMatrixOfAlternatives:
    def __init__(self, reader):
        self.reader = reader
        self.options = reader.options
        self.choices = reader.choices
        self.categories = reader.categories
        self.filters = reader.filters
        self.matrix = None
        self.create_layout()

    def create_layout(self):
        moa_layout = []
        cat_row = -1
        for _, category in self.categories.items():
            cat_row += 1
            chs_row = -1
            moa_layout.append([category.text, []])
            choices = category.choices
            for _, choice in choices.items():
                chs_row += 1
                moa_layout[cat_row][1].append([choice.text])
                options = choice.options
                for _, option in options.items():
                    moa_layout[cat_row][1][chs_row].append(option.button)
        for _, moa_filter in self.filters.items():
            moa_layout.append(moa_filter.slider)
        self.matrix = layout(moa_layout)


class BasicInterface:
    def __init__(self, moa):
        self.doc = curdoc()
        self.doc.add_root(moa)
