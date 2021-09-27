from __future__ import annotations


from typing import Iterable, Optional, Tuple, List

# from .db import NexusFile


class NexusPage:
    owner: 'nexus.file.NexusFile'
    styles: List[NexusStyle]
    blocks: List[NexusBlock]

    def __init__(self, owner):
        self.owner = owner
        self.styles = []
        self.blocks = []
    
    def __getitem__(self, name) -> str:
        raise NotImplementedError()
    
    def __setitem__(self, name, value) -> None:
        raise NotImplementedError()
    
    def getProperties(serf) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError()
    
    def getPropertyHistory(self, name: str) -> Iterable[str]:
        raise NotImplementedError()
    
    def getBlocks(self) -> Iterable[NexusBlock]:
        raise NotImplementedError()
    
    def createBlock(self) -> NexusBlock:
        raise NotImplementedError()
    
    def getBlock(self, index: int) -> NexusBlock:
        raise NotImplementedError()
    
    def createStyle(self, **kwargs):
        styleId = len(self.styles) + 1
        style = NexusStyle(styleId)
        for key in kwargs:
            setattr(style, key, kwargs[key])
        self.styles += [style]
        return style
    
    def createBlock(self):
        block = NexusBlock(self)
        self.blocks += [block]
        return block
    
    def render(self):
        html = ""
        html += "<head><style>"
        for style in self.styles:
            html += style.cssRule()
        html += "</style></head>"
        for block in self.blocks:
            html += block.render()
        return html

class NexusBlock:
    owner: NexusPage
    textItems: Iterable[NexusText]

    def __init__(self, page) -> None:
        self.page = page
        self.textItems = []
    
    def createText(self, text, style):
        text = NexusText(self, text)
        text.style = style
        self.textItems += [text]
        return text
    
    def render(self):
        html = "<p>"
        for text in self.textItems:
            html += text.render()
        html += "</p>"
        return html


class NexusText:
    owner: NexusBlock
    text: str
    style: NexusStyle

    def __init__(self, block, text, **styles):
        self.text = text
        self.style = block.page.createStyle(**styles)
    
    def render(self):
        return self.style.wrap(self.text)


class NexusStyle:
    page: NexusPage

    fontSize: int = 12
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    foreground: str = "black"
    background: str = ""
    bullet: bool = False
    bulletNumber: Optional[int] = None

    def __init__(self, styleId, **kwargs):
        self.styleId = styleId
        for key in kwargs:
            setattr(self, key, kwargs[key])
    
    def wrap(self, text):
        return f"<span class=nexus-{self.styleId}>{text}</span>"
    
    def cssRule(self):
        rule = f".nexus-{self.styleId}{{"
        if self.bold:
            rule += "font-weight: bold;"
        if self.italic:
            rule += "font-style: italic;"
        if self.underline:
            rule += "text-decoration: underline;"
        if self.foreground:
            rule += f"color: {self.foreground}"
        if self.background:
            rule += f"color: {self.background}"
        # TODO: Handle strike through and bullets
        rule += "}"
        return rule
