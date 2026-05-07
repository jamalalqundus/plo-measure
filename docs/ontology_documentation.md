# PLO-MEASURE Ontology Documentation

## Overview

The PLO-MEASURE ontology is an OWL 2 DL ontology for modeling Program Learning Outcomes (PLOs), Key Performance Indicators (KPIs), Course Learning Outcomes (CLOs), and their relationships to assessments and instructor permissions.

**Namespace:** `http://www.example.org/plo-measure#`  
**Version:** 1.0  
**License:** MIT

## Core Classes

### Organizational Classes

| Class | Description |
|-------|-------------|
| `Faculty` | Academic faculty/department group |
| `Department` | Academic department within a faculty |
| `Program` | Degree program (e.g., B.Sc. Computer Science) |
| `Course` | A taught course with code, title, semester, year |

### Learning Outcome Classes

| Class | Description |
|-------|-------------|
| `PLO` | Program Learning Outcome (high-level) |
| `KPI` | Key Performance Indicator (measurable) |
| `CLO` | Course Learning Outcome (specific) |

### Assessment Classes

| Class | Description |
|-------|-------------|
| `Assessment` | Quiz, exam, assignment, or project |
| `Question` | Individual question or task |
| `Grade` | Student's score on a specific question |

### Agent Classes

| Class | Description |
|-------|-------------|
| `Instructor` | Course instructor |
| `Dean` | Faculty dean |
| `HeadOfDepartment` | Department head |
| `Student` | Enrolled student |

## Object Properties

| Property | Domain | Range | Meaning |
|----------|--------|-------|---------|
| `hasDepartment` | Faculty | Department | Faculty contains department |
| `hasProgram` | Department | Program | Department contains program |
| `hasCourse` | Program | Course | Program contains course |
| `hasPLO` | Program | PLO | Program has PLO |
| `hasKPI` | PLO | KPI | PLO has KPI |
| `hasCLO` | Course | CLO | Course has CLO |
| `alignsWithKPI` | CLO | KPI | CLO maps to KPI |
| `hasBloomLevel` | CLO | bloom:BloomLevel | CLO's cognitive level |
| `teaches` | Instructor | Course | Instructor teaches course |
| `canModifyCLO` | Instructor | CLO | Inferred permission |

## SWRL Rules

### Rule 1: Instructor CLO Modification
```swrl
Instructor(?i) ∧ teaches(?i, ?c) ∧ hasCLO(?c, ?clo) → canModifyCLO(?i, ?clo)
```

### Rule 2: Head of Department KPI Modification
HeadOfDepartment(?h) ∧ hasDepartment(?h, ?d) ∧ hasProgram(?d, ?p) 
∧ hasPLO(?p, ?plo) ∧ hasKPI(?plo, ?kpi) → canModifyKPI(?h, ?kpi)

### Rule 3: Head of Department PLO Modification
HeadOfDepartment(?h) ∧ hasDepartment(?h, ?d) ∧ hasProgram(?d, ?p) 
∧ hasPLO(?p, ?plo) → canModifyPLO(?h, ?plo)

### Rule 4: Dean Course Management
Dean(?d) ∧ hasFaculty(?d, ?f) ∧ hasDepartment(?f, ?dep) 
∧ hasProgram(?dep, ?p) ∧ hasCourse(?p, ?c) → canManageCourse(?d, ?c)

## Usage in Protégé

Open Protégé 5.6+
1. File → Open → ontology/plo-measure-ontology.ttl
2. Reasoner → Pellet → Start reasoner
3. Query → SPARQL 
4. Query (to run queries)

### Example SPARQL Queries

#### Find instructors who can modify CLOs supporting a specific PLO
PREFIX plo: <http://www.example.org/plo-measure#>
SELECT DISTINCT ?instructor ?clo ?kpi ?plo
WHERE {
  ?plo plo:hasKPI ?kpi .
  ?kpi plo:hasCLO ?clo .
  ?instructor plo:canModifyCLO ?clo .
}

#### Calculate PLO achievement
PREFIX plo: <http://www.example.org/plo-measure#>
SELECT ?plo (AVG(?weightedKPI) AS ?achievement)
WHERE {
  ?plo plo:hasKPI ?kpi .
  ?kpi plo:hasCLO ?clo .
  ?clo plo:hasWeight ?w .
  ?w plo:weightValue ?wv .
  ?grade plo:forQuestion ?q .
  ?grade plo:hasScore ?s .
  ?q plo:measuresCLO ?clo .
  ?q plo:hasMaxScore ?m .
  BIND((?s/?m)*?wv AS ?weightedKPI)
} GROUP BY ?plo

## OWL File Format
The ontology is available in two formats:
- plo-measure-ontology.ttl (Turtle)
- plo-measure-ontology.owl (OWL/XML)