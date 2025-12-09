from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import datetime
from django.http import HttpResponse
import io

class WordExporter:
    @staticmethod
    def export_to_word(data, title, headers, fields):
        doc = Document()
        
        title_paragraph = doc.add_heading(title, 0)
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        date_paragraph = doc.add_paragraph(f'Дата создания: {datetime.now().strftime("%d.%m.%Y %H:%M")}')
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  
        
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        header_cells = table.rows[0].cells
        for i, header in enumerate(headers):
            cell = header_cells[i]
            cell.text = header
            # Форматируем заголовки
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(11)

        for item in data:
            row_cells = table.add_row().cells
            for i, field in enumerate(fields):
                #  связанные поля 
                if '__' in field:
                    # Разбиваем путь к полю
                    field_parts = field.split('__')
                    value = item
                    for part in field_parts:
                        if hasattr(value, part):
                            value = getattr(value, part)
                        else:
                            value = None
                            break
                else:
                    value = getattr(item, field, '')
                
                # Если это форинкей, получаем строковое представление
                if hasattr(value, '__str__'):
                    value = str(value)
                row_cells[i].text = str(value) if value is not None else ''
        
        doc.add_paragraph()
        total_paragraph = doc.add_paragraph(f'Всего записей: {len(data)}')
        total_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        return doc
    
    @staticmethod
    def create_http_response(doc, filename):
        # Сохраняем документ в поток байтов
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        response = HttpResponse(
            file_stream.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response