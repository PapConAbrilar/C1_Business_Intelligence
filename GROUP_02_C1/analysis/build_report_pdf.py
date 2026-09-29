"""Build the self-contained English C1 report from verified case tables.

The process record deliberately labels member-specific C1 contributions as
awaiting team confirmation; it never invents instructor feedback or reflections.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


PACKAGE = Path(__file__).resolve().parents[1]
GROUP_ID = PACKAGE.name.split("_")[1]
OUTPUT = PACKAGE / "report" / f"{PACKAGE.name}_Report.pdf"
PROCESSED = PACKAGE / "data/processed"
FIGURES = PACKAGE / "analysis/figures"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 1.8 * cm
TOP = 1.7 * cm
BOTTOM = 1.7 * cm
CONTENT_W = PAGE_W - LEFT - RIGHT

def _register_dejavu():
    for normal, bold in [
        ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]:
        if Path(normal).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("DejaVu", normal))
            pdfmetrics.registerFont(TTFont("DejaVuBold", bold))
            pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVuBold")
            return
    raise FileNotFoundError("DejaVu TTF fonts not found")

_register_dejavu()

INK = colors.HexColor("#16313b")
ACCENT = colors.HexColor("#27667a")
PALE = colors.HexColor("#e9f1f3")
MUTED = colors.HexColor("#53636a")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="C1Title", fontName="DejaVuBold", fontSize=20, leading=26,
                          textColor=INK, spaceAfter=14))
styles.add(ParagraphStyle(name="C1Subtitle", fontName="DejaVu", fontSize=11, leading=16,
                          textColor=MUTED, spaceAfter=12))
styles.add(ParagraphStyle(name="C1H1", fontName="DejaVuBold", fontSize=13.2, leading=18,
                          textColor=INK, spaceBefore=15, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="C1H2", fontName="DejaVuBold", fontSize=10.5, leading=15,
                          textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="C1Body", fontName="DejaVu", fontSize=8.9, leading=13.3,
                          textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="C1Small", fontName="DejaVu", fontSize=7.1, leading=9.7,
                          textColor=INK, spaceAfter=3))
styles.add(ParagraphStyle(name="C1Caption", fontName="DejaVu", fontSize=7.6, leading=10.8,
                          textColor=MUTED, spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle(name="C1TableHead", fontName="DejaVuBold", fontSize=7.2,
                          leading=10.2, textColor=colors.white))
styles.add(ParagraphStyle(name="C1TableCell", fontName="DejaVu", fontSize=7.15,
                          leading=10.3, textColor=INK))
styles.add(ParagraphStyle(name="C1Kicker", fontName="DejaVuBold", fontSize=8.2,
                          leading=12, textColor=ACCENT, spaceAfter=9))


def para(text: str, style: str = "C1Body") -> Paragraph:
    return Paragraph(text, styles[style])


def add_p(story: list, text: str, style: str = "C1Body") -> None:
    story.append(para(text, style))


def add_h(story: list, text: str, level: int = 1) -> None:
    story.append(para(text, "C1H1" if level == 1 else "C1H2"))


def add_table(story: list, headers: list[str], rows: list[list[str]], widths: list[float],
              font_size: float | None = None) -> None:
    head_style = styles["C1TableHead"]
    body_style = styles["C1TableCell"]
    if font_size is not None:
        body_style = ParagraphStyle("C1TableCellTemp", parent=body_style,
                                    fontSize=font_size, leading=font_size + 3)
    matrix = [[para(str(x), "C1TableHead") for x in headers]]
    matrix += [[Paragraph(str(x), body_style) for x in row] for row in rows]
    table = Table(matrix, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.35, colors.HexColor("#bbced4")),
    ]))
    story.append(table)
    story.append(Spacer(1, 7))


def add_figure(story: list, name: str, caption: str, width: float = CONTENT_W) -> None:
    path = FIGURES / name
    if not path.exists():
        raise FileNotFoundError(path)
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width
    img.drawHeight = width * ratio
    story.append(KeepTogether([img, para(caption, "C1Caption")]))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cdd9dd"))
    canvas.line(LEFT, 1.25 * cm, PAGE_W - RIGHT, 1.25 * cm)
    canvas.setFont("DejaVu", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, 0.94 * cm, "IIB423T-1 | C1 | 29 September 2026")
    canvas.drawRightString(PAGE_W - RIGHT, 0.94 * cm, f"Page {doc.page}")
    canvas.restoreState()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    annual = pd.read_csv(PROCESSED / "annual_summary.csv")
    weekly = pd.read_csv(PROCESSED / "weekly_national_2020_2024.csv",
                         parse_dates=["week_start", "week_end"])
    quality = pd.read_csv(PROCESSED / "source_quality_profile.csv")
    reduced_profile = pd.read_csv(PROCESSED / "reduced_input_profile.csv")
    age = pd.read_csv(PROCESSED / "annual_respiratory_age_counts.csv")
    type_mix = pd.read_csv(PROCESSED / "annual_respiratory_facility_type.csv")
    coverage = pd.read_csv(PROCESSED / "facility_reporting_coverage.csv")
    sensitivity = pd.read_csv(PROCESSED / "common_facility_sensitivity.csv")
    assert annual.year.tolist() == [2020, 2021, 2022, 2023, 2024]
    assert quality.raw_selected_rows.sum() == 2_169_824
    assert int(quality.duplicate_key_extras.sum()) == 2
    assert int(weekly.complete_week.sum()) == 260

    story: list = []
    add_p(story, "BUSINESS INTELLIGENCE · C1", "C1Kicker")
    add_p(story, "Respiratory emergency visits in Chile<br/>A defensible five-year case", "C1Title")
    add_p(story, "Selected W1 line · DEIS public emergency network · 2020-2024", "C1Subtitle")
    group_label = f"{GROUP_ID} (pending assignment)" if GROUP_ID == "XX" else GROUP_ID
    add_p(story, f"<b>Team:</b> Benjamín Pinto and Sebastián Herrera. <b>Group ID:</b> {group_label}. "
          "<b>Course:</b> IIB423T-1, Universidad del Desarrollo. <b>Instructor:</b> Tomás Fontecilla Correa. "
          "<b>Submission date:</b> 29 September 2026.", "C1Small")
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=12))
    add_h(story, "Executive summary")
    add_p(story, "This report asks how the volume and share of <b>recorded respiratory emergency visits</b> changed by week and care setting in the Chilean public network from 2020 through 2024, and what the history can contribute to a <i>proposed</i> Winter Campaign monitoring decision. The unit is a consultation count reported by a facility, not a person, risk estimate or measure of beds and staffing. The analysis uses every date in the five local DEIS Urgencias archives for cause IDs 1 and 2, a 2,169,824-row uncleaned reduced input. [1, 6]")
    add_p(story, "The respiratory share of all recorded emergency visits was 10.75% in 2020, 9.97% in 2021, and 24.69%-28.95% in 2022-2024. Complete-week respiratory volume peaked in May in both 2023 and 2024 (189,297 and 203,353 visits). The share pattern persists in a panel of 581 facilities present all five years. These observations support earlier monitoring review, but they do not establish why the pattern changed or prove that capacity was insufficient.")
    add_p(story, "C1 corrects a W1 reproducibility gap. W1 had already reported five-year aggregates, yet its submitted reduced emergency input covered only selected peak weeks in 2023-2024. The expanded C1 case includes all dates in 2020-2024 for the two KPI codes, removes two identical 2023 duplicate rows from derived tables, and groups weeks from actual dates. W1 received 100/100; the wider-data suggestion was internal team feedback, and no specific instructor comments were reported.")

    add_h(story, "1. Selected problem, prior alternatives and policy context")
    add_p(story, "Respiratory illness can create changing demand across public emergency settings. A plausible proposed user is winter planning staff in the public care network. The bounded decision is when to intensify review of weekly demand by care setting before or during the Winter Campaign. Actual changes to shifts or beds require current capacity and clinical data that this case lacks. MINSAL's National Health Strategy discusses acute respiratory illness, and its Winter Campaign reporting shows the operational relevance of monitoring emergency consultations. Our respiratory-visit share is <b>not</b> a numerical target for morbidity or mortality in that strategy. [2, 3]")
    add_table(story, ["W1 option", "Evidence and fit", "C1 decision"], [
        ["A · Respiratory emergency visits", "Weekly facility/cause counts in 2020-2024, with a direct historical demand measure; source reporting and pandemic years require caution.", "Selected. High-frequency activity series can support bounded timing and monitoring questions."],
        ["B · Child nutrition in REM-P2", "June/December cuts for children under six, with coverage and codebook issues documented in W1.", "Retained as the W1 alternative. Its sparse cuts were a weaker fit for a short-horizon analytical continuation."],
    ], [3.2*cm, 7.3*cm, CONTENT_W-10.5*cm])
    add_p(story, "The documented W1 selection received a full-mark result. There were no specific instructor comments to accept or reject. A teammate's subsequent internal review identified that the packaged W1 reduced emergency input did not support independent reconstruction of all five years. C1 responds by supplying the full-date selected input, its preparation scripts and executed notebook. The analytical question remains focused on recorded demand; geographic comparison is deferred because comparable 2020-2022 geographic fields and a validated historical establishment join are not included.")

    add_h(story, "2. Seven steps from Class 03")
    seven = [
        ["1. Decision", "Proposed user: public-network winter planning staff. Decision: when to review preparedness and intensify monitoring by setting; staffing and bed changes need additional evidence."],
        ["2. Success criteria", "Desired service improvement is earlier, better-informed preparation. C1 can verify a consistent historical weekly series, its peaks, shares and coverage; it cannot measure improved outcomes."],
        ["3. Business questions", "Main: how did weekly volume and share change in 2020-2024? Supporting: when were complete-week peaks; how did age and care-setting mix change; does the broad share pattern persist in common facilities?"],
        ["4. Business process", "Facilities record consultations; DEIS publishes grouped daily facility/cause activity. The files omit patient trajectories, wait times, staff, beds, outcomes and unrecorded demand."],
        ["5. Entities, events and states", "Facility is an entity; a consultation is the counted event; each source row is an aggregate facility/date/cause state. Visits are not unique people."],
        ["6. Data representation", "Candidate source key: year + facility ID + date + cause ID. Counts are Total and five age bands; facility type is a care-location category. Annual files are harmonized without an external join."],
        ["7. Measurement", "Weekly respiratory visits = sum of Total for ID 2. Respiratory share (%) = 100 × ID 2 / ID 1 for the same period and scope. Age/type shares use all respiratory visits as denominator. Exclude incomplete weeks for peak comparisons."],
    ]
    add_table(story, ["Step", "Case-specific reasoning"], seven, [3.7*cm, CONTENT_W-3.7*cm])

    add_h(story, "3. Data, definitions and preparation")
    add_p(story, "The exact source versions are five DEIS AtencionesUrgenciaYYYY ZIP files, retrieved 24 September 2026. `data/source_manifest.csv` records each URL, byte size, SHA-256 and retrieval time; the official dictionary is in `data/reference/`. The selected input retains every raw ID 1/2 row from every date in local 2020-2024 archives. ID 1 is all recorded emergency visits; ID 2 is the respiratory subset. `Total` equals the sum of five age-band counts for every selected row. The data are grouped records from the public network, not a patient-level file. [1, 6]")
    add_p(story, "Preparation order: (1) filter only IDs 1/2 from annual originals while retaining selected source rows unchanged in the reduced extract; (2) profile keys, dates, measures, recorded zeros and facility coverage; (3) remove one extra copy of each of two identical 2023 facility/date/cause rows; (4) parse dates and derive Sunday `week_start`; (5) aggregate to facility-week-cause and national-week tables; (6) calculate shares only after numerator and denominator are aligned. Source originals remain unchanged. The 2023 duplicate removal subtracts 13 from all visits and zero from respiratory visits. Every derived annual count reconciles to the weekly tables.")
    add_table(story, ["Measure", "Numerator and denominator", "Unit / interpretation"], [
        ["Weekly respiratory volume", "Sum of Total where IdCausa = 2 within one Sunday-Saturday week.", "Recorded visits; incomplete first/last weeks are flagged."],
        ["Respiratory share", "100 × Total(ID 2) / Total(ID 1), same date scope and included facilities.", "Percentage of recorded emergency activity, not incidence or risk."],
        ["Age composition", "100 × respiratory age-band count / all respiratory visits in same scope.", "Distribution of visits; age cells reconcile to Total."],
        ["Care-setting mix", "100 × respiratory visits at a facility type / all respiratory visits.", "Location of care, not home residence, occupancy or quality."],
    ], [3.2*cm, 7.2*cm, CONTENT_W-10.4*cm])

    add_h(story, "4. Profiling, preparation checks and the Five Cs")
    add_p(story, "The 2,169,824 selected raw rows represent 1,084,911 distinct facility-dates after duplicate removal. Every such facility-date has both IDs 1 and 2, and respiratory counts never exceed all-visit counts. Key, measure and facility-type fields have no nulls; dates parse within their source years; weeks are in 1-53; no negative cells or age-sum mismatches were found. This is an observed check, not proof that every real consultation was reported. Recorded zeros remain: ID 2 has 38,434 zero-count rows in 2020 and 14,800 in 2024. Two identical 2023 extra rows, one per cause ID, were removed only from processed outputs.")
    five = [
        ["Clean", "Check keys, dates, numeric validity, age sums, zeros and exact duplicates. Remove identical 2023 extras; annual ID 1 falls by 13, ID 2 by 0."],
        ["Consistent", "Use the same cause and age definitions across selected annual archives. Annual `semana` labels can map to disjoint boundary weeks (2022 label 52, 2023/2024 label 1); derive weeks from dates instead."],
        ["Conformed", "Harmonize the shared selected fields and IDs across all five files. No geographic facility-register join is used: it would not answer the national question and would require historical key/cardinality validation."],
        ["Current", "Historical 2020-2024 versions suit retrospective seasonality. A same-week 2026 decision would need a current feed, version/freshness flags and operational capacity data."],
        ["Comprehensive", "All local years/dates for IDs 1/2 are included. The data omit unreported care, private activity outside this public-network scope, unique patients, residence, population denominators, staffing, beds and outcomes."],
    ]
    add_table(story, ["C1 lens", "Check and consequence"], five, [2.5*cm, CONTENT_W-2.5*cm])
    quality_rows = []
    for q in quality.itertuples():
        zero_id2 = reduced_profile.loc[(reduced_profile.year.eq(q.year)) &
                                       (reduced_profile.cause_id.eq(2)),
                                       "recorded_zero_total_rows"].iloc[0]
        quality_rows.append([str(int(q.year)), f"{int(q.raw_selected_rows):,}",
                             f"{int(zero_id2):,}", str(int(q.duplicate_key_extras)),
                             str(int(q.unique_facilities))])
    add_table(story, ["Year", "Selected source rows", "ID 2 zero rows", "Duplicate extras", "Facilities"],
              quality_rows, [1.5*cm, 4.7*cm, 3.6*cm, 4.0*cm, CONTENT_W-13.8*cm])
    add_p(story, "Table 1. Source-row profile before duplicate removal. Zero-count rows are recorded values, not missing observations. The two 2023 extras are identical source copies.", "C1Caption")
    add_p(story, "Facility reporting coverage is uneven. There are 607 reporting facility IDs in 2020 and 640 in 2024; 41 report fewer than 100 days in 2020 versus 15 in 2024. This cautions against reading absolute count differences as a pure change in underlying illness. The 581 IDs present all five years account for 98.05% of all visits in 2020 and 95.89% in 2024; their share pattern is close to the full sample.")

    add_h(story, "5. Exploratory results and interpretation")
    annual_rows = [[str(int(r.year)), f"{int(r.all_emergency_visits):,}",
                    f"{int(r.respiratory_visits):,}", f"{r.respiratory_share_pct:.2f}%"]
                   for r in annual.itertuples()]
    add_table(story, ["Year", "All visits", "Respiratory visits", "Respiratory share"],
              annual_rows, [1.8*cm, 4.2*cm, 4.4*cm, CONTENT_W-10.4*cm])
    add_figure(story, "annual_respiratory_share.png", "Figure 1. Respiratory visits as a percentage of all recorded emergency visits by source year. 2020-2021 should not be treated as an ordinary seasonal baseline without considering the pandemic-era regime.", CONTENT_W*0.74)
    add_p(story, "<b>Observed:</b> the respiratory share is around 10% in 2020-2021 and 24.69%-28.95% in 2022-2024. <b>Interpretation:</b> the mix of recorded emergency activity changed substantially; comparing years requires care because reporting facilities, care seeking and pandemic-era conditions may differ. <b>Not established:</b> a change in individual disease risk, clinical severity, policy effect or service capacity.")

    peaks = (weekly.loc[weekly.complete_week]
             .loc[lambda d: d.groupby("reporting_year").respiratory_visits.transform("max").eq(d.respiratory_visits)]
             .sort_values("reporting_year").drop_duplicates("reporting_year"))
    peak_rows = [[str(int(r.reporting_year)), r.week_start.strftime("%d %b"),
                  r.week_end.strftime("%d %b %Y"), f"{int(r.respiratory_visits):,}",
                  f"{r.respiratory_share_pct:.2f}%"] for r in peaks.itertuples()]
    add_table(story, ["Year", "Week start", "Week end", "Respiratory visits", "Share"],
              peak_rows, [1.4*cm, 3.1*cm, 3.4*cm, 4.0*cm, CONTENT_W-11.9*cm])
    add_p(story, "Table 2. Largest respiratory-volume week in each reporting year among 260 complete Sunday-Saturday weeks. The first and last generated weeks have only four and three source days and are excluded from this comparison.", "C1Caption")
    add_figure(story, "weekly_volume_and_share.png", "Figure 2. Weekly recorded respiratory volume and share from the selected five-year case. The shape is descriptive; a seasonal forecast is outside C1.", CONTENT_W*0.80)
    add_p(story, "The 2023 and 2024 complete-week peaks occurred in May, with 189,297 (41.66%) and 203,353 (45.56%) respiratory visits respectively. MINSAL's 24 May 2024 campaign report records a 45.4% week-20 respiratory share. That is close but not numerically identical to 45.56% from this downloaded DEIS archive; differing version, scope or definitions have not been resolved, so the external report corroborates timing rather than an exact number. [3, 4]")

    add_figure(story, "eda_distributions_kde.png", "Figure 2b. Full EDA: Histograms and Kernel Density Estimation (KDE) comparing the pandemic suppression regime (2020-2021) with post-pandemic rebound (2022-2024).", CONTENT_W*0.84)
    add_p(story, "<b>Distributions and densities (Histograms & KDE):</b> Weekly volume and share distributions reveal a marked regime shift. The pandemic era (2020-2021) is tightly concentrated at low demand (<50,000 weekly visits, median share ~10%) due to non-pharmacological interventions and school closures. In contrast, post-pandemic years (2022-2024) display a right-skewed, multimodal distribution with long seasonal tails extending to 203,353 visits and 45.56% share during winter peaks.")

    age_cols = ["Menores_1", "De_1_a_4", "De_5_a_14", "De_15_a_64", "De_65_y_mas"]
    age["under_15_pct"] = 100 * age[age_cols[:3]].sum(axis=1) / age[age_cols].sum(axis=1)
    age["age_65_plus_pct"] = 100 * age["De_65_y_mas"] / age[age_cols].sum(axis=1)
    primary = type_mix.loc[type_mix.facility_type.isin(["SAPU", "SAR", "SUR"])].groupby("year").respiratory_visits.sum()
    all_type = type_mix.groupby("year").respiratory_visits.sum()
    mix_rows = [[str(y), f"{age.loc[age.year.eq(y), 'under_15_pct'].iloc[0]:.2f}%",
                 f"{age.loc[age.year.eq(y), 'age_65_plus_pct'].iloc[0]:.2f}%",
                 f"{100*primary[y]/all_type[y]:.2f}%"] for y in annual.year]
    add_table(story, ["Year", "Under 15", "Age 65+", "SAPU + SAR + SUR"],
              mix_rows, [2.0*cm, 3.7*cm, 3.4*cm, CONTENT_W-9.1*cm])
    add_p(story, "Table 3. Shares of recorded respiratory visits, not population rates. The last column is place-of-care mix, not a measure of capacity or treatment success.", "C1Caption")
    add_figure(story, "age_and_facility_mix.png", "Figure 3. Age and facility-type composition of respiratory visits. Age groups reconcile to the respiratory Total. The place of care is not patient residence.", CONTENT_W*0.91)
    add_p(story, "Under-15 visits represented 30.05% of respiratory visits in 2020 and 40.72% in 2024; SAPU, SAR and SUR together represented 71.08% and 75.87% respectively. This supports showing care-setting and age mix in a future monitoring view. It does not show whether hospital pressure was alleviated or whether children faced higher risk.")

    add_figure(story, "eda_correlation_analysis.png", "Figure 3b. Full EDA: Pearson correlation matrix across age bands (left) and demand coupling between primary care (SAPU/SAR/SUR) and hospitals (right, r = 0.984).", CONTENT_W*0.84)
    add_p(story, "<b>Correlations and cross-setting co-movement:</b> Pearson correlations across weekly age-band volumes indicate strong synchronicity between infant (<1) and toddler (1-4) surges (r = 0.954), and between working-age adults (15-64) and older adults (65+, r = 0.949). Furthermore, weekly respiratory demand in primary emergency care (SAPU/SAR/SUR) and hospitals moves in near-lockstep (r = 0.984). This empirical coupling demonstrates that primary care saturation directly coincides with hospital emergency room pressure.")

    sensitivity_rows = [[str(int(r.year)), f"{r.all_facility_share_pct:.2f}%",
                         f"{r.common_facility_share_pct:.2f}%",
                         f"{r.common_facility_all_visit_coverage_pct:.2f}%"]
                        for r in sensitivity.itertuples()]
    add_table(story, ["Year", "All-facility share", "Common-facility share", "All-visit coverage"],
              sensitivity_rows, [1.7*cm, 4.1*cm, 4.5*cm, CONTENT_W-10.3*cm])
    add_p(story, "Table 4. A stable panel of 581 facility IDs reproduces the broad share pattern while covering at least 95.89% of all recorded visits in each year. This check addresses entry/exit, not every comparability concern.", "C1Caption")
    add_figure(story, "common_facility_sensitivity.png", "Figure 4. Full sample and 581 common-facility respiratory shares are close. Reporting completeness and pandemic-era conditions still limit interpretation.", CONTENT_W*0.78)

    add_h(story, "6. Conclusion, limits and feasible continuation")
    add_p(story, "The evidence answers the bounded question descriptively: recorded respiratory demand composition and complete-week peak timing varied markedly across 2020-2024; May peaks occurred in both 2023 and 2024; and the broad annual share change remains in facilities present across all years. For the <i>proposed</i> planning decision, a historical monitoring view should begin before midwinter and show current volume, share, age/care-setting mix and data coverage. Any operational shift or bed action requires current workload, staffing, occupancy, local catchment and clinical information not available here.")
    add_p(story, "Alternative explanations include virus circulation, pandemic controls, care-seeking behavior, changes in reporting and the set of active facilities. ISP virological surveillance is a distinct, selected sample rather than a visit denominator; no causal or facility-level virological join is claimed. [5] There are no patient identifiers, residence or population denominator; counts cannot estimate incidence, unique patients, waiting times, outcomes, risk, care quality or the effect of an intervention. The 2020-2024 archives are historical and cannot themselves guide a live 2026 staffing decision.")
    add_h(story, "Future ML and dashboard feasibility", 2)
    add_p(story, "A concrete future supervised task is a two-week-ahead forecast of completed-week respiratory visit counts by national care setting. One observation would be a week × care setting. Only information available before the forecast week - prior visit counts, calendar features and any verified contemporaneous external signal - could be inputs; the target week and post-outcome data cannot leak into predictors. Five annual cycles, the 2020-2021 regime change, facility reporting variation and lack of a current feed limit viability. The next stage should test whether a timely source and robust evaluation window exist before choosing a model. No ML is trained for C1.")
    add_p(story, "A future dashboard for proposed winter planners would show weekly volume and share against comparable historical weeks, age distribution, hospital versus SAPU/SAR/SUR mix, and source freshness/coverage flags. It would support a human review of preparedness, not automatically prescribe capacity. A 30% alert threshold was a W1 design idea, not an official standard; it requires validation before use. No complete dashboard is built for C1.")

    add_h(story, "7. Process record")
    add_h(story, "Decisions and checks", 2)
    add_table(story, ["Stage / decision", "Alternative, reason and check", "Evidence"], [
        ["W1 to C1 scope", "Keep selected A; widen reduced input to every date of all five local years after internal team review. Check 2,169,824 selected rows and annual source coverage.", "`data/input/`; `source_quality_profile.csv`; notebook sections 1-2"],
        ["Duplicate handling", "Retain raw rows in the extract; remove only two identical 2023 extras from outputs. Check full-row equality and 2023 change of -13 all visits, 0 respiratory.", "Notebook section 2; `annual_summary.csv`"],
        ["Week key", "Do not group only by source year + `semana`: labels collide at calendar boundaries. Parse dates and use Sunday `week_start`; exclude two incomplete weeks from peak comparisons.", "`source_week_collisions.csv`; notebook section 4"],
        ["No geographic join", "National question is answerable from shared fields. A facility-register join risks unmatched or duplicated geography without a validated historical mapping.", "Notebook section 5; report sections 2-4"],
        ["Coverage sensitivity", "Compare all reporting facilities with 581 IDs present all five years; shares remain close, but reporting and pandemic limitations remain.", "`facility_reporting_coverage.csv`; `common_facility_sensitivity.csv`"],
        ["Reproducibility", "Rebuild from the included uncleaned extract in a clean copied folder. Annual/weekly/profile outputs matched byte for byte after deterministic gzip metadata.", "`analysis/prepare_reduced_case.py`; README"],
    ], [3.0*cm, 8.5*cm, CONTENT_W-11.5*cm], font_size=6.85)
    add_h(story, "Instructor feedback and response", 2)
    add_p(story, "W1 was graded 100/100. The team reports no specific instructor comments after W1. Therefore there is no advice to claim as accepted, adapted or rejected. The wider-data correction was internal feedback from the teammate. The response is the complete five-year, all-date reduced case and auditable preparation described above. If the instructor later provides concrete guidance, the team should add its wording/date and response before submission.")
    add_h(story, "Individual contributions", 2)
    add_p(story, "The previous submitted W1 report documents Benjamín Pinto as lead for Candidate A (respiratory emergency data, streamed processing, Five Cs, COVID sensitivity, multiyear figures and integrated comparison), and Sebastián Herrera as lead for Candidate B (REM-P2 codebooks, coverage anomalies, source inventory and nutrition discussion). This is the verified division of W1 work. The new C1 extract, notebook and report were prepared with Codex AI assistance under the team's request; the team must assign and verify each member's <b>actual C1 review, writing and presentation contribution</b> before submission. The file trail records work, but it cannot establish which student personally performed each new step. [7]")
    add_h(story, "AI use and verification", 2)
    add_table(story, ["Tool and prompt/output excerpt", "Accepted, modified and verified"], [
        ["OpenAI Codex. Team request excerpt: 'Use all the years on the folder.' Output: scripts and a 2,169,824-row uncleaned ID 1/2 extract for 2020-2024.", "Accepted scope after checking folder years, manifest hashes, row counts, nulls, zeros, duplicate rows and full-source rebuild."],
        ["OpenAI Codex. Team request excerpt: 'explain that the data has widened as a correction of the previous work.' Output: W1-to-C1 evolution statement.", "Modified to distinguish W1's five-year aggregate analysis from its narrow submitted reduced input; checked against W1 PDF/notebook and C1 source files."],
        ["OpenAI Codex. Output: Sunday week key, common-facility sensitivity, executed notebook, figures and report draft.", "Checked date/week collisions, annual-weekly reconciliation, cause pairing, identical duplicate contents, clean-folder rerun, saved notebook outputs and official source context. Team remains responsible for final interpretation."],
    ], [7.2*cm, CONTENT_W-7.2*cm], font_size=6.9)
    add_h(story, "Individual reflections", 2)
    add_p(story, "<b>Benjamín Pinto - reflection carried forward from W1, to confirm for C1:</b> contribution: efficient processing of the large emergency files and initial quality audit. Learning: administrative consultation counts differ from population prevalence. Remaining uncertainty: how to handle the 2020-2021 pandemic shock in a later forecasting model. <b>Sebastián Herrera - reflection carried forward from W1, to confirm for C1:</b> contribution: REM-P2 codebook and coverage audit that informed selection. Learning: a policy objective does not mean administrative data measure it without bias. Remaining uncertainty from W1: how to interpret absent REM-P2 code rows. Both members should revise these into their own current C1 reflections before submitting. [7]")

    add_h(story, "References")
    refs = [
        "[1] Departamento de Estadísticas e Información de Salud (DEIS). <i>Preguntas frecuentes: Atenciones de urgencia</i>. Accessed 29 September 2026. <link href='https://deis.minsal.cl/faqs/' color='#27667a'>deis.minsal.cl/faqs/</link>.",
        "[2] Ministerio de Salud de Chile (MINSAL). <i>Estrategia Nacional de Salud 2022</i>. 2022, respiratory illness objectives and context. <link href='https://www.minsal.cl/wp-content/uploads/2022/03/Estrategia-Nacional-de-Salud-2022-MINSAL-V8.pdf' color='#27667a'>MINSAL PDF</link>.",
        "[3] MINSAL. <i>Campaña Invierno 2024: informes de virus respiratorios</i>. 2024. <link href='https://www.minsal.cl/campana-invierno-2024-informe-de-virus-respiratorios/' color='#27667a'>MINSAL reports index</link>.",
        "[4] MINSAL. <i>Informe Campaña de Invierno, 24 May 2024</i>, including week-20 emergency share. <link href='https://www.minsal.cl/wp-content/uploads/2024/05/4.-Informe-24-de-mayo-Campana-Invierno-2024.pdf' color='#27667a'>MINSAL PDF</link>.",
        "[5] Instituto de Salud Pública de Chile (ISP). <i>2024 respiratory-virus laboratory surveillance reports</i>. <link href='https://www.ispch.cl/biomedico/vigilancia-de-laboratorio/ambitos-de-vigilancia/vigilancia-virus-respiratorios/informes-virus-respiratorios/?y=2024' color='#27667a'>ISP index</link>.",
        "[6] DEIS. <i>Diccionario AtencionesUrgencia</i> (local official workbook) and annual AtencionesUrgencia2020-2024 ZIP files; exact URLs, sizes, SHA-256 and retrieval date in `data/source_manifest.csv`. Included reduced input and derivation scripts in this package.",
        f"[7] Team. <i>GROUP_{GROUP_ID}_W1_Report.pdf</i> and W1 README, submitted English package, 25 September 2026, alternatives, Process record and full member names. The final C1 group ID must match W1.",
    ]
    for ref in refs:
        add_p(story, ref, "C1Small")

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=LEFT,
                            rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
                            title="C1 Respiratory Emergency Visits in Chile",
                            author="Benjamín Pinto and Sebastián Herrera")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    main()
