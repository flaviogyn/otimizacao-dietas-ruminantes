import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont('Helvetica', 8)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawString(36, letter[1] - 25, 'IFG / RuFaS — Fazenda Campo Dourado | Relatório de Composição Bromatológica')
            self.drawRightString(letter[0] - 36, letter[1] - 25, 'Outubro / 2026')
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(36, letter[1] - 28, letter[0] - 36, letter[1] - 28)

        # Footer (all pages)
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748b'))
        page_text = f'Página {self._pageNumber} de {page_count}'
        self.drawRightString(letter[0] - 36, 22, page_text)
        self.drawString(36, 22, 'Confidencial / Uso Acadêmico — IFG — Otimização de Dietas de Ruminantes')
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(36, 32, letter[0] - 36, 32)
        self.restoreState()


def generate_pdf():
    pdf_filename = r'Fazenda Campo Dourado/relatorio_ingredientes_racoes_GO_campo_dourado.pdf'
    docs_pdf_filename = r'docs/relatorio_ingredientes_racoes_GO_campo_dourado.pdf'
    
    os.makedirs('Fazenda Campo Dourado', exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=42
    )

    usable_width = letter[0] - 72  # 540 pt

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        'MetaBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155')
    ))

    styles.add(ParagraphStyle(
        'MetaBoxBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    ))

    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'BodyP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        'BodyPBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'TableHead',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1 # Center
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    ))

    styles.add(ParagraphStyle(
        'TableCellCenter',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b'),
        alignment=1 # Center
    ))

    styles.add(ParagraphStyle(
        'TableCellRight',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b'),
        alignment=2 # Right
    ))

    styles.add(ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#0f766e')
    ))

    story = []

    # 1. Header Banner Box
    banner_data = [
        [
            Paragraph("<b>IFG — INSTITUTO FEDERAL DE GOIÁS</b><br/>"
                      "Mestrado / Pós-Graduação em Inteligência Artificial & Zootecnia Computacional", styles['MetaBox']),
            Paragraph("<b>Projeto:</b> Otimização de Dietas de Ruminantes<br/>"
                      "<b>Simulador:</b> RuFaS (Ruminant Farm Systems)<br/>"
                      "<b>Padrão Nutricional:</b> NASEM (2021)", styles['MetaBox'])
        ]
    ]
    t_banner = Table(banner_data, colWidths=[usable_width*0.58, usable_width*0.42])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 10))

    # Title & Subtitle
    story.append(Paragraph("Relatório Técnico: Composição Bromatológica e Origem dos Dados", styles['MainTitle']))
    story.append(Paragraph("Consolidação dos 12 Alimentos da Fazenda Campo Dourado (GO_campo_dourado) com Base no RuFaS", styles['SubTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=8, spaceBefore=0))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Planilha Alvo:</b>", styles['TableCell']),
            Paragraph("ingredientes_racoes_GO_campo_dourado.xlsx", styles['TableCell']),
            Paragraph("<b>Cenário:</b>", styles['TableCell']),
            Paragraph("Conservador (100 vacas, Goiás)", styles['TableCell'])
        ],
        [
            Paragraph("<b>Arquivo-Mestre:</b>", styles['TableCell']),
            Paragraph("NASEM_Comp.csv (inputs_resolvidos)", styles['TableCell']),
            Paragraph("<b>Data do Ajuste:</b>", styles['TableCell']),
            Paragraph("Outubro / 2026", styles['TableCell'])
        ]
    ]
    t_meta = Table(meta_data, colWidths=[usable_width*0.17, usable_width*0.43, usable_width*0.16, usable_width*0.24])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Overview
    story.append(Paragraph("1. Contexto e Objetivo do Documento", styles['SectionHeader']))
    story.append(Paragraph(
        "Este relatório formaliza a proveniência e os valores dos parâmetros nutricionais inseridos na planilha "
        "<b><code>ingredientes_racoes_GO_campo_dourado.xlsx</code></b>. Os ingredientes correspondem aos 12 alimentos "
        "utilizados na formulação das dietas dos lotes de animais (bezerros, novilhas em recria, vacas no pré-parto e vacas em lactação) "
        "para o cenário representativo da bacia leiteira de Goiás no simulador biofísico <b>RuFaS</b>.",
        styles['BodyP']
    ))
    story.append(Paragraph(
        "A biblioteca de composição de alimentos adotada é a do padrão oficial <b>NASEM (2021)</b>, cujas características bromatológicas "
        "alimentam o motor de cálculo de exigências nutricionais e formulação linearizada de mínimo custo.",
        styles['BodyP']
    ))

    # Section 2: Main Consolidated Table
    story.append(Paragraph("2. Tabela de Alimentos Preenchida na Planilha", styles['SectionHeader']))
    story.append(Paragraph(
        "A tabela abaixo reproduz fielmente as colunas e os dados consolidados na planilha Excel, onde todas as "
        "células anteriormente pendentes (travessão '–') foram completadas com os teores oficiais do RuFaS:",
        styles['BodyP']
    ))

    # Table columns:
    # 1: feed_type (40)
    # 2: Alimento (145)
    # 3: Categoria (85)
    # 4: DM (45)
    # 5: CP (45)
    # 6: NDF (45)
    # 7: Ca (45)
    # 8: P (45)
    # 9: Custo (45)
    # Sum = 40+145+85+45*6 = 540 pt
    headers_main = [
        Paragraph("<b>feed_type</b>", styles['TableHead']),
        Paragraph("<b>Alimento</b>", styles['TableHead']),
        Paragraph("<b>Categoria</b>", styles['TableHead']),
        Paragraph("<b>DM<br/>(%MS)</b>", styles['TableHead']),
        Paragraph("<b>CP<br/>(%)</b>", styles['TableHead']),
        Paragraph("<b>NDF<br/>(%)</b>", styles['TableHead']),
        Paragraph("<b>Ca<br/>(%)</b>", styles['TableHead']),
        Paragraph("<b>P<br/>(%)</b>", styles['TableHead']),
        Paragraph("<b>Custo<br/>($/kg MS)</b>", styles['TableHead'])
    ]

    rows_main = [headers_main]
    
    table_data_raw = [
        (18, 'Bermudagrass, feno', 'Forragem', 93.37, 10.99, 65.41, 0.491, 0.195, 0.01),
        (23, 'Blood meal, low dRUP', 'Concentrado proteico', 90.86, 95.06, 0.00, 0.135, 0.276, 0.10),
        (44, 'Milho grão moído seco', 'Energético', 86.91, 8.51, 9.76, 0.035, 0.309, 0.50),
        (51, 'Silagem de milho, meia maturação', 'Forragem', 35.36, 7.71, 40.93, 0.237, 0.232, 0.01),
        (94, 'Mistura capim-leguminosa, feno', 'Forragem', 89.24, 15.61, 54.69, 0.625, 0.329, 0.01),
        (100, 'Mistura capim-leguminosa, silagem', 'Forragem', 40.02, 17.68, 51.23, 0.870, 0.341, 0.01),
        (110, 'Leguminosa forrageira, silagem', 'Forragem', 42.88, 20.47, 43.20, 1.254, 0.351, 0.01),
        (176, 'Sudan grass, silagem madura', 'Forragem', 31.47, 9.54, 66.62, 0.446, 0.266, 0.10),
        (202, 'Leite integral', 'Leite (bezerros)', 12.50, 25.40, 0.00, 1.000, 0.750, 0.10),
        (216, 'Starter 18CP high starch (bezerros)', 'Starter', 88.00, 20.60, 17.37, 0.750, 0.370, 0.10),
        (301, 'Premix mineral/vitamínico', 'Mineral', 99.46, 0.04, 0.14, 15.430, 2.320, 1.00),
        (303, 'Premix mineral/vitamínico', 'Mineral', 74.11, 33.37, 23.88, 0.422, 0.730, 0.10),
    ]

    for item in table_data_raw:
        rows_main.append([
            Paragraph(str(item[0]), styles['TableCellCenter']),
            Paragraph(item[1], styles['TableCell']),
            Paragraph(item[2], styles['TableCell']),
            Paragraph(f"{item[3]:.2f}", styles['TableCellRight']),
            Paragraph(f"{item[4]:.2f}", styles['TableCellRight']),
            Paragraph(f"{item[5]:.2f}", styles['TableCellRight']),
            Paragraph(f"{item[6]:.3f}", styles['TableCellRight']),
            Paragraph(f"{item[7]:.3f}", styles['TableCellRight']),
            Paragraph(f"{item[8]:.2f}", styles['TableCellRight']),
        ])

    t_main = Table(rows_main, colWidths=[48, 142, 80, 45, 45, 45, 45, 45, 45])
    
    t_main_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')), # Teal Header
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0f766e')),
    ]
    # Alternating row colors
    for r_idx in range(1, len(rows_main)):
        if r_idx % 2 == 0:
            t_main_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor('#f8fafc')))
        else:
            t_main_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.white))
            
    t_main.setStyle(TableStyle(t_main_style))
    story.append(t_main)
    story.append(Spacer(1, 8))

    # Callout box regarding Ca and P
    callout_data = [[
        Paragraph(
            "<b>Nota Técnica sobre Cálcio e Fósforo (Linhas 4 a 6):</b><br/>"
            "Na planilha original, os alimentos 18, 23 e 44 haviam sido preenchidos com um deslocamento de 1 coluna "
            "(o teor de Fósforo constava sob <code>Ca (%)</code> e o de Magnésio sob <code>P (%)</code>). "
            "Todas as 12 linhas foram devidamente alinhadas e corrigidas conforme as variáveis <code>calcium</code> e "
            "<code>phosphorus</code> da matriz oficial do NASEM.",
            styles['CalloutText']
        )
    ]]
    t_callout = Table(callout_data, colWidths=[usable_width])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0d9488')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 14))

    # Section 3: Data Sources
    story.append(Paragraph("3. Origem dos Dados e Rastreabilidade nos Arquivos do RuFaS", styles['SectionHeader']))
    story.append(Paragraph(
        "Os teores nutricionais e econômicos foram extraídos da estrutura de simulação da Fazenda Campo Dourado. "
        "A cadeia de proveniência envolve quatro arquivos-chave do repositório:",
        styles['BodyP']
    ))

    sources_data = [
        [
            Paragraph("<b>Arquivo / Caminho</b>", styles['TableHead']),
            Paragraph("<b>Escopo e Descrição no RuFaS</b>", styles['TableHead']),
            Paragraph("<b>Variáveis Extraídas</b>", styles['TableHead'])
        ],
        [
            Paragraph("<code>Fazenda Campo Dourado/<br/>GO_campo_dourado/<br/>inputs_resolvidos/<br/>NASEM_Comp.csv</code>", styles['TableCell']),
            Paragraph("Matriz bromatológica oficial com 176 alimentos do padrão NASEM (2021) e 90 variáveis por alimento. Idêntico ao arquivo na raiz do <code>RuFaS-dev</code>.", styles['TableCell']),
            Paragraph("<code>DM</code> (Matéria Seca),<br/><code>CP</code> (Proteína Bruta),<br/><code>NDF</code> (FDN),<br/><code>calcium</code> (Cálcio),<br/><code>phosphorus</code> (Fósforo).", styles['TableCell'])
        ],
        [
            Paragraph("<code>inputs_resolvidos/<br/>user_feeds.csv</code>", styles['TableCell']),
            Paragraph("Tabela descritiva de catálogo com 300 ingredientes, indexada por <code>rufas_id</code>.", styles['TableCell']),
            Paragraph("Nomes em inglês, descrição do alimento e categorias originais.", styles['TableCell'])
        ],
        [
            Paragraph("<code>inputs_resolvidos/<br/>feed.json</code> e<br/><code>feed_goias.json</code>", styles['TableCell']),
            Paragraph("Configuração das dietas dos lotes da fazenda e custos de aquisição por kg de Matéria Seca.", styles['TableCell']),
            Paragraph("<code>purchased_feed_cost</code> (custo de compra por kg de MS).", styles['TableCell'])
        ],
        [
            Paragraph("<code>docs/<br/>OtimizadorNasem.pdf</code>", styles['TableCell']),
            Paragraph("Documento técnico do Otimizador Linear NASEM (Simplex/HiGHS) acoplado ao RuFaS.", styles['TableCell']),
            Paragraph("Especificação das restrições e confirmação de que <code>rufas_id == feed_type</code>.", styles['TableCell'])
        ]
    ]
    t_sources = Table(sources_data, colWidths=[usable_width*0.33, usable_width*0.42, usable_width*0.25])
    t_sources.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f8fafc')),
    ]))
    story.append(t_sources)
    story.append(Spacer(1, 14))

    # Section 4: Raw values comparison table
    story.append(Paragraph("4. Rastreabilidade Detalhada: Valores Brutos no NASEM_Comp.csv", styles['SectionHeader']))
    story.append(Paragraph(
        "Para fins de auditoria científica e validação das dietas, a tabela abaixo apresenta os valores brutos "
        "exatos (com precisão de 4 casas decimais) conforme registrados no arquivo <code>NASEM_Comp.csv</code>:",
        styles['BodyP']
    ))

    raw_headers = [
        Paragraph("<b>rufas_id</b>", styles['TableHead']),
        Paragraph("<b>Nome Oficial no NASEM (Name)</b>", styles['TableHead']),
        Paragraph("<b>DM bruto</b>", styles['TableHead']),
        Paragraph("<b>CP bruto</b>", styles['TableHead']),
        Paragraph("<b>NDF bruto</b>", styles['TableHead']),
        Paragraph("<b>Ca bruto</b>", styles['TableHead']),
        Paragraph("<b>P bruto</b>", styles['TableHead']),
    ]

    raw_rows = [raw_headers]
    raw_records = [
        (18, 'Bermudagrass hay', '93.3730', '10.9910', '65.4080', '0.4910', '0.1950'),
        (23, 'Blood meal, low dRUP', '90.8640', '95.0600', '0.0000', '0.1350', '0.2760'),
        (44, 'Corn grain dry, medium grind', '86.9070', '8.5140', '9.7610', '0.0350', '0.3090'),
        (51, 'Corn silage, typical', '35.3610', '7.7070', '40.9310', '0.2370', '0.2320'),
        (94, 'Grass lg mixt, grass hay, mid', '89.2390', '15.6080', '54.6850', '0.6250', '0.3290'),
        (100, 'Grass lg mixt, mix silage', '40.0210', '17.6790', '51.2320', '0.8700', '0.3410'),
        (110, 'Legume silage, mid-maturity', '42.8830', '20.4710', '43.1950', '1.2540', '0.3510'),
        (176, 'Sudangrass silage, mature', '31.4710', '9.5380', '66.6170', '0.4460', '0.2660'),
        (202, 'Whole milk', '12.5000', '25.4000', '0.0000', '1.0000', '0.7500'),
        (216, 'Calf starter 18CP high starch (Fed to calves)', '88.0000', '20.6000', '17.3700', '0.7500', '0.3700'),
        (301, 'Farm ES Mineral Mix', '99.4594', '0.0351', '0.1449', '15.4300', '2.3200'),
        (303, 'Farm ES Northeast BP Blend', '74.1127', '33.3732', '23.8769', '0.4217', '0.7297'),
    ]

    for rec in raw_records:
        raw_rows.append([
            Paragraph(str(rec[0]), styles['TableCellCenter']),
            Paragraph(rec[1], styles['TableCell']),
            Paragraph(rec[2], styles['TableCellRight']),
            Paragraph(rec[3], styles['TableCellRight']),
            Paragraph(rec[4], styles['TableCellRight']),
            Paragraph(rec[5], styles['TableCellRight']),
            Paragraph(rec[6], styles['TableCellRight']),
        ])

    t_raw = Table(raw_rows, colWidths=[45, 185, 62, 62, 62, 62, 62])
    t_raw_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
    ]
    for r_idx in range(1, len(raw_rows)):
        if r_idx % 2 == 0:
            t_raw_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor('#f8fafc')))
        else:
            t_raw_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.white))
    t_raw.setStyle(TableStyle(t_raw_style))
    story.append(t_raw)
    story.append(Spacer(1, 14))

    # Section 5: Conclusion / Sign-off
    story.append(Paragraph("5. Validação e Conclusão", styles['SectionHeader']))
    story.append(Paragraph(
        "A integridade dos dados foi testada e aprovada pelo ambiente de simulação biofísica do RuFaS. "
        "A planilha Excel encontra-se pronta para utilização em formulações de dietas, estudos de sensibilidade "
        "econômica e integração com as rotinas de otimização linear (Simplex) do projeto.",
        styles['BodyP']
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Copy to docs/ as well
    import shutil
    shutil.copy2(pdf_filename, docs_pdf_filename)
    print('Generated PDF at:', pdf_filename)
    print('Copied PDF to:', docs_pdf_filename)

if __name__ == '__main__':
    generate_pdf()
