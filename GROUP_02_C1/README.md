# Certamen 1 (C1) · Submission Package

**Team:** Benjamín Pinto and Sebastián Herrera  
**Group:** 02  
**Date:** September 29, 2026  
**Course:** Business Intelligence (IIB423T-1) — Universidad del Desarrollo  
**Instructor:** Tomás Fontecilla Correa  

---

## 1. Project Overview & Selected Line

- **Topic:** Seasonal demand and capacity planning for respiratory emergencies in Chile (2020–2024), supporting the MINSAL Winter Campaign (*Campaña de Invierno*).
- **Core KPI:** 
  $$\text{Respiratory Share (\%)} = \frac{\text{Total Urgencias Respiratorias (IdCausa = 2)}}{\text{Total Urgencias (IdCausa = 1)}} \times 100$$
- **Target Users:** Directorate for Health Care Network Management (DIGERA), Health Service directors, and emergency network administrators (SAPU, SAR, SUR, and Hospitals).
- **Key Decision:** Anticipating staffing needs (physicians, nurses, respiratory therapists), phased pediatric/adult critical bed conversions, and primary care triage diversion to prevent hospital emergency room saturation.

---

## 2. Directory Structure

```text
GROUP_02_C1/
├── README.md                           # Package entry point and instructions
├── report/
│   ├── GROUP_02_C1_Report.pdf          # Self-contained standalone report
│   └── GROUP_02_C1_Report.docx         # Editable source document
├── presentation/
│   └── GROUP_02_C1_Slides.pdf          # Defense slides
├── analysis/
│   ├── requirements.txt                # Python environment dependencies
│   ├── urgencias_respiratorias_c1.ipynb# Full EDA notebook with executed outputs
│   ├── build_reduced_inputs.py         # Filters for generating reduced test cases
│   ├── verify_reduced_case.py          # Script to reproduce verification checks
│   ├── audit_duplicate_keys.py         # Full-source key duplicate audit
│   └── download_required_sources.py    # Downloads official DEIS ZIPs with SHA-256 checks
└── data/
    ├── input/                          # Uncleaned reduced extracts
    ├── processed/                      # Spot checks and generated EDA summary tables
    ├── reference/                      # Official data dictionaries and assignment brief
    └── source_manifest.csv             # URLs, download timestamps, and SHA-256 checksums
```

---

## 3. Reproduction & Setup

```bash
# Install dependencies
python -m pip install -r analysis/requirements.txt

# Run verification checks
python analysis/verify_reduced_case.py
```
