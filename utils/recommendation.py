import os
import sys
from typing import Dict, Any, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def generate_retention_recommendations(emp_record: Dict[str, Any], risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates targeted, actionable retention recommendations based strictly
    on the employee's verified attributes and detected risk drivers.
    """
    recommendations = []
    
    # 1. Overtime / Workload Burnout
    has_overtime = any(f["factor"] == "Frequent Overtime" for f in risk_factors)
    wlb_issue = any(f["factor"] == "Suboptimal Work-Life Balance" for f in risk_factors)
    if has_overtime or wlb_issue:
        recommendations.append({
            "category": "Workload & Work-Life Balance",
            "title": "Overtime Cap & Flexible Scheduling",
            "action": "Implement a workload redistribution review to cap weekly overtime. Introduce hybrid or flexible working hours to alleviate personal schedule pressure.",
            "priority": "Immediate (Within 7 Days)",
            "owner": "Direct Manager & HR Business Partner"
        })
        
    # 2. Career Stagnation / Promotion Delay
    promo_stagnation = any(f["factor"] == "Career Progression Stagnation" for f in risk_factors)
    years_role = emp_record.get("YearsInCurrentRole", 0)
    if promo_stagnation or years_role >= 4:
        recommendations.append({
            "category": "Career Growth & Mobility",
            "title": "Clear Promotion Track & Lateral Stretch Projects",
            "action": "Convene a formal career development planning session. Establish milestones for next-level readiness or offer a lateral rotation to rejuvenate engagement.",
            "priority": "High (Within 14 Days)",
            "owner": "Department Head & Talent Lead"
        })
        
    # 3. Job Satisfaction & Involvement
    job_sat_issue = any(f["factor"] == "Low Job Satisfaction" for f in risk_factors)
    job_involvement = emp_record.get("JobInvolvement", 3)
    if job_sat_issue or job_involvement <= 2:
        recommendations.append({
            "category": "Engagement & Role Adjustment",
            "title": "Role Re-alignment & Responsibility Review",
            "action": "Conduct a 1-on-1 discovery interview to identify friction points in daily tasks. Realign responsibilities toward high-impact, energizing projects.",
            "priority": "High (Within 14 Days)",
            "owner": "Direct Manager"
        })
        
    # 4. Workplace Culture / Environment
    env_issue = any(f["factor"] == "Low Workplace Environment Satisfaction" for f in risk_factors)
    if env_issue:
        recommendations.append({
            "category": "Workplace Culture",
            "title": "Team Climate Assessment & Ergonomic/Physical Environment Check",
            "action": "Address workplace culture dynamics in the team. Review team collaboration tools and physical work conditions to ensure a supportive environment.",
            "priority": "Medium (Within 30 Days)",
            "owner": "HR Operations & People Partner"
        })
        
    # 5. Compensation & Equity Alignment
    hike_issue = any(f["factor"] == "Below-Average Salary Increment" for f in risk_factors)
    zero_stock = any(f["factor"] == "Zero Equity Retention Tie" for f in risk_factors)
    monthly_inc = emp_record.get("MonthlyIncome", 0)
    if hike_issue or zero_stock or monthly_inc < 3500:
        recommendations.append({
            "category": "Compensation & Recognition",
            "title": "Out-of-Cycle Compensation Benchmarking & Retention Bonus",
            "action": "Review current total rewards against peer market benchmarks. Evaluate eligibility for spot performance bonuses, stock grant allocation, or retention incentives.",
            "priority": "Medium (Within 30 Days)",
            "owner": "Compensation & Benefits Committee"
        })
        
    # 6. Commute Distance / Travel Stress
    commute_issue = any(f["factor"] == "Long Daily Commute" for f in risk_factors)
    travel_issue = any(f["factor"] == "High Travel Burden" for f in risk_factors)
    if commute_issue or travel_issue:
        recommendations.append({
            "category": "Workplace Flexibility",
            "title": "Remote Work Flexibility & Travel Schedule Optimization",
            "action": f"Provide 2-3 remote work days per week to eliminate daily {emp_record.get('DistanceFromHome', 0)}-mile commute stress. Re-evaluate required business trips.",
            "priority": "Immediate (Within 7 Days)",
            "owner": "Direct Manager"
        })
        
    # 7. Manager Relationship / Transition Support
    mgr_transition = any(f["factor"] == "Recent Manager Transition" for f in risk_factors)
    rel_sat = emp_record.get("RelationshipSatisfaction", 3)
    if mgr_transition or rel_sat <= 2:
        recommendations.append({
            "category": "Leadership & Mentorship",
            "title": "Manager Check-In Cadence & Executive Mentorship",
            "action": "Institute bi-weekly structured 1-on-1 check-ins focused on mutual feedback and support. Pair employee with a senior cross-functional mentor.",
            "priority": "Medium (Within 21 Days)",
            "owner": "People & Culture / Leadership Coaching"
        })
        
    # Default positive reinforcement if low risk / few negative factors
    if not recommendations:
        recommendations.append({
            "category": "Retention Sustenance & Recognition",
            "title": "Sustained Recognition & High-Impact Leadership Pipeline",
            "action": "Acknowledge stellar performance and tenure consistency. Involve employee in strategic planning and nominate for leadership accelerator initiatives.",
            "priority": "Routine (Quarterly Review)",
            "owner": "Leadership Team"
        })
        
    return recommendations
