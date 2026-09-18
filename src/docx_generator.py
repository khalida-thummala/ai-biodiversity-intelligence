import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def create_submission_docx(
    output_path="c:/Users/khali/AIChatbot/Darukaa_Earth_Submission_AI_Biodiversity.docx",
    github_url="https://github.com/darukaa-submission/ai-biodiversity-intelligence",
    demo_url="http://localhost:8501 (or Streamlit Community Cloud)"
):
    doc = Document()

    title = doc.add_heading(level=0)
    run_title = title.add_run("Darukaa.Earth Hackathon Submission\nAI Biodiversity Intelligence Chatbot")
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(34, 84, 61)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run("A Knowledge-Grounded, Multi-Metric Environmental Scientist Reasoning System")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(74, 85, 104)

    doc.add_heading("1. Submission & Repository Links", level=1)
    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    rows_data = [
        ("GitHub Repository Link", github_url),
        ("Live Demo URL", demo_url),
        ("Model Core", "Google Gemini 3.6 Flash / 3.5 Flash Lite + RAG Hybrid Engine"),
        ("Invited Reviewers", "ankita.dasgupta@darukaa.com, harsh.kumar@darukaa.com, utkarsh.gauniyal@darukaa.com, guneet.mutreja@darukaa.com")
    ]
    for idx, (label, val) in enumerate(rows_data):
        row = table.rows[idx]
        row.cells[0].text = label
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[1].text = val
        set_cell_background(row.cells[0], "F0FDF4")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_heading("2. System Architecture & Scientific Design", level=1)
    doc.add_paragraph(
        "This system addresses the Darukaa.Earth challenge by behaving as an AI Environmental Scientist rather than a superficial chatbot. "
        "It combines a structured RAG knowledge layer with multi-metric causal reasoning and strict conversational intelligence that refuses to make "
        "generic guesses without adequate baseline metrics."
    )

    doc.add_heading("Core Architectural Layers:", level=2)
    arch_points = [
        ("Knowledge Layer (RAG): ", "Indexes verified scientific reports from FAO (Recarbonizing Global Soils, 2020), IPCC (Special Report on Climate Change and Land, 2019), and IPBES (Global Assessment Report, 2019). Documents are structured with explicit baseline conditions, quantitative impact benchmarks, and peer-reviewed citations."),
        ("Multi-Metric Reasoning Engine: ", "Enforces the mandatory requirement to cross-link at least 3 environmental dimensions together (Soil Health <-> Water Dynamics <-> Species Survival/Trophic Diversity). No single-variable answers are permitted."),
        ("Conversational Intelligence: ", "Evaluates input sufficiency before synthesizing recommendations. When presented with underspecified statements (e.g., 'Biodiversity is declining on my land'), the agent asks targeted clarifying questions to establish baseline soil carbon %, rainfall pattern, and land use."),
        ("Dual Input Modality: ", "Accepts both free-form natural language and structured JSON inputs, alongside bonus geospatial coordinate inference to estimate regional biomes and rainfall regimes.")
    ]
    for title_text, desc in arch_points:
        p = doc.add_paragraph(style='List Bullet')
        r_bold = p.add_run(title_text)
        r_bold.font.bold = True
        p.add_run(desc)

    doc.add_heading("3. Challenge Benchmark Verification", level=1)
    doc.add_paragraph("The system was tested against the official hackathon use case specified in the challenge brief:")
    
    test_table = doc.add_table(rows=5, cols=2)
    test_table.style = 'Table Grid'
    test_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    test_data = [
        ("Input Soil Organic Carbon", "0.3% (Critically depleted baseline)"),
        ("Input Rainfall Pattern", "Low (< 450 mm/year, semi-arid)"),
        ("Input Land Use", "Monoculture wheat"),
        ("Input Region", "Semi-arid dryland"),
        ("Generated Interventions", "1. Silvoarable Alley Cropping with Drought-Tolerant Native Trees (FAO/IPCC)\n2. Multi-Species Legume Cover Cropping & MAOM Sequestration (FAO/Lal)\n3. Native Flowering Hedgerow & Microclimate Corridors (IPBES)")
    ]
    for idx, (param, val) in enumerate(test_data):
        row = test_table.rows[idx]
        row.cells[0].text = param
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[1].text = val
        set_cell_background(row.cells[0], "F7FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_heading("4. Evidence-Backed Improvement Benchmarks", level=1)
    doc.add_paragraph("All interventions are supported by explicit quantitative metrics and scientific mechanisms:")
    
    metric_table = doc.add_table(rows=4, cols=3)
    metric_table.style = 'Table Grid'
    metric_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Intervention", "Quantified Metric Improvements", "Credible Citations"]
    for col_idx, h in enumerate(headers):
        cell = metric_table.rows[0].cells[col_idx]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "E2E8F0")

    benchmarks_data = [
        (
            "Silvoarable Agroforestry & Alley Cropping",
            "- Soil Organic Carbon: +0.25 to +0.65 t C/ha/yr\n- Wind erosion loss: -50% to -75%\n- Water Use Efficiency: +18% to +30%\n- Avian/Arthropod Diversity: +40% to +65%",
            "IPCC (2019) SRCCL Ch. 4; CGIAR / ICRAF (2021)"
        ),
        (
            "Legume-Based Cover Cropping",
            "- Soil Organic Carbon: +15% to +28% over 2-4 yrs\n- Microbial Biomass: +35% to +50%\n- Infiltration Rate: +25% to +40%\n- Synthetic N reduction: 30% to 50%",
            "FAO (2020) Recarbonizing Global Soils; Lal, R. (2018)"
        ),
        (
            "Native Hedgerows & Buffer Corridors",
            "- Wild bee richness: +70% to +120%\n- Natural pest predation: +45%\n- Runoff filtration: 55% to 75%\n- Wildlife dispersal: +120%",
            "IPBES (2016) Pollinators; Kremen & Miles (2012)"
        )
    ]
    for row_idx, data_tuple in enumerate(benchmarks_data, start=1):
        row = metric_table.rows[row_idx]
        for col_idx, text_val in enumerate(data_tuple):
            row.cells[col_idx].text = text_val

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_heading("5. Local Setup & Execution Guide", level=1)
    steps = [
        "1. Clone the repository: git clone " + github_url,
        "2. Create virtual environment and install dependencies: pip install -r requirements.txt",
        "3. Configure your GEMINI_API_KEY in the .env file",
        "4. Run the interactive Streamlit application: streamlit run app.py",
        "5. Run the automated test suite: python tests/test_scenarios.py"
    ]
    for s in steps:
        p = doc.add_paragraph(s)
        p.paragraph_format.left_indent = Inches(0.2)

    doc.save(output_path)
    print(f"Successfully generated submission document at: {output_path}")

if __name__ == "__main__":
    create_submission_docx()
