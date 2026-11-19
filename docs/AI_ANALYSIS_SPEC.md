# AI Analysis Specification — Resume Analysis & Salary Estimation

**Document ID:** `DOC-AI-ANALYSIS-SPEC-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `SALARY_ESTIMATION_SPEC.md`, `LABOR_MARKET_DATA_SPEC.md`, `DOC-FUNC-REQ-001`

---

## 1. Purpose

Define how AI is used in the salary estimation product. AI supports resume analysis and skill identification, but **never invents salary figures or statistics**.

## 2. AI Responsibilities

| Responsibility | Description | AI Role |
|:---|:---|:---|
| Resume parsing | Extract skills, experience years, education from PDF/text resume | Assisted extraction |
| Skill identification | Identify technical and soft skills from text | Assisted identification |
| Skill level assessment | Estimate proficiency level ( beginner / intermediate / advanced ) | Assisted assessment |
| Experience extraction | Extract years of experience from work history | Assisted extraction |
| Market comparison | Compare candidate profile against market data | Calculation logic (not AI) |
| Salary computation | Compute range and primary estimate | Calculation logic (not AI) |
| Explanation generation | Explain which factors influenced the estimate | Assisted generation |

## 3. AI Boundaries (Hard Limits)

| Boundary | Rule |
|:---|:---|
| B-01 | AI must never generate a salary number without market data support |
| B-02 | AI must never invent statistics about Iranian job market |
| B-03 | If market data is insufficient, AI must not provide a fallback estimate |
| B-04 | All AI outputs must be reviewed/validated by calculation logic before display |
| B-05 | AI analysis results must carry confidence scores and source attribution |

## 4. AI-Human Collaboration

```
Resume text
    → AI extracts: skills, experience_years, education, job_titles
    → Validation: calculation logic checks extracted data for consistency
    → If AI confidence low: manager prompted to review/correct extracted fields
    → Final profile: manager-validated candidate data
    → Estimation: market data + calculation logic (not AI)
```

## 5. Output from AI Component

| Field | Type | Description |
|:---|:---|:---|
| `extracted_skills` | list | Skills identified from resume |
| `skill_levels` | map | Skill → level (beginner/intermediate/advanced) |
| `extracted_experience_years` | integer | Years of experience |
| `extracted_education` | string | Education level and field |
| `extracted_job_titles` | list | Previous job titles |
| `ai_confidence` | string | `high` \| `medium` \| `low` |
| `requires_manager_review` | boolean | True if AI confidence is low |

## 6. Assumptions (Unresolved)

| ID | Assumption | Owner Decision Needed |
|:---|:---|:---|
| AI-01 | AI model will be local (e.g., Ollama) or API-based | Yes |
| AI-02 | Resume parsing will use structured prompts with JSON output | Yes |
| AI-03 | Manager review step required when AI confidence is low | Yes |
