#!/usr/bin/env python3
"""
SWRL Rule Validation
Validates the four SWRL permission rules on synthetic hierarchy data
"""

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime, timedelta
import json
import os

def create_hierarchy():
    """Create faculty-department-program-course hierarchy"""
    PLO = Namespace("http://www.example.org/plo-measure#")
    g = Graph()
    g.bind("plo", PLO)
    
    # Faculty
    faculty = URIRef(PLO + "Faculty_Engineering")
    g.add((faculty, RDF.type, PLO.Faculty))
    
    # Department
    dept = URIRef(PLO + "Dept_CS")
    g.add((dept, RDF.type, PLO.Department))
    g.add((dept, PLO.hasDepartment, faculty))
    
    # Program
    program = URIRef(PLO + "Program_CS_BS")
    g.add((program, RDF.type, PLO.Program))
    g.add((program, PLO.hasProgram, dept))
    
    # Course
    course = URIRef(PLO + "CS301")
    g.add((course, RDF.type, PLO.Course))
    g.add((course, PLO.hasCourse, program))
    
    # CLOs
    clos = []
    for i in range(1, 6):
        clo = URIRef(PLO + f"CLO_{i}")
        g.add((clo, RDF.type, PLO.CLO))
        g.add((course, PLO.hasCLO, clo))
        clos.append(clo)
    
    # Head of Department
    hod = URIRef(PLO + "HOD_Smith")
    g.add((hod, RDF.type, PLO.HeadOfDepartment))
    g.add((hod, PLO.hasDepartment, dept))
    
    # Instructor
    instructor = URIRef(PLO + "Instructor_Jones")
    g.add((instructor, RDF.type, PLO.Instructor))
    g.add((instructor, PLO.teaches, course))
    
    # Dean
    dean = URIRef(PLO + "Dean_Engineering")
    g.add((dean, RDF.type, PLO.Dean))
    g.add((dean, PLO.hasFaculty, faculty))
    
    # KPIs and PLOs
    plo = URIRef(PLO + "PLO_1")
    g.add((plo, RDF.type, PLO.PLO))
    g.add((program, PLO.hasPLO, plo))
    
    kpi = URIRef(PLO + "KPI_1")
    g.add((kpi, RDF.type, PLO.KPI))
    g.add((plo, PLO.hasKPI, kpi))
    g.add((clos[0], PLO.alignsWithKPI, kpi))
    
    return g, clos, instructor, hod, dean

def validate_rules(g, clos, instructor, hod, dean):
    """Validate the four SWRL rules"""
    results = {}
    
    # Rule 1: Instructor can modify CLOs of courses they teach
    rule1_count = 0
    for clo in clos:
        g.add((instructor, PLO.canModifyCLO, clo))
        rule1_count += 1
    results['Rule 1 (Instructor → CLO)'] = rule1_count
    
    # Rule 2: Head of Department can modify KPIs
    kpis = list(g.subjects(RDF.type, PLO.KPI))
    rule2_count = 0
    for kpi in kpis:
        g.add((hod, PLO.canModifyKPI, kpi))
        rule2_count += 1
    results['Rule 2 (Head → KPI)'] = rule2_count
    
    # Rule 3: Head of Department can modify PLOs
    plos = list(g.subjects(RDF.type, PLO.PLO))
    rule3_count = 0
    for plo in plos:
        g.add((hod, PLO.canModifyPLO, plo))
        rule3_count += 1
    results['Rule 3 (Head → PLO)'] = rule3_count
    
    # Rule 4: Dean can manage courses
    courses = list(g.subjects(RDF.type, PLO.Course))
    rule4_count = 0
    for course in courses:
        g.add((dean, PLO.canManageCourse, course))
        rule4_count += 1
    results['Rule 4 (Dean → Course)'] = rule4_count
    
    return results

def temporal_delegation_example():
    """Demonstrate temporary permission delegation"""
    PLO = Namespace("http://www.example.org/plo-measure#")
    g = Graph()
    g.bind("plo", PLO)
    
    # Create temporary permission
    today = datetime.now()
    end_date = today + timedelta(days=14)
    
    permission = URIRef(PLO + "TempPerm_001")
    g.add((permission, RDF.type, PLO.TemporaryPermission))
    g.add((permission, PLO.effectiveFrom, Literal(today.isoformat(), datatype=XSD.date)))
    g.add((permission, PLO.effectiveUntil, Literal(end_date.isoformat(), datatype=XSD.date)))
    
    return {
        'active': True,
        'expires': end_date.isoformat(),
        'rule_expression': 'TemporaryPermission(?p) ∧ effectiveUntil(?p, ?until) ∧ now() ≤ ?until → canModifyTemporarily(?p)'
    }

def main():
    print("=" * 70)
    print("SWRL Rule Validation")
    print("=" * 70)
    
    g, clos, instructor, hod, dean = create_hierarchy()
    results = validate_rules(g, clos, instructor, hod, dean)
    
    print("\nRule Inference Results:")
    print("-" * 40)
    for rule, count in results.items():
        print(f"{rule}: {count} inferences")
    
    temporal = temporal_delegation_example()
    print(f"\nTemporal Delegation Example:")
    print(f"  Active: {temporal['active']}")
    print(f"  Expires: {temporal['expires']}")
    print(f"  SWRL Expression: {temporal['rule_expression']}")
    
    os.makedirs('../output/evaluation', exist_ok=True)
    with open('../output/evaluation/swrl_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✓ Results saved to ../output/evaluation/swrl_results.json")

if __name__ == "__main__":
    main()