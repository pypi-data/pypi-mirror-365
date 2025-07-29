from dataclasses import dataclass
from typing import Any

from docx import Document
from docx.shared import Pt, Inches

from py_docx_creator.AbstractClasses import DocumentStyles, FontNames
from py_docx_creator.CoreClasses import CoreDocumentStyle, CorePageStyle, \
    CoreTextStyle, CoreDocumentWriter, AlignParagraph, CoreParagraphStyle, CoreStyleManager


class NormalDocumentStyle(CoreDocumentStyle):
    """Стандартный стиль документа"""

    def __init__(self):
        super().__init__()
        self.document_style = DocumentStyles.Normal.value


@dataclass
class MainPageStyle(CorePageStyle):
    """Основной формат страницы"""
    top_margin: Pt | None = Pt(15)
    bottom_margin: Pt | None = Pt(10)
    left_margin: Pt | None = Pt(75)
    right_margin: Pt | None = Pt(75)


@dataclass
class MainParagraphStyle(CoreParagraphStyle):
    """Стиль основного текста"""
    alignment: AlignParagraph | None = AlignParagraph.JUSTIFY.value
    space_after: Pt | None = Pt(0)
    left_indent: Inches | None = Inches(-0.5)
    right_indent: Inches | None = Inches(-0.5)
    line_spacing: float | None = 1.15
    first_line_indent: Pt | None = 20


@dataclass
class HeaderParagraphStyle(CoreParagraphStyle):
    """Стиль для заголовков """
    alignment: AlignParagraph = AlignParagraph.CENTER.value
    left_indent: Inches = Inches(-0.5)
    right_indent: Inches = Inches(-0.5)


class MainDocumentWriter(CoreDocumentWriter):
    def __init__(self):
        super().__init__()


@dataclass
class MainTextStyle(CoreTextStyle):
    """Основной стиль текста"""
    size: Pt = Pt(10)
    name: str = FontNames.TimesNewRoman.value
    bold: bool = False


@dataclass
class HeaderTextStyle(CoreTextStyle):
    size: Pt = Pt(12)
    name: str = FontNames.TimesNewRoman.value
    bold = True


class FastWriter(CoreDocumentWriter):
    """Класс для быстрой записи в документ"""

    @classmethod
    def write(cls, document: Document, text: str, paragraph_style: CoreParagraphStyle, text_style: CoreTextStyle,
              size: int = None, bold: bool = None, italic: bool = None, underline: bool = None,
              space_after: int = None) -> None:
        """
        Метод записи в документ
        Аргументы:

            document: Document - документ для записи

            text: str - записываемый текст

            paragraph_style: CoreParagraphStyle - стиль параграфа

            text_style: CoreTextStyle - стиль текста

        Опциональные аргументы:

            Нижеперечисленные аргументы используются для быстрого изменения основных настроек стиля
            без необходимости прописывать отдельный dataclass

            size: int

            bold: bool

            italic: bool

            underline: bool

            space_after: int

        """
        if size:
            text_style.size = Pt(size)
        if bold:
            text_style.bold = bold
        if italic:
            text_style.italic = italic
        if underline:
            text_style.underline = underline
        if space_after:
            paragraph_style.space_before = Pt(space_after)

        paragraph = cls.add_paragraph_to_document(document)
        CoreStyleManager.PARAGRAPH_STYLE_MANAGER.apply_style(paragraph, paragraph_style)
        run = cls.add_run_to_paragraph(paragraph, text)
        CoreStyleManager.TEXT_STYLE_MANAGER.apply_style(run, text_style)
