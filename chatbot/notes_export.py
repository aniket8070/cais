"""
CAIS - Notes PDF Export Utility
chatbot/notes_export.py म्हणून save करा
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ─── Styles ───────────────────────────────────────────────────────────────────

def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CAISTitle',
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=4,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='CAISSubtitle',
        fontSize=11,
        fontName='Helvetica',
        textColor=colors.HexColor('#555555'),
        spaceAfter=2,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='SectorHeading',
        fontSize=15,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        spaceAfter=6,
        spaceBefore=10,
        leftIndent=6,
    ))
    styles.add(ParagraphStyle(
        name='SubHeading',
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=4,
        spaceBefore=8,
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#222222'),
        spaceAfter=3,
        leading=15,
    ))
    styles.add(ParagraphStyle(
        name='BulletText',
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#333333'),
        spaceAfter=2,
        leftIndent=14,
        bulletIndent=4,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER,
    ))
    return styles


SECTOR_COLORS = {
    'Polity & Governance':        '#1565C0',
    'Economy & Finance':          '#2E7D32',
    'International Relations':    '#6A1B9A',
    'Environment & Ecology':      '#00695C',
    'Science & Technology':       '#E65100',
    'Health & Social Issues':     '#C62828',
    'Defence & Security':         '#37474F',
    'Geography & Disaster Mgmt':  '#4E342E',
    'Art, Culture & Heritage':    '#AD1457',
    'Education & Sports':         '#00838F',
}


# ─── Helper: parse markdown-style notes ───────────────────────────────────────

def _parse_notes_to_elements(notes_text: str, styles) -> list:
    """Convert AI-generated markdown notes into ReportLab flowables."""
    elements = []

    for line in notes_text.split('\n'):
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 3))
            continue

        # ### Sub-heading
        if line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, styles['SubHeading']))

        # ## Section heading (treat as sub-heading)
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, styles['SubHeading']))

        # Bullet points: - or *
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Bold markers **text**
            text = text.replace('**', '<b>', 1).replace('**', '</b>', 1)
            elements.append(Paragraph(f'• {text}', styles['BulletText']))

        # Numbered list
        elif len(line) > 2 and line[0].isdigit() and line[1] in '.):':
            text = line[2:].strip()
            text = text.replace('**', '<b>', 1).replace('**', '</b>', 1)
            elements.append(Paragraph(f'{line[0]}. {text}', styles['BulletText']))

        # Normal paragraph
        else:
            text = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
            elements.append(Paragraph(text, styles['BodyText2']))

    return elements


# ─── Main export function ──────────────────────────────────────────────────────

def generate_notes_pdf(
    sector_notes: dict,          # {'Polity & Governance': 'notes text...', ...}
    newspaper_date: str = None,  # e.g. '16 March 2026'
    newspaper_name: str = 'Indian Express',
) -> bytes:
    """
    Generate a well-formatted PDF from sector notes.

    Args:
        sector_notes: dict of {sector_name: notes_text}
        newspaper_date: date string for the header
        newspaper_name: newspaper source name

    Returns:
        PDF as bytes (ready to send as HttpResponse)

    Usage in views.py:
        from chatbot.notes_export import generate_notes_pdf

        pdf_bytes = generate_notes_pdf(
            sector_notes=request.session.get('sector_notes', {}),
            newspaper_date=request.session.get('newspaper_date', ''),
        )
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="CAIS_Notes.pdf"'
        return response
    """

    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=18*mm,
        bottomMargin=18*mm,
        title='CAIS Current Affairs Notes',
        author='CAIS - Current Affairs Intelligence System',
    )

    story = []
    date_str = newspaper_date or datetime.now().strftime('%d %B %Y')

    # ── Cover Header ──
    story.append(Spacer(1, 10))
    story.append(Paragraph('CAIS', styles['CAISTitle']))
    story.append(Paragraph('Current Affairs Intelligence System', styles['CAISSubtitle']))
    story.append(Paragraph(f'{newspaper_name}  •  {date_str}', styles['CAISSubtitle']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(
        width='100%', thickness=2,
        color=colors.HexColor('#1a237e'), spaceAfter=10
    ))

    # ── Exam Banner ──
    exam_data = [['UPSC / MPSC', 'SSC / Railway', 'Banking (IBPS/SBI)', 'Defence (NDA/CDS)']]
    exam_table = Table(exam_data, colWidths=[42*mm, 42*mm, 50*mm, 42*mm])
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8EAF6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#E8EAF6')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9FA8DA')),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(exam_table)
    story.append(Spacer(1, 14))

    # ── Table of Contents ──
    story.append(Paragraph('📋 Sectors Covered', styles['SubHeading']))
    sectors_list = list(sector_notes.keys())
    toc_data = [[f'{i+1}. {s}' for i, s in enumerate(sectors_list[j:j+2])]
                for j in range(0, len(sectors_list), 2)]
    if toc_data:
        toc_table = Table(toc_data, colWidths=[85*mm, 85*mm])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(toc_table)

    story.append(PageBreak())

    # ── Sector Pages ──
    for sector_name, notes_text in sector_notes.items():
        if not notes_text or not notes_text.strip():
            continue

        # Colored sector header bar
        color_hex = SECTOR_COLORS.get(sector_name, '#37474F')
        header_data = [[Paragraph(f'  {sector_name}', styles['SectorHeading'])]]
        header_table = Table(header_data, colWidths=[174*mm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(color_hex)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 6))

        # Notes content
        note_elements = _parse_notes_to_elements(notes_text, styles)
        story.extend(note_elements)

        story.append(Spacer(1, 6))
        story.append(HRFlowable(
            width='100%', thickness=0.5,
            color=colors.HexColor('#CCCCCC'), spaceAfter=6
        ))
        story.append(PageBreak())

    # ── Footer on last content ──
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f'Generated by CAIS • {datetime.now().strftime("%d %B %Y, %I:%M %p")}',
        styles['Footer']
    ))
    story.append(Paragraph(
        'For UPSC • MPSC • SSC • Banking • Railway • Defence preparation',
        styles['Footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()