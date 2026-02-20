# utils.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os
import aiofiles
async def generate_diploma(user_name, language='ru'):
    """Генерирует PDF-диплом"""
    filename = f"diploma_{user_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = f"temp/{filename}"
    
    # Создаем папку temp, если её нет
    os.makedirs('temp', exist_ok=True)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Фон (можно добавить изображение старой бумаги)
    c.setFillColorRGB(0.96, 0.93, 0.86)  # цвет старой бумаги
    c.rect(0, 0, width, height, fill=True)
    
    # Рамка
    c.setStrokeColorRGB(0.6, 0.4, 0.2)
    c.setLineWidth(5)
    c.rect(50, 50, width-100, height-100)
    
    # Заголовок
    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0.4, 0.2, 0.0)
    if language == 'ru':
        c.drawString(150, height-150, "ДИПЛОМ")
        c.drawString(120, height-200, "ОХОТНИКА ЗА СОКРОВИЩАМИ")
    else:
        c.drawString(150, height-150, "DIPLOMA")
        c.drawString(100, height-200, "TREASURE HUNTER")
    
    # Имя
    c.setFont("Helvetica", 28)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(200, height-300, user_name)
    
    # Текст
    c.setFont("Helvetica", 16)
    if language == 'ru':
        text = [
            "Нашёл сокровища капитана Джона Тейлора",
            f"на острове Мадейра {datetime.now().strftime('%d.%m.%Y')}",
            "",
            "Капитан Тейлор завещал:",
            "\"Ты доказал, что достоин быть пиратом.",
            "Пусть ветер всегда дует тебе в спину!\""
        ]
    else:
        text = [
            "Found the treasure of Captain John Taylor",
            f"on Madeira Island {datetime.now().strftime('%d.%m.%Y')}",
            "",
            "Captain Taylor bequeathed:",
            "\"You proved worthy of being a pirate.",
            "May the wind always be at your back!\""
        ]
    
    y = height-380
    for line in text:
        c.drawString(100, y, line)
        y -= 30
    
    # Подпись
    c.setFont("Helvetica-Oblique", 14)
    c.drawString(100, 150, "Captain John Taylor")
    c.drawString(400, 150, "_______")
    
    # Печать
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, 120, "Treasure Hunt Madeira")
    
    c.save()
    return filepath