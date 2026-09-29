"""Generate both GROUP_02_C1_Slides.pdf and GROUP_02_C1_Slides.pptx for the C1 Defense.

Team: Benjamín Pinto & Sebastián Herrera (Group 02)
Course: Business Intelligence (IIB423T-1) - Universidad del Desarrollo
"""

from pathlib import Path
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


PACKAGE = Path(__file__).resolve().parents[1]
OUTPUT_PDF = PACKAGE / "presentation/GROUP_02_C1_Slides.pdf"
OUTPUT_PPTX = PACKAGE / "presentation/GROUP_02_C1_Slides.pptx"
FIG = PACKAGE / "analysis/figures"

# Ensure presentation dir exists
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

# Register fonts for ReportLab
for normal, bold in [
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
]:
    if Path(normal).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont("DejaVu", normal))
        pdfmetrics.registerFont(TTFont("DejaVuBold", bold))
        pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVuBold")
        break


# -------------------------------------------------------------
# 1. GENERATE PPTX (EDITABLE PRESENTATION)
# -------------------------------------------------------------
def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_TEAL = RGBColor(22, 49, 59)
    MED_TEAL = RGBColor(39, 102, 122)
    AMBER = RGBColor(186, 107, 59)
    GRAY = RGBColor(83, 99, 106)
    LIGHT_BG = RGBColor(240, 245, 247)

    def add_header(slide, title_text, category_text="BUSINESS INTELLIGENCE IIB423T-1 · CERTAMEN 1"):
        # Header category
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = MED_TEAL

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_TEAL

    # --- SLIDE 1: Title Slide ---
    s1 = prs.slides.add_slide(blank_layout)
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Business Intelligence · IIB423T-1 · Certamen 1"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = MED_TEAL
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "Respiratory Emergency Visits in Chile (2020–2024)"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Full Exploratory Data Analysis, Five Cs Quality Audit, and Capacity Planning for the Winter Campaign"
    p.font.size = Pt(16)
    p.font.color.rgb = GRAY
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Team: Benjamín Pinto & Sebastián Herrera  |  Group: 02\nInstructor: Tomás Fontecilla Correa  |  Date: September 29, 2026"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_TEAL

    # --- SLIDE 2: Problem & Operational Decision ---
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Operational Context & The Winter Campaign Decision")
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    bullets2 = [
        ("The Public Health Concern:", "Recurrent, severe seasonal surges in acute respiratory infections (RSV, Influenza A/B, Adenovirus, COVID-19) place intense pressure on the Chilean emergency network."),
        ("Target Users:", "Directorate for Health Care Network Management (DIGERA), Health Service directors, and emergency leaders (SAPU, SAR, SUR, and Hospitals)."),
        ("The Decision to Inform:", "Timing the activation of Winter Campaign measures: scheduling clinical shifts (physicians, nurses, kinesitherapy), phased critical bed conversions, and primary care triage diversion before hospital emergency departments reach saturation."),
        ("Core KPI & Analytical Formula:", "Respiratory Share (%) = 100 × Total Respiratory Visits (IdCausa = 2) / Total Emergency Visits (IdCausa = 1)."),
        ("Critical Boundary:", "This measures recorded public-network consultation activity. It does NOT measure individual disease risk, clinical severity, bed occupancy, or population incidence.")
    ]
    for title, desc in bullets2:
        p = tf2.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(12)

    # --- SLIDE 3: W1 to C1 Evolution ---
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Selection from W1 and the C1 Correction")
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    bullets3 = [
        ("Why Candidate A (Respiratory) was Selected:", "Offers a continuous, high-frequency time series (262 dated weeks across 2020–2024) with complete reporting, directly supporting seasonal monitoring."),
        ("Why Candidate B (REM-P2 Child Nutrition) was Deselected:", "Audit uncovered severe reporting collapse in June 2020 (only 83 facilities reported due to pandemic lockdowns vs >1,950 normally); only 10 reporting points in 5 years; >59% of age/sex breakdown cells missing; code changes in 2023."),
        ("The W1-to-C1 Reproducibility Correction:", "While W1 reported 5-year aggregates, its submitted reduced extract included only sample peak weeks in 2023–2024. For C1, our teammate's internal review corrected this by expanding the packaged extract to EVERY date across all 5 years (2020–2024)."),
        ("Audit Scope:", "The uncleaned extract contains 2,169,824 rows (~85x larger than W1's extract) while maintaining an efficient 19 MB compressed archive size.")
    ]
    for title, desc in bullets3:
        p = tf3.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(12)

    # --- SLIDE 4: Seven Steps of BI Framing ---
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Application of the Seven Steps (Class 03 Framework)")
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    steps = [
        ("1. Decision:", "Proposed winter planners review weekly demand trajectory to determine when to activate phased staffing and bed contingency plans."),
        ("2. Success Criteria:", "Construct a reproducible 2020–2024 weekly baseline with audited coverage, stable codes, and verified care-setting coupling."),
        ("3. Business Question:", "How did the weekly volume and share of respiratory emergency visits vary in 2020–2024 across care settings and age bands?"),
        ("4. Care Process:", "Daily emergency consultation records (DAU/SADU) logged at health facilities and transmitted to DEIS."),
        ("5. Entities & Events:", "Entity: Health facility. Event: Recorded emergency visit. Observation unit: Aggregate facility × date × cause count (NOT unique patients)."),
        ("6. Representation:", "Candidate key: (source_year, IdEstablecimiento, fecha, IdCausa). Clean case derives Sunday week starts from parsed dates."),
        ("7. Measurement:", "Respiratory Visits = Total(IdCausa=2); Respiratory Share (%) = Total(IdCausa=2) / Total(IdCausa=1) × 100 within identical periods/units.")
    ]
    for title, desc in steps:
        p = tf4.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(6)

    # --- SLIDE 5: Five Cs Quality Audit ---
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Data Profiling & The Five Cs Quality Audit")
    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    five_cs = [
        ("Clean:", "Checked 2,169,824 rows: zero missing key/measure cells; zero negative values; age sums match Total 100%. Two identical duplicate rows in 2023 removed only from derived tables (-13 all visits, -0 respiratory). Valid zero-count rows retained."),
        ("Consistent:", "IdCausa 1 and 2 maintain stable definitions across 2020–2024. Parsing dates into Sunday week starts resolves calendar boundary collisions where the same (year, semana) label mapped to two disjoint weeks."),
        ("Conformed:", "Harmonized schemas across annual DEIS archives. No external geographic join is claimed: 2020–2022 lack direct comuna/region fields, and unvalidated joins risk creating duplicate or unmatched rows."),
        ("Current:", "The 2020–2024 series is appropriate for historical baseline analysis. It cannot directly guide live 2026 shift decisions without an automated operational feed."),
        ("Comprehensive:", "Covers the entire reporting public emergency network (>600 facilities annually). Does not cover private clinic care or self-treated community cases.")
    ]
    for title, desc in five_cs:
        p = tf5.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(12.5)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(10)

    # --- SLIDE 6: Full EDA - Distributions & Densities ---
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Full EDA: Histograms & Kernel Density Estimation (KDE)")
    img_path = FIG / "eda_distributions_kde.png"
    if img_path.exists():
        s6.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))
    tb6 = s6.shapes.add_textbox(Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    p = tf6.paragraphs[0]
    p.text = "Key Statistical Findings:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(10)

    bullets6 = [
        ("Parametric Non-Normality:", "Weekly volume and share distributions exhibit high positive skewness and heavy right tails during epidemic surges; normality assumptions fail."),
        ("Pandemic Suppression (2020–2021):", "Unimodal, tightly bounded distribution centered at ~10% share and <50k weekly visits due to school closures and mask mandates."),
        ("Post-Pandemic Rebound (2022–2024):", "Multimodal distribution with broad dispersion reaching 45.56% share and 203,353 visits/week."),
        ("Operational Implication:", "Planning models must account for regime shifts; assuming a single Gaussian distribution severely underestimates peak surge risk.")
    ]
    for t, d in bullets6:
        p = tf6.add_paragraph()
        p.text = f"• {t} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(8)

    # --- SLIDE 7: Full EDA - Seasonality & May Peaks ---
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Full EDA: Seasonal Dynamics & Autumn Peaks")
    img_path = FIG / "weekly_volume_and_share.png"
    if img_path.exists():
        s7.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))
    tb7 = s7.shapes.add_textbox(Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    p = tf7.paragraphs[0]
    p.text = "Historical Peak Evidence:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(10)

    bullets7 = [
        ("260 Complete Weeks Analyzed:", "Edge weeks (4 and 3 days) excluded for strict cross-year peak comparability."),
        ("2023 Peak:", "Week of 14–20 May: 189,297 respiratory visits (41.66% share)."),
        ("2024 Peak:", "Week of 12–18 May: 203,353 respiratory visits (45.56% share)."),
        ("Timing Corroboration:", "MINSAL's 24 May 2024 official campaign report recorded 45.4% week-20 share, broadly corroborating this archive's 45.56% timing."),
        ("Key Takeaway for Planners:", "Peaks in recent years occurred in mid-May (late autumn), NOT in July/August (mid-winter). Preparedness reviews must begin early in April.")
    ]
    for t, d in bullets7:
        p = tf7.add_paragraph()
        p.text = f"• {t} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(8)

    # --- SLIDE 8: Full EDA - Statistical Correlations (Pearson vs Spearman) ---
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Statistical Correlation: Pearson (Linear) vs. Spearman (Rank)")
    img_path = FIG / "eda_correlation_analysis.png"
    if img_path.exists():
        s8.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.5))
    tb8 = s8.shapes.add_textbox(Inches(8.5), Inches(1.5), Inches(4.0), Inches(5.4))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    p = tf8.paragraphs[0]
    p.text = "The Statistician's View:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(10)

    bullets8 = [
        ("Linear vs Monotonic:", "Pearson evaluates linear bivariate normality; Spearman evaluates monotonic rank ordering, immune to non-linear surges."),
        ("Age Co-Movement:", "Spearman is systematically higher than Pearson across all age groups (+0.012 to +0.074). Between <1 and 65+, correlation rises from r = 0.775 (Pearson) to rho = 0.835 (Spearman)."),
        ("Why? Epidemic Dynamics:", "Different virus onset slopes (steep early RSV surge vs delayed influenza wave) depress linear Pearson, but rank severity across weeks is strongly preserved."),
        ("Network Coupling:", "Primary Care (SAPU/SAR) vs Hospital demand has Pearson r = 0.9835 and Spearman rho = 0.9848. Triage and hospital pressure move in lockstep.")
    ]
    for t, d in bullets8:
        p = tf8.add_paragraph()
        p.text = f"• {t} "
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(8)

    # --- SLIDE 9: Care-Setting & Age Composition ---
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Demand Breakdown: Care Settings & Vulnerable Age Groups")
    img_path = FIG / "age_and_facility_mix.png"
    if img_path.exists():
        s9.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))
    tb9 = s9.shapes.add_textbox(Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    p = tf9.paragraphs[0]
    p.text = "Compositional Findings:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(10)

    bullets9 = [
        ("Primary Care Shock Absorber:", "SAPU, SAR, and SUR facilities handle between 71.08% (2020) and 75.87% (2024) of all recorded respiratory emergencies."),
        ("Pediatric Share:", "Under-15 visits represented 30.05% of respiratory consultations in 2020, spiking to 50.71% in 2022 with school reopening, and settling at 40.72% in 2024."),
        ("Older Adult Demand:", "Adults aged 65+ account for ~15-18% of visits, but represent the highest risk of hospitalization and ICU admission."),
        ("Design Consequence:", "Monitoring cannot look only at hospitals. Primary care triage volume is the earliest and largest indicator of winter network strain.")
    ]
    for t, d in bullets9:
        p = tf9.add_paragraph()
        p.text = f"• {t} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(8)

    # --- SLIDE 10: Sensitivity Analysis ---
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Sensitivity Check: Stable 581-Facility Panel")
    img_path = FIG / "common_facility_sensitivity.png"
    if img_path.exists():
        s10.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))
    tb10 = s10.shapes.add_textbox(Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    p = tf10.paragraphs[0]
    p.text = "Controlling for Entry/Exit:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_TEAL
    p.space_after = Pt(10)

    bullets10 = [
        ("Compositional Bias Risk:", "Total reporting facilities varied from 607 (2020) to 642 (2023). Did facility entry/exit create the observed respiratory surge?"),
        ("The Stable Panel:", "581 facility IDs reported across ALL five years, covering 98.05% of all emergency visits in 2020 and 95.89% in 2024."),
        ("Empirical Result:", "Respiratory share in the common-facility panel: 10.73%, 9.97%, 24.62%, 28.86%, 28.37% (virtually identical to full sample)."),
        ("Conclusion:", "The dramatic post-pandemic rebound is a genuine epidemiological and care-seeking reality, not an artifact of reporting panel turnover.")
    ]
    for t, d in bullets10:
        p = tf10.add_paragraph()
        p.text = f"• {t} "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(8)

    # --- SLIDE 11: Feasible Project Continuation ---
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Project Continuity: Beyond C1 (ML & Dashboard)")
    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.4))
    tf11 = tb11.text_frame
    tf11.word_wrap = True

    bullets11 = [
        ("Future Supervised ML Task:", "Predict weekly respiratory emergency volume 2 completed weeks ahead (t+2) by care setting (SAPU/SAR vs Hospitals)."),
        ("Information Boundary & Data Leakage:", "Predictors restricted strictly to information available prior to the forecast week: lagged volume counts, calendar week indicators, and historical seasonal moving averages. No target week counts or post-outcome fields used."),
        ("Honest ML Feasibility Challenges:", "With only 5 annual cycles and a strong regime shift in 2020–2021, standard time-series splits face high variance. Operational deployment requires an automated live feed. (No model trained in C1)."),
        ("Future BI Dashboard Prototype:", "Targeted at DIGERA and Health Service emergency coordinators."),
        ("Core Dashboard Views:", "1) Real-time weekly demand curve against 5-year historical confidence bands; 2) Pediatric (<1, 1-4) vs Geriatric (65+) composition; 3) SAPU/SAR absorption ratio; 4) Reporting facility freshness and completeness flags.")
    ]
    for title, desc in bullets11:
        p = tf11.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(10)

    # --- SLIDE 12: Defense Anchors & Member Roles ---
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Summary & Individual Defense Anchors (Q&A)")
    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.4))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    bullets12 = [
        ("What This Analysis Demonstrates (F):", "Defensible, auditable 5-year retrospective characterization of respiratory emergency demand, peak timing (May), age co-movement, and care-setting coupling in Chile."),
        ("What This Analysis Cannot Claim (H):", "Does not estimate individual patient risk, true disease incidence, bed occupancy rates, triage wait times, or causal impacts of health campaigns."),
        ("Benjamín Pinto — Methodological Lead (G):", "Processing 2.17M rows; 5 Cs quality audit; duplicate key resolution; date-derived Sunday week starts; statistical correlation analysis (Pearson vs Spearman); parametric vs nonparametric density."),
        ("Sebastián Herrera — Selection & Sensitivity Lead (G):", "Candidate B deselection audit (REM-P2 coverage collapse in June 2020); 581 common-facility panel sensitivity; care-setting breakdown (SAPU vs Hospital); dashboard design & operational framing.")
    ]
    for title, desc in bullets12:
        p = tf12.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(12.5)
        p.font.color.rgb = DARK_TEAL
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = GRAY
        p.space_after = Pt(12)

    prs.save(OUTPUT_PPTX)
    print(f"Built editable presentation: {OUTPUT_PPTX}")


# -------------------------------------------------------------
# 2. GENERATE PDF SLIDES (USING REPORTLAB)
# -------------------------------------------------------------
def build_pdf():
    # 16:9 widescreen: 1152 x 648 pt
    PAGE_W, PAGE_H = 16 * 72, 9 * 72
    MARGIN = 0.5 * inch

    DARK_TEAL = colors.HexColor("#16313b")
    MED_TEAL = colors.HexColor("#27667a")
    AMBER = colors.HexColor("#ba6b3b")
    MUTED = colors.HexColor("#53636a")
    LIGHT_BG = colors.HexColor("#f0f5f7")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="SlideTitle", fontName="DejaVuBold", fontSize=20, leading=24, textColor=DARK_TEAL, spaceAfter=4
    )
    cat_style = ParagraphStyle(
        name="SlideCat", fontName="DejaVuBold", fontSize=9, leading=12, textColor=MED_TEAL, spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        name="SlideBullet", fontName="DejaVu", fontSize=11, leading=16, textColor=DARK_TEAL, spaceAfter=8
    )
    bold_prefix_style = ParagraphStyle(
        name="SlideBoldPrefix", fontName="DejaVuBold", fontSize=11, leading=16, textColor=DARK_TEAL
    )

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF), pagesize=(PAGE_W, PAGE_H),
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN
    )

    story = []

    def slide_header(category, title):
        story.append(Paragraph(category.upper(), cat_style))
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 14))

    # --- SLIDE 1 ---
    story.append(Spacer(1, 100))
    story.append(Paragraph("BUSINESS INTELLIGENCE · IIB423T-1 · CERTAMEN 1 (C1)", ParagraphStyle(
        name="S1Cat", fontName="DejaVuBold", fontSize=13, leading=16, textColor=MED_TEAL, spaceAfter=14
    )))
    story.append(Paragraph("Respiratory Emergency Visits in Chile (2020–2024)", ParagraphStyle(
        name="S1Title", fontName="DejaVuBold", fontSize=32, leading=38, textColor=DARK_TEAL, spaceAfter=12
    )))
    story.append(Paragraph("Full Exploratory Data Analysis, Five Cs Quality Audit, and Capacity Planning for the Winter Campaign", ParagraphStyle(
        name="S1Sub", fontName="DejaVu", fontSize=15, leading=20, textColor=MUTED, spaceAfter=30
    )))
    story.append(Paragraph("<b>Team:</b> Benjamín Pinto & Sebastián Herrera &nbsp;|&nbsp; <b>Group:</b> 02<br/><b>Instructor:</b> Tomás Fontecilla Correa &nbsp;|&nbsp; <b>Date:</b> September 29, 2026", ParagraphStyle(
        name="S1Meta", fontName="DejaVu", fontSize=12, leading=18, textColor=DARK_TEAL
    )))
    story.append(PageBreak())

    # --- SLIDE 2 ---
    slide_header("Context & Decision", "Operational Context & The Winter Campaign Decision")
    b2 = [
        "<b>The Public Health Concern:</b> Recurrent seasonal surges in acute respiratory infections (RSV, Influenza A/B, Adenovirus, COVID-19) place severe pressure on public hospital emergency departments and primary care.",
        "<b>Target Users:</b> Directorate for Health Care Network Management (DIGERA), Health Service directors, and emergency leaders across SAPU, SAR, SUR, and Hospitals.",
        "<b>The Decision to Inform:</b> Timing the activation of Winter Campaign measures: scheduling clinical shifts (physicians, nurses, kinesitherapy), phased critical bed conversions, and primary care triage diversion.",
        "<b>Core KPI & Formula:</b> <i>Respiratory Share (%) = 100 × Total Respiratory Visits (IdCausa = 2) / Total Emergency Visits (IdCausa = 1)</i>.",
        "<b>Critical Methodological Boundary:</b> This measures recorded public-network consultation activity. It does NOT estimate individual clinical risk, disease severity, bed occupancy, or true population incidence."
    ]
    for b in b2:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))
    story.append(PageBreak())

    # --- SLIDE 3 ---
    slide_header("W1 to C1 Evolution", "Selection from W1 and the C1 Reproducibility Correction")
    b3 = [
        "<b>Why Candidate A (Respiratory) was Selected:</b> Continuous, high-frequency weekly series (262 dated weeks across 2020–2024) with complete reporting, directly supporting seasonal monitoring.",
        "<b>Why Candidate B (REM-P2 Child Nutrition) was Deselected:</b> Audit uncovered severe reporting collapse in June 2020 (only 83 facilities reported due to lockdown vs >1,950 normally); only 10 reporting points in 5 years; >59% age/sex breakdown missing; code changes in 2023.",
        "<b>The W1-to-C1 Reproducibility Correction:</b> While W1 reported 5-year aggregates, its packaged reduced extract contained only sample peak weeks in 2023–2024. For C1, an internal teammate review expanded the extract to EVERY date across all 5 years (2020–2024).",
        "<b>Auditable Extract Scope:</b> 2,169,824 uncleaned source rows (~85x larger than W1's extract) while maintaining an efficient 19 MB compressed archive size for seamless verification."
    ]
    for b in b3:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))
    story.append(PageBreak())

    # --- SLIDE 4 ---
    slide_header("Framing Framework", "Application of the Seven Steps (Class 03 Framework)")
    b4 = [
        "<b>1. Decision:</b> Proposed winter planners review weekly demand trajectory to determine when to activate phased staffing and critical bed contingency plans.",
        "<b>2. Success Criteria:</b> Construct a reproducible 2020–2024 weekly baseline with audited coverage, stable definitions, and verified care-setting coupling.",
        "<b>3. Business Question:</b> How did the weekly volume and share of respiratory emergency visits vary in 2020–2024 across care settings and age bands?",
        "<b>4. Care Process:</b> Daily emergency consultation records (DAU/SADU) logged at health facilities and transmitted to DEIS.",
        "<b>5. Entities & Events:</b> Entity: Health facility. Event: Recorded emergency visit. Observation unit: Aggregate facility × date × cause count (NOT unique patients).",
        "<b>6. Representation:</b> Candidate key: (source_year, IdEstablecimiento, fecha, IdCausa). Clean case derives Sunday week starts from parsed dates.",
        "<b>7. Measurement:</b> Respiratory Visits = Total(IdCausa=2); Respiratory Share (%) = Total(IdCausa=2) / Total(IdCausa=1) × 100 within identical periods/units."
    ]
    for b in b4:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))
    story.append(PageBreak())

    # --- SLIDE 5 ---
    slide_header("Quality Audit", "Data Profiling & The Five Cs Quality Audit")
    b5 = [
        "<b>Clean:</b> Checked 2,169,824 rows: zero missing key/measure cells; zero negative values; age sums match Total 100%. Exactly 2 identical duplicate rows in 2023 removed only from derived tables (-13 all visits, -0 respiratory). Valid zero-count rows retained.",
        "<b>Consistent:</b> IdCausa 1 and 2 maintain stable definitions across 2020–2024. Parsing dates into Sunday week starts resolves calendar boundary collisions where the same (year, semana) label mapped to two disjoint weeks.",
        "<b>Conformed:</b> Harmonized schemas across annual DEIS archives. No external geographic join is claimed: 2020–2022 lack direct comuna/region fields, and unvalidated joins risk creating duplicate or unmatched rows.",
        "<b>Current:</b> The 2020–2024 series is appropriate for historical baseline analysis. It cannot directly guide live 2026 shift decisions without an automated operational feed.",
        "<b>Comprehensive:</b> Covers the entire reporting public emergency network (>600 facilities annually). Does not cover private clinic care or self-treated community cases."
    ]
    for b in b5:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))
    story.append(PageBreak())

    # Helper for 2-column image + text slide
    def add_image_slide(category, title, img_name, bullets, img_w=6.5*inch):
        slide_header(category, title)
        img_path = FIG / img_name
        col_w = PAGE_W - 2 * MARGIN - img_w - 0.4 * inch

        img_elem = Image(str(img_path))
        ratio = img_elem.imageHeight / img_elem.imageWidth
        img_elem.drawWidth = img_w
        img_elem.drawHeight = img_w * ratio

        text_story = []
        for b in bullets:
            text_story.append(Paragraph(f"• &nbsp; {b}", ParagraphStyle(
                name="SideBullet", fontName="DejaVu", fontSize=9.5, leading=14, textColor=DARK_TEAL, spaceAfter=8
            )))

        t = Table([[img_elem, text_story]], colWidths=[img_w, col_w])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (1,0), (1,0), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t)
        story.append(PageBreak())

    # --- SLIDE 6 ---
    add_image_slide(
        "Full EDA: Distributions & Densities",
        "Histograms & Kernel Density Estimation (KDE)",
        "eda_distributions_kde.png",
        [
            "<b>Parametric Non-Normality:</b> Weekly volume and share distributions exhibit high positive skewness and heavy right tails during epidemic surges; normality assumptions fail.",
            "<b>Pandemic Suppression (2020–2021):</b> Unimodal, tightly bounded distribution centered at ~10% share and <50k weekly visits due to school closures and mask mandates.",
            "<b>Post-Pandemic Rebound (2022–2024):</b> Multimodal distribution with broad dispersion reaching 45.56% share and 203,353 visits/week during winter peaks.",
            "<b>Operational Implication:</b> Planning models must account for regime shifts; assuming a single Gaussian distribution severely underestimates peak surge risk."
        ],
        img_w=6.8*inch
    )

    # --- SLIDE 7 ---
    add_image_slide(
        "Full EDA: Seasonality & Peak Timing",
        "Weekly Demand Dynamics & Autumn Volume Peaks",
        "weekly_volume_and_share.png",
        [
            "<b>260 Complete Weeks Analyzed:</b> Edge weeks (4 and 3 days) excluded for strict cross-year peak comparability.",
            "<b>2023 Peak:</b> Week of 14–20 May: 189,297 respiratory visits (41.66% share).",
            "<b>2024 Peak:</b> Week of 12–18 May: 203,353 respiratory visits (45.56% share).",
            "<b>Timing Corroboration:</b> MINSAL's 24 May 2024 official campaign report recorded 45.4% week-20 share, broadly corroborating this archive's 45.56% timing.",
            "<b>Key Takeaway for Planners:</b> Peaks in recent years occurred in mid-May (late autumn), NOT in July/August (mid-winter). Preparedness reviews must begin early in April."
        ],
        img_w=6.8*inch
    )

    # --- SLIDE 8 ---
    add_image_slide(
        "Full EDA: Statistical Correlations",
        "Pearson (Linear) vs. Spearman (Rank) Correlation Analysis",
        "eda_correlation_analysis.png",
        [
            "<b>Linear vs Monotonic Association:</b> Pearson evaluates linear bivariate normality; Spearman evaluates monotonic rank ordering, robust against non-linear surges and outliers.",
            "<b>Age Cohort Synchronization:</b> Spearman is systematically higher than Pearson across all age groups (+0.012 to +0.074). Between <1 and 65+, correlation rises from r = 0.775 (Pearson) to rho = 0.835 (Spearman).",
            "<b>Statistical Reason:</b> Different virus onset slopes (steep early RSV surge in infants vs delayed influenza in elderly) depress linear Pearson, but rank severity across weeks is strongly preserved.",
            "<b>Network Coupling:</b> Primary Care (SAPU/SAR) vs Hospital demand has Pearson r = 0.9835 and Spearman rho = 0.9848. Triage and hospital pressure move in lockstep."
        ],
        img_w=7.2*inch
    )

    # --- SLIDE 9 ---
    add_image_slide(
        "Full EDA: Demand Composition",
        "Care-Setting Distribution & Vulnerable Age Cohorts",
        "age_and_facility_mix.png",
        [
            "<b>Primary Care Shock Absorber:</b> SAPU, SAR, and SUR facilities handle between 71.08% (2020) and 75.87% (2024) of all recorded respiratory emergencies.",
            "<b>Pediatric Surge Dynamics:</b> Under-15 patients represented 30.05% of respiratory consultations in 2020, spiking to 50.71% in 2022 with school reopening, and settling at 40.72% in 2024.",
            "<b>Older Adult Demand:</b> Adults aged 65+ account for ~15-18% of visits, but represent the highest risk of hospitalization and ICU bed admission.",
            "<b>Design Consequence:</b> Monitoring cannot look only at hospitals. Primary care triage volume is the earliest and largest indicator of winter network strain."
        ],
        img_w=6.8*inch
    )

    # --- SLIDE 10 ---
    add_image_slide(
        "Sensitivity & Panel Stability",
        "Common-Facility Panel Check (581 Continuous Centers)",
        "common_facility_sensitivity.png",
        [
            "<b>Compositional Bias Risk:</b> Total reporting facilities varied from 607 (2020) to 642 (2023). Did facility entry/exit create the observed respiratory surge?",
            "<b>The Stable Panel:</b> 581 facility IDs reported across ALL five years, covering 98.05% of all emergency visits in 2020 and 95.89% in 2024.",
            "<b>Empirical Result:</b> Respiratory share in the common-facility panel: 10.73%, 9.97%, 24.62%, 28.86%, 28.37% (virtually identical to full sample).",
            "<b>Conclusion:</b> The dramatic post-pandemic rebound is a genuine epidemiological and care-seeking reality, not an artifact of reporting panel turnover."
        ],
        img_w=6.8*inch
    )

    # --- SLIDE 11 ---
    slide_header("Project Continuity", "Project Continuity Beyond C1: Machine Learning & Dashboard")
    b11 = [
        "<b>Future Supervised ML Task:</b> Forecast weekly respiratory emergency visits 2 completed weeks ahead (t+2) by care setting (SAPU/SAR vs Hospitals).",
        "<b>Information Boundary & Data Leakage:</b> Predictors restricted strictly to information available prior to the forecast week: lagged volume counts, calendar week indicators, and historical seasonal moving averages. No target week counts or post-outcome fields used.",
        "<b>Honest ML Feasibility Challenges:</b> With only 5 annual cycles and a strong regime shift in 2020–2021, standard time-series splits face high variance. Operational deployment requires an automated live feed. (No model trained in C1).",
        "<b>Future BI Dashboard Prototype:</b> Targeted at DIGERA and Health Service emergency coordinators.",
        "<b>Core Dashboard Views:</b> 1) Real-time weekly demand curve against 5-year historical confidence bands; 2) Pediatric (<1, 1-4) vs Geriatric (65+) composition; 3) SAPU/SAR absorption ratio; 4) Reporting facility freshness and completeness flags."
    ]
    for b in b11:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))
    story.append(PageBreak())

    # --- SLIDE 12 ---
    slide_header("Defense Anchors", "Individual Defense Roles & Methodological Anchors (Q&A)")
    b12 = [
        "<b>What This Analysis Demonstrates (F):</b> Defensible, auditable 5-year retrospective characterization of respiratory emergency demand, peak timing (May), age co-movement, and care-setting coupling in Chile.",
        "<b>What This Analysis Cannot Claim (H):</b> Does not estimate individual patient risk, true disease incidence, bed occupancy rates, triage wait times, or causal impacts of health campaigns.",
        "<b>Benjamín Pinto — Methodological Lead (G):</b> Processing 2.17M rows; 5 Cs quality audit; duplicate key resolution; date-derived Sunday week starts; statistical correlation analysis (Pearson vs Spearman); parametric vs nonparametric density.",
        "<b>Sebastián Herrera — Selection & Sensitivity Lead (G):</b> Candidate B deselection audit (REM-P2 coverage collapse in June 2020); 581 common-facility panel sensitivity; care-setting breakdown (SAPU vs Hospital); dashboard design & operational framing."
    ]
    for b in b12:
        story.append(Paragraph(f"• &nbsp; {b}", bullet_style))

    doc.build(story)
    print(f"Built PDF presentation: {OUTPUT_PDF}")


def main():
    build_pptx()
    build_pdf()


if __name__ == "__main__":
    main()
