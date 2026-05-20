# Requirements Document

## 1. Application Overview

**Application Name**: BriefToScope AI Workflow Orchestrator

**Description**: An AI-powered workflow orchestration tool that processes client meeting transcripts through a multi-stage pipeline to generate comprehensive project scopes, risk assessments, contract-ready clauses, and polished Statement of Work documents. The system transforms unstructured conversation data into structured, actionable project documentation with commercial protections and client-facing deliverables.

## 2. Users and Usage Scenarios

**Target Users**: Agency operations teams, project managers, commercial leads, delivery consultants who need to convert client discovery calls into formal scope documents, contract clauses, and complete SOW documents.

**Core Usage Scenarios**:
- Process meeting transcripts to extract project requirements
- Generate structured project scopes with deliverables and timelines
- Identify scope creep risks and commercial vulnerabilities
- Produce contract-ready clauses for SOWs and MSAs
- Assemble polished, client-facing Statement of Work documents
- Ensure commercial protections are embedded in project documentation

## 3. Page Structure and Functional Description

### 3.1 System Architecture

```
BriefToScope AI Workflow Orchestrator
├── Pipeline Orchestrator
│   ├── A1 Transcript Cleaner
│   ├── A2 Brief Extractor
│   ├── A3 Scope Builder
│   ├── A4 Scope Creep Risk Detector
│   ├── A5 Clause Generator
│   ├── A6 SOW Composer (NEW)
│   └── A7 (Future Step)
├── Data Models & Schemas
├── Service Layer
└── Testing Framework
```

### 3.2 A5 Clause Generator

**Purpose**: Generate commercially safe and professional contract-style clauses based on project scope, detected risks, timeline, deliverables, dependencies, revision expectations, and responsibilities.

**Persona**: Senior agency operations consultant / commercial SOW writer / contract operations strategist / delivery process expert (NOT a lawyer).

**Input Sources**:
- A1 Transcript Cleaner output
- A2 Brief Extractor output
- A3 Scope Builder output
- A4 Scope Creep Risk Detector output
- Industry context
- Tone preferences

**Output Components**:
- **revision_policy**: Summary, clauses array, limits_defined flag
- **payment_schedule**: Summary, milestones array (label, percentage, condition), late_payment_clause, payment_assumptions array
- **out_of_scope_clause**: Summary, excluded_items array, formal_clause
- **client_responsibilities_clause**: Summary, responsibilities array, formal_clause
- **ip_ownership_clause**: Summary, ownership_model, formal_clause
- **change_request_process**: Summary, workflow_steps array, formal_clause
- **timeline_assumptions_clause**: Summary, assumptions array, delay_conditions array, formal_clause
- **additional_protection_clauses**: Array of objects (title, reason, formal_clause)
- **clause_generation_confidence_score**: Integer 0-100

**Core Capabilities**:
- Consume outputs from A1, A2, A3, A4 pipeline steps
- Use structured JSON-mode LLM calls to generate clauses
- Implement retry logic for malformed JSON responses
- Support DEMO_MODE with rich fallback mock clauses
- Generate structured logs for A5 lifecycle events
- Store A5 output in PipelineState for downstream consumption

### 3.3 A6 SOW Composer (New Component)

**Purpose**: Assemble all previous AI outputs (A1–A5) into a final polished, client-facing Statement of Work document.

**Persona**: Senior agency account director / commercial proposal writer / SOW operations lead / premium client delivery strategist.

**Input Sources**:
- A1 Transcript Cleaner output
- A2 Brief Extractor output
- A3 Scope Builder output
- A4 Scope Creep Risk Detector output
- A5 Clause Generator output
- Industry context
- Tone preferences

**Output Components**:
- **document_title**: String
- **document_subtitle**: String
- **executive_summary**: String
- **sections**: Array of objects containing:
  - section_key: String
  - section_title: String
  - content_markdown: String
  - order: Integer
- **metadata**: Object containing:
  - client_name: String
  - project_name: String
  - industry: String
  - tone: String
  - generated_date: String
  - document_version: String
  - prepared_by: String
- **document_stats**: Object containing:
  - estimated_page_count: Integer
  - total_sections: Integer
  - scope_items_count: Integer
  - risk_items_detected: Integer
- **export_ready**: Boolean
- **composer_confidence_score**: Integer 0-100

**Required SOW Sections** (in order):
1. Project Overview
2. Objectives
3. Scope of Work
4. Deliverables
5. Timeline
6. Payment Schedule
7. Client Responsibilities
8. Revision Policy
9. Out of Scope
10. Assumptions
11. Acceptance Criteria
12. Signature Section

**Core Capabilities**:
- Consume consolidated outputs from A1+A2+A3+A4+A5
- Use structured JSON-mode LLM calls to generate SOW document
- Implement retry logic for malformed JSON responses
- Support DEMO_MODE with rich fallback mock SOW
- Generate Markdown-formatted content for web editor, PDF export, and DocuSign flow
- Generate structured logs for A6 lifecycle events
- Store A6 output in PipelineState for downstream consumption

### 3.4 Pipeline Orchestrator Updates

**Modified Flow**: A1 → A2 → A3 → A4 → A5 → A6 → A7

**A6 Integration Points**:
- Receives consolidated output from A1+A2+A3+A4+A5
- Passes SOW document data to A7 for further processing
- Updates PipelineState with A6 results

### 3.5 Data Models & Schemas

**Existing Schemas** (in /models/ai_schemas.py):
- **ClauseGeneratorInput**: Pydantic schema defining A5 input structure
- **ClauseGeneratorOutput**: Pydantic schema defining A5 output structure

**New Schemas** (in /models/ai_schemas.py):
- **SOWComposerInput**: Pydantic schema defining A6 input structure
- **SOWComposerOutput**: Pydantic schema defining A6 output structure matching the output components listed above

### 3.6 Service Layer

**Existing Service** (/services/clause_generator.py):
- Full implementation of A5 Clause Generator
- A5 persona-driven prompt engineering
- Retry mechanism for LLM call failures
- Fallback logic for DEMO_MODE
- Structured logging (A5 started, A5 completed, A5 failed, A5 fallback used)

**New Service** (/services/sow_composer.py):
- Full implementation of A6 SOW Composer
- A6 persona-driven prompt engineering
- Retry mechanism for LLM call failures
- Fallback logic for DEMO_MODE
- Structured logging (A6 started, A6 completed, A6 failed, A6 fallback used)
- Markdown content generation for frontend editor, PDF export, and e-sign flow

**Updated Service** (/services/ai_orchestrator.py):
- Integrate A5 step into pipeline execution
- Pass A1+A2+A3+A4 outputs to A5
- Handle A5 output storage in PipelineState
- Integrate A6 step into pipeline execution
- Pass A1+A2+A3+A4+A5 outputs to A6
- Handle A6 output storage in PipelineState
- Ensure A7 receives SOW document data from A6

### 3.7 Testing Framework

**Existing Test File** (/tests/test_clause_generator.py):
- Test revision limits generation
- Test payment milestones generation
- Test risk-based protection clauses
- Test unclear content ownership protection
- Test timeline assumptions generation
- Test fallback mode behavior
- Test full pipeline A1→A5 integration

**New Test File** (/tests/test_sow_composer.py):
- Test complete SOW generation with all 12 sections
- Test missing budget handling
- Test missing revision handling
- Test excluded scope rendering
- Test Markdown formatting validity
- Test fallback mode behavior
- Test full pipeline A1→A6 integration

## 4. Business Rules and Logic

### 4.1 A5 Clause Generation Logic

**Input Processing**:
- A5 must receive and process outputs from all upstream steps (A1, A2, A3, A4)
- Industry context and tone preferences must be applied to clause generation
- All input data must be validated against ClauseGeneratorInput schema

**Clause Generation Rules**:
- Revision policy must define clear limits and conditions
- Payment schedule must include milestone-based structure with percentages and conditions
- Out-of-scope items must be explicitly listed and formalized
- Client responsibilities must be clearly defined and actionable
- IP ownership model must be unambiguous
- Change request process must include step-by-step workflow
- Timeline assumptions must account for dependencies and delay conditions
- Additional protection clauses must be generated based on detected risks from A4

**Confidence Scoring**:
- Confidence score (0-100) must reflect completeness and clarity of input data
- Lower scores indicate need for human review before contract finalization

### 4.2 A6 SOW Composition Logic

**Input Processing**:
- A6 must receive and process outputs from all upstream steps (A1, A2, A3, A4, A5)
- Industry context and tone preferences must be applied to SOW composition
- All input data must be validated against SOWComposerInput schema

**SOW Generation Rules**:
- All 12 required sections must be generated in specified order
- Content must be formatted in Markdown for web editor, PDF export, and DocuSign flow
- Executive summary must synthesize key points from all upstream outputs
- Project Overview must incorporate A2 brief data
- Scope of Work must incorporate A3 scope data
- Deliverables must incorporate A3 deliverables data
- Timeline must incorporate A3 timeline data
- Payment Schedule must incorporate A5 payment schedule clause
- Client Responsibilities must incorporate A5 client responsibilities clause
- Revision Policy must incorporate A5 revision policy clause
- Out of Scope must incorporate A5 out-of-scope clause
- Assumptions must incorporate A5 timeline assumptions clause
- Acceptance Criteria must define clear success metrics
- Signature Section must include placeholders for client and service provider signatures

**Metadata Generation**:
- Document metadata must include client name, project name, industry, tone, generated date, document version, and prepared by
- Document stats must calculate estimated page count, total sections, scope items count, and risk items detected

**Confidence Scoring**:
- Confidence score (0-100) must reflect completeness and clarity of input data from A1-A5
- Lower scores indicate need for human review before client delivery

**Export Readiness**:
- export_ready flag must be set to true only when all required sections are complete and valid

### 4.3 Pipeline Orchestration Rules

**Sequential Execution**:
- A5 executes only after A4 completes successfully
- A6 executes only after A5 completes successfully
- A5 output must be stored before A6 execution begins
- A6 output must be stored before A7 execution begins
- Pipeline state must be updated at each step completion

**Error Handling**:
- If A5 fails, retry logic attempts up to N times (configurable)
- If A6 fails, retry logic attempts up to N times (configurable)
- If all retries fail, fallback to DEMO_MODE mock data
- Pipeline execution logs all A5 and A6 lifecycle events

**DEMO_MODE Behavior**:
- When enabled, A5 returns rich mock clause data
- When enabled, A6 returns rich mock SOW document data
- Mock data must be realistic and representative of production output
- DEMO_MODE flag must be clearly indicated in logs and output

### 4.4 Data Flow Rules

**State Management**:
- PipelineState must persist A5 output for A6 consumption
- PipelineState must persist A6 output for downstream steps
- A7 must have access to all SOW document data generated by A6
- State transitions must be atomic and logged

**Schema Validation**:
- All A5 inputs must conform to ClauseGeneratorInput schema
- All A5 outputs must conform to ClauseGeneratorOutput schema
- All A6 inputs must conform to SOWComposerInput schema
- All A6 outputs must conform to SOWComposerOutput schema
- Schema validation failures must trigger retry or fallback

## 5. Exceptions and Edge Cases

| Scenario | Handling |
|----------|----------|
| A5 receives malformed JSON from LLM | Retry up to N times, then fallback to DEMO_MODE |
| A6 receives malformed JSON from LLM | Retry up to N times, then fallback to DEMO_MODE |
| A4 output missing risk data | A5 generates baseline clauses without risk-specific protections |
| A5 output missing payment schedule | A6 generates standard payment schedule section with placeholder text |
| A5 output missing revision policy | A6 generates standard revision policy section with placeholder text |
| Unclear IP ownership from A3 | A5 generates protective IP ownership clause favoring service provider |
| No payment milestones defined in A3 | A5 generates standard milestone structure (e.g., 30% upfront, 40% midpoint, 30% completion) |
| A5 confidence score below threshold | Log warning, flag output for human review |
| A6 confidence score below threshold | Log warning, flag output for human review before client delivery |
| A6 Markdown formatting invalid | Retry generation with stricter formatting constraints |
| DEMO_MODE enabled | A5 and A6 skip LLM calls, return mock data |
| A5 execution timeout | Log failure, trigger retry or fallback |
| A6 execution timeout | Log failure, trigger retry or fallback |
| A7 step not yet implemented | A6 output stored in PipelineState, pipeline ends at A6 |
| Missing client name in A2 output | A6 uses placeholder \"[Client Name]\" in metadata |
| Missing project name in A2 output | A6 uses placeholder \"[Project Name]\" in metadata |

## 6. Acceptance Criteria

1. User provides meeting transcript to pipeline orchestrator
2. Pipeline executes A1 (Transcript Cleaner) and produces cleaned transcript
3. Pipeline executes A2 (Brief Extractor) and extracts project brief
4. Pipeline executes A3 (Scope Builder) and generates structured scope
5. Pipeline executes A4 (Risk Detector) and identifies scope creep risks
6. Pipeline executes A5 (Clause Generator) consuming A1+A2+A3+A4 outputs
7. A5 generates ClauseGeneratorOutput with all required clause components
8. A5 output stored in PipelineState with confidence score
9. Pipeline executes A6 (SOW Composer) consuming A1+A2+A3+A4+A5 outputs
10. A6 generates SOWComposerOutput with all 12 required sections in Markdown format
11. A6 output stored in PipelineState with confidence score and export_ready flag
12. System logs A5 and A6 lifecycle events (started, completed, confidence scores)
13. User receives complete SOW document ready for client delivery

## 7. Out of Scope for This Release

- A7 pipeline step implementation
- Legal review or validation of generated clauses or SOW content
- Contract template integration beyond SOW generation
- Multi-language clause or SOW generation
- User interface for clause or SOW editing or customization
- Clause or SOW version control or change tracking
- Integration with contract management systems
- Automated clause negotiation or redlining
- Client-facing clause or SOW presentation or approval workflow
- Clause or SOW library or template management
- Performance optimization for large-scale batch processing
- Advanced analytics on clause effectiveness or risk mitigation
- PDF export functionality (Markdown generation only)
- DocuSign integration (Markdown generation only)
- Custom branding or styling for SOW documents
- Multi-user collaboration on SOW editing
- SOW comparison or diff functionality
- Automated SOW delivery or distribution