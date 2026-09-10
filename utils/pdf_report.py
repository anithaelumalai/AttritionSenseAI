import io
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(
    emp_record: Dict[str, Any],
    pred_result: Dict[str, Any],
    recommendations: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a professional executive PDF attrition risk assessment report.
    Returns the PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    primary_color = colors.HexColor("#1e3a8a")  # Deep Corporate Blue
    accent_color = colors.HexColor("#0284c7")   # Light Sky Blue
    dark_gray = colors.HexColor("#1f2937")
    light_bg = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#cbd5e1")
    
    # Determine Risk Banner Color
    risk_level = str(pred_result.get("risk_level", "LOW RISK")).upper()
    if "HIGH" in risk_level:
        risk_banner_bg = colors.HexColor("#fee2e2")
        risk_banner_text = colors.HexColor("#991b1b")
        risk_badge_border = colors.HexColor("#f87171")
    elif risk_level == "MEDIUM RISK":
        risk_banner_bg = colors.HexColor("#fef3c7")
        risk_banner_text = colors.HexColor("#92400e")
        risk_badge_border = colors.HexColor("#fbbf24")
    else:
        risk_banner_bg = colors.HexColor("#dcfce7")
        risk_banner_text = colors.HexColor("#166534")
        risk_badge_border = colors.HexColor("#4ade80")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b")
    )
    
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceAfter=6
    )
    
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=dark_gray
    )
    
    body_text = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=dark_gray
    )
    
    banner_style = ParagraphStyle(
        "BannerStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=risk_banner_text,
        alignment=1  # Centered
    )

    story = []
    
    # 1. Header
    story.append(Paragraph("AttritionSense AI", title_style))
    story.append(Paragraph("Confidential Employee Attrition Prediction & Retention Assessment Report", subtitle_style))
    report_date = datetime.now().strftime("%B %d, %Y - %H:%M")
    story.append(Paragraph(f"Generated on: {report_date} | Authorized HR Personnel Copy", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=14))
    
    # 2. Risk Level Banner
    risk_score = pred_result.get("risk_score", 0.0)
    prob_pct = round(pred_result.get("attrition_probability", 0.0) * 100, 1)
    prediction_text = pred_result.get("prediction", "Unknown")
    
    banner_content = [
        [
            Paragraph(
                f"<b>EXECUTIVE ASSESSMENT: {risk_level}</b><br/>"
                f"Prediction: {prediction_text} | Risk Score: {risk_score}/100 | Attrition Probability: {prob_pct}%",
                banner_style
            )
        ]
    ]
    banner_table = Table(banner_content, colWidths=[532])
    banner_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), risk_banner_bg),
        ("BOX", (0, 0), (-1, -1), 1.5, risk_badge_border),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 16))
    
    # 3. Employee Profile Summary Table
    story.append(Paragraph("1. Employee Profile Summary", section_heading))
    
    emp_id = emp_record.get("EmployeeNumber", "N/A")
    dept = emp_record.get("Department", "N/A")
    role = emp_record.get("JobRole", "N/A")
    age = emp_record.get("Age", "N/A")
    gender = emp_record.get("Gender", "N/A")
    income = f"${emp_record.get('MonthlyIncome', 0):,}"
    job_level = emp_record.get("JobLevel", "N/A")
    overtime = emp_record.get("OverTime", "N/A")
    job_sat = f"{emp_record.get('JobSatisfaction', 'N/A')}/4"
    env_sat = f"{emp_record.get('EnvironmentSatisfaction', 'N/A')}/4"
    wlb = f"{emp_record.get('WorkLifeBalance', 'N/A')}/4"
    tenure = f"{emp_record.get('YearsAtCompany', 'N/A')} yrs"
    role_tenure = f"{emp_record.get('YearsInCurrentRole', 'N/A')} yrs"
    promotion = f"{emp_record.get('YearsSinceLastPromotion', 'N/A')} yrs ago"
    mgr_tenure = f"{emp_record.get('YearsWithCurrManager', 'N/A')} yrs"
    
    profile_data = [
        [Paragraph("Employee ID:", body_bold), Paragraph(str(emp_id), body_text),
         Paragraph("Department:", body_bold), Paragraph(str(dept), body_text)],
        [Paragraph("Job Role:", body_bold), Paragraph(str(role), body_text),
         Paragraph("Age / Gender:", body_bold), Paragraph(f"{age} / {gender}", body_text)],
        [Paragraph("Monthly Income:", body_bold), Paragraph(income, body_text),
         Paragraph("Job Level:", body_bold), Paragraph(str(job_level), body_text)],
        [Paragraph("OverTime:", body_bold), Paragraph(str(overtime), body_text),
         Paragraph("Work-Life Balance:", body_bold), Paragraph(wlb, body_text)],
        [Paragraph("Job Satisfaction:", body_bold), Paragraph(job_sat, body_text),
         Paragraph("Environment Sat.:", body_bold), Paragraph(env_sat, body_text)],
        [Paragraph("Years at Company:", body_bold), Paragraph(tenure, body_text),
         Paragraph("Years in Role:", body_bold), Paragraph(role_tenure, body_text)],
        [Paragraph("Years Last Promo:", body_bold), Paragraph(promotion, body_text),
         Paragraph("With Current Mgr:", body_bold), Paragraph(mgr_tenure, body_text)],
    ]
    
    profile_table = Table(profile_data, colWidths=[110, 156, 110, 156])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 16))
    
    # 4. Detected Attrition Risk Factors
    story.append(Paragraph("2. Detected Attrition Risk Factors", section_heading))
    risk_factors = pred_result.get("risk_factors", [])
    if risk_factors:
        factors_data = [[
            Paragraph("Risk Factor", body_bold),
            Paragraph("Severity", body_bold),
            Paragraph("Context & Detail", body_bold)
        ]]
        for f in risk_factors:
            sev = f.get("severity", "Medium")
            factors_data.append([
                Paragraph(f"<b>{f.get('factor', '')}</b>", body_text),
                Paragraph(f"<b>{sev}</b>", body_bold),
                Paragraph(f.get("detail", ""), body_text)
            ])
        factors_table = Table(factors_data, colWidths=[150, 70, 312])
        factors_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(factors_table)
    else:
        story.append(Paragraph("No critical attrition risk drivers detected. Baseline engagement indicators remain solid.", body_text))
        
    story.append(Spacer(1, 16))
    
    # 5. Targeted Retention Recommendations
    story.append(Paragraph("3. Prescriptive Retention Action Plan", section_heading))
    if recommendations:
        recs_data = [[
            Paragraph("Category", body_bold),
            Paragraph("Recommended Action", body_bold),
            Paragraph("Priority & Target", body_bold)
        ]]
        for r in recommendations:
            recs_data.append([
                Paragraph(f"<b>{r.get('category', '')}</b>", body_text),
                Paragraph(f"<b>{r.get('title', '')}</b><br/>{r.get('action', '')}", body_text),
                Paragraph(f"<b>{r.get('priority', '')}</b><br/><i>Owner: {r.get('owner', '')}</i>", body_text)
            ])
        recs_table = Table(recs_data, colWidths=[120, 272, 140])
        recs_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(recs_table)
    else:
        story.append(Paragraph("Continue standard high-performance recognition and quarterly development touchpoints.", body_text))
        
    story.append(Spacer(1, 20))
    
    # 6. Sign-off and Disclaimer Block
    sign_off_data = [
        [
            Paragraph("<b>HR Reviewer Signature:</b> ___________________________", body_text),
            Paragraph("<b>Date of Review:</b> ___________________________", body_text)
        ],
        [
            Paragraph("<b>Action Plan Follow-up Target Date:</b> ___________________________", body_text),
            Paragraph("<b>HR Case Status:</b> [  ] Pending  [  ] In Progress  [  ] Resolved", body_text)
        ]
    ]
    sign_table = Table(sign_off_data, colWidths=[266, 266])
    sign_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    
    story.append(KeepTogether([
        Paragraph("4. HR Governance & Action Sign-Off", section_heading),
        Spacer(1, 4),
        sign_table,
        Spacer(1, 10),
        Paragraph(
            "<i>CONFIDENTIAL NOTICE: This document contains proprietary predictive analytics generated by AttritionSense AI. "
            "It is intended solely for authorized HR business partners for voluntary employee engagement and retention planning.</i>",
            subtitle_style
        )
    ]))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
