import io

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
)
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


class PdfSpecSheetService:
    def apply_highlights_to_pdf(
        self,
        pdf_bytes: bytes,
        regions: list[SpecSheetHighlightRegion],
    ) -> bytes:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()

        regions_by_page: dict[int, list[SpecSheetHighlightRegion]] = {}
        for region in regions:
            page_num = region.page_number
            if page_num not in regions_by_page:
                regions_by_page[page_num] = []
            regions_by_page[page_num].append(region)

        for page_index, page in enumerate(reader.pages):
            page_num = page_index + 1
            page_regions = regions_by_page.get(page_num, [])

            if page_regions:
                media_box = page.mediabox
                page_width = float(media_box.width)
                page_height = float(media_box.height)

                overlay_buffer = io.BytesIO()
                c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))

                for region in page_regions:
                    self._draw_highlight_region(c, region, page_width, page_height)

                c.save()
                _ = overlay_buffer.seek(0)

                overlay_reader = PdfReader(overlay_buffer)
                if overlay_reader.pages:
                    page.merge_page(overlay_reader.pages[0])

            _ = writer.add_page(page)

        output_buffer = io.BytesIO()
        _ = writer.write(output_buffer)
        return output_buffer.getvalue()

    def _draw_highlight_region(
        self,
        c: canvas.Canvas,
        region: SpecSheetHighlightRegion,
        page_width: float,
        page_height: float,
    ) -> None:
        x = (region.x / 100.0) * page_width
        y_from_top = (region.y / 100.0) * page_height
        width = (region.width / 100.0) * page_width
        height = (region.height / 100.0) * page_height

        y = page_height - y_from_top - height

        hex_color = region.color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        c.setStrokeColorRGB(r, g, b)
        c.setFillColorRGB(r, g, b, alpha=0.3)
        c.setLineWidth(2)

        if region.shape_type == "oval":
            c.ellipse(x, y, x + width, y + height, stroke=1, fill=1)
        else:
            c.rect(x, y, width, height, stroke=1, fill=1)
