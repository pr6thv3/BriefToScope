-- ==========================================
-- BriefToScope - Seed Data Library
-- Includes: 10 Industry SOW Templates & MVP Demo Accounts
-- ==========================================

-- Clean previous seeds to prevent unique violations on fresh seed runs
TRUNCATE TABLE templates CASCADE;

-- 1. SEED INDUSTRY TEMPLATES
-- ==========================================

-- Industry 1: Web Design
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Web Design',
    'Standard Responsive Website Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Project Overview", "order": 1},
            {"key": "objectives", "title": "Objectives", "order": 2},
            {"key": "scope_of_work", "title": "Scope of Work", "order": 3},
            {"key": "deliverables", "title": "Deliverables", "order": 4},
            {"key": "timeline", "title": "Timeline & Phases", "order": 5},
            {"key": "payment_schedule", "title": "Payment Schedule", "order": 6},
            {"key": "client_responsibilities", "title": "Client Responsibilities", "order": 7},
            {"key": "revision_policy", "title": "Revision Policy", "order": 8},
            {"key": "out_of_scope", "title": "Out of Scope Exclusions", "order": 9},
            {"key": "assumptions", "title": "Assumptions & Dependencies", "order": 10},
            {"key": "acceptance_criteria", "title": "Acceptance Criteria", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes up to two (2) rounds of revisions. Additional revisions will be billed at an hourly rate of $150/hr."
        },
        "payment_default": {
            "milestones": [
                {"label": "Deposit", "percentage": "50%", "condition": "Due upon signing before commencement"},
                {"label": "Design Approval", "percentage": "25%", "condition": "Upon approval of visual layouts"},
                {"label": "Final Delivery", "percentage": "25%", "condition": "Due prior to website launch"}
            ]
        },
        "exclusions_default": [
            "Copywriting and content creation (unless explicitly mentioned)",
            "Purchase of premium plugins, stock photography, or custom fonts",
            "Hosting setup and server infrastructure fees",
            "Ongoing maintenance or post-launch technical support"
        ],
        "risk_rules": [
            {"trigger": "hosting", "warning": "Undefined hosting environment. Delays server-side configuration.", "severity": "medium"}
        ]
    }'::jsonb
);

-- Industry 2: Branding
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Branding',
    'Creative Brand Identity Kit Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Project Overview", "order": 1},
            {"key": "objectives", "title": "Brand Goals & Vision", "order": 2},
            {"key": "scope_of_work", "title": "Design Work scope", "order": 3},
            {"key": "deliverables", "title": "Brand Assets List", "order": 4},
            {"key": "timeline", "title": "Visual Delivery Phases", "order": 5},
            {"key": "payment_schedule", "title": "Payment Milestones", "order": 6},
            {"key": "client_responsibilities", "title": "Feedback Requirements", "order": 7},
            {"key": "revision_policy", "title": "Concept Revision Limits", "order": 8},
            {"key": "out_of_scope", "title": "Excluded Creative Services", "order": 9},
            {"key": "assumptions", "title": "Usage Rights & Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Approval Protocols", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 3,
            "policy_text": "Includes up to three (3) rounds of revisions on the selected visual concept. Changes to selected directions after final sign-off are billed as a change order."
        },
        "payment_default": {
            "milestones": [
                {"label": "Kickoff payment", "percentage": "50%", "condition": "Due upon signing SOW"},
                {"label": "Concept approval", "percentage": "30%", "condition": "Due upon selection of final direction"},
                {"label": "Master delivery", "percentage": "20%", "condition": "Due before release of raw files"}
            ]
        },
        "exclusions_default": [
            "Trademark registration or legal trademark searches",
            "Physical print production or packaging costs",
            "Custom illustrations beyond primary logo elements",
            "Naming services (unless explicitly added as a deliverable)"
        ],
        "risk_rules": [
            {"trigger": "trademark", "warning": "Subjective reviews or lack of legal searches may cause delays in naming approvals.", "severity": "high"}
        ]
    }'::jsonb
);

-- Industry 3: Marketing
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Marketing',
    'Digital Acquisition Campaign Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Campaign Overview", "order": 1},
            {"key": "objectives", "title": "KPIs & Performance Metrics", "order": 2},
            {"key": "scope_of_work", "title": "Ad Management Scope", "order": 3},
            {"key": "deliverables", "title": "Marketing Assets & Reports", "order": 4},
            {"key": "timeline", "title": "Campaign Timeline", "order": 5},
            {"key": "payment_schedule", "title": "Ad Spend & Retainer Fees", "order": 6},
            {"key": "client_responsibilities", "title": "Ad Account Access", "order": 7},
            {"key": "revision_policy", "title": "Ad Creative Revision Policy", "order": 8},
            {"key": "out_of_scope", "title": "Campaign Exclusions", "order": 9},
            {"key": "assumptions", "title": "Platform Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Performance Terms", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes two (2) adjustment rounds for campaign copy and graphics prior to publishing. Mid-campaign structural changes are subject to scope increases."
        },
        "payment_default": {
            "milestones": [
                {"label": "Setup fee", "percentage": "100%", "condition": "Due before project kickoff"},
                {"label": "Monthly Retainer", "percentage": "100%", "condition": "Billed upfront on the 1st of each service month"}
            ]
        },
        "exclusions_default": [
            "Direct payment of ad spend budgets to platforms (Facebook, Google, etc.)",
            "Website conversion landing page design (unless specified)",
            "Third-party attribution software subscriptions",
            "Handling negative client public reviews or PR crises"
        ],
        "risk_rules": [
            {"trigger": "spend", "warning": "Platform changes or unapproved ad accounts may freeze campaigns.", "severity": "medium"}
        ]
    }'::jsonb
);

-- Industry 4: Copywriting
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Copywriting',
    'Strategic Copywriting & Editorial Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Editorial Overview", "order": 1},
            {"key": "objectives", "title": "Brand Tone & Objectives", "order": 2},
            {"key": "scope_of_work", "title": "Writing & Research Scope", "order": 3},
            {"key": "deliverables", "title": "Written Deliverables", "order": 4},
            {"key": "timeline", "title": "Draft Review Cycles", "order": 5},
            {"key": "payment_schedule", "title": "Editorial Milestones", "order": 6},
            {"key": "client_responsibilities", "title": "Information Provision", "order": 7},
            {"key": "revision_policy", "title": "Revision Limits & Feedback", "order": 8},
            {"key": "out_of_scope", "title": "Out of Scope Content", "order": 9},
            {"key": "assumptions", "title": "Editorial Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Approval Criteria", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes two (2) rounds of textual reviews within ten (10) business days of draft delivery. Rewrites based on direction changes are subject to change fees."
        },
        "payment_default": {
            "milestones": [
                {"label": "Kickoff Retainer", "percentage": "50%", "condition": "Due upon signing SOW"},
                {"label": "Final Draft Delivery", "percentage": "50%", "condition": "Due prior to delivery of final raw documents"}
            ]
        },
        "exclusions_default": [
            "Layout design, page layout or web uploading tasks",
            "SEO metadata entry directly into CMS tools",
            "Legal compliance verification of advertising copy statements",
            "Interviews with external subject matter experts unless set in scope"
        ],
        "risk_rules": [
            {"trigger": "compliance", "warning": "Legal claims in advertising require separate compliance reviews.", "severity": "low"}
        ]
    }'::jsonb
);

-- Industry 5: SEO
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'SEO',
    'Search Engine Optimization Strategy Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Project Overview", "order": 1},
            {"key": "objectives", "title": "SEO Key Performance Indicators", "order": 2},
            {"key": "scope_of_work", "title": "Technical & On-Page Scope", "order": 3},
            {"key": "deliverables", "title": "SEO Reports & Audit Files", "order": 4},
            {"key": "timeline", "title": "Implementation Schedule", "order": 5},
            {"key": "payment_schedule", "title": "SEO Investment Structure", "order": 6},
            {"key": "client_responsibilities", "title": "Developer Access & Permissions", "order": 7},
            {"key": "revision_policy", "title": "Report Amendment Limits", "order": 8},
            {"key": "out_of_scope", "title": "SEO Exclusions", "order": 9},
            {"key": "assumptions", "title": "Search Engine Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Performance Expectations", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 1,
            "policy_text": "Includes one (1) round of revisions to the monthly keyword strategy sheet. Standard technical audits are fixed deliverables."
        },
        "payment_default": {
            "milestones": [
                {"label": "First month payment", "percentage": "100%", "condition": "Due prior to starting search queries research"},
                {"label": "Monthly retainers", "percentage": "100%", "condition": "Billed monthly at commencement of each service cycle"}
            ]
        },
        "exclusions_default": [
            "Development work to implement site updates (must be done by Client developers)",
            "Purchases of backlinks or automated link farm placements",
            "Copywriting blog articles (unless explicitly added in scope)",
            "Guarantees of specific page #1 keyword rankings"
        ],
        "risk_rules": [
            {"trigger": "implementation", "warning": "SEO success relies on Client developer speed to publish recommendation tickets.", "severity": "high"}
        ]
    }'::jsonb
);

-- Industry 6: Consulting
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Consulting',
    'Management Consulting & Advisory Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Engagement Overview", "order": 1},
            {"key": "objectives", "title": "Strategic Goals", "order": 2},
            {"key": "scope_of_work", "title": "Advisory Scope of Services", "order": 3},
            {"key": "deliverables", "title": "Consulting Deliverables", "order": 4},
            {"key": "timeline", "title": "Engagement Timeline", "order": 5},
            {"key": "payment_schedule", "title": "Professional Fees Schedule", "order": 6},
            {"key": "client_responsibilities", "title": "Executive Input & Access", "order": 7},
            {"key": "revision_policy", "title": "Strategy Document Amendments", "order": 8},
            {"key": "out_of_scope", "title": "Excluded Operations Services", "order": 9},
            {"key": "assumptions", "title": "Engagement Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Signoff Criteria", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 1,
            "policy_text": "Includes one (1) review session for the final strategy recommendation deck within 5 working days of delivery."
        },
        "payment_default": {
            "milestones": [
                {"label": "Retainer Payment", "percentage": "50%", "condition": "Due upon execution of agreement"},
                {"label": "Final Deliverable", "percentage": "50%", "condition": "Due upon delivery of final advisory deck"}
            ]
        },
        "exclusions_default": [
            "Direct hands-on execution or staffing of operations",
            "Legal or accounting compliance advice",
            "Providing specialized software platforms",
            "Recruiting search or background vetting calls"
        ],
        "risk_rules": [
            {"trigger": "implementation", "warning": "Engagement failure if client fails to commit executive session hours.", "severity": "medium"}
        ]
    }'::jsonb
);

-- Industry 7: App Development
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'App Development',
    'Custom Software & Application Development Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "System Architecture Overview", "order": 1},
            {"key": "objectives", "title": "Functional Objectives", "order": 2},
            {"key": "scope_of_work", "title": "Engineering Scope & Modules", "order": 3},
            {"key": "deliverables", "title": "Codebase & Deployment Assets", "order": 4},
            {"key": "timeline", "title": "Milestone & Sprint Phases", "order": 5},
            {"key": "payment_schedule", "title": "Phased Payment Structure", "order": 6},
            {"key": "client_responsibilities", "title": "API Access & Integrations", "order": 7},
            {"key": "revision_policy", "title": "User Acceptance Testing (UAT)", "order": 8},
            {"key": "out_of_scope", "title": "Excluded Technical Tasks", "order": 9},
            {"key": "assumptions", "title": "Tech Stack Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Launch Readiness Standards", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes two (2) iterations of bug fixing during the designated User Acceptance Testing (UAT) window of 14 days. Features outside signed specifications require change requests."
        },
        "payment_default": {
            "milestones": [
                {"label": "Kickoff milestone", "percentage": "30%", "condition": "Due before technical kickoff"},
                {"label": "UAT Alpha launch", "percentage": "40%", "condition": "Due upon staging release of code"},
                {"label": "Production deploy", "percentage": "30%", "condition": "Due prior to production server deployment"}
            ]
        },
        "exclusions_default": [
            "App store registration and developer accounts",
            "API keys, servers, and SMS verification pricing",
            "Migration of existing databases into new tables",
            "Upgrades for subsequent major operating system releases"
        ],
        "risk_rules": [
            {"trigger": "api", "warning": "Integrations with legacy custom software APIs could stall timeline sprints.", "severity": "high"}
        ]
    }'::jsonb
);

-- Industry 8: Video Production
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Video Production',
    'Commercial Video & Post-Production Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Production Concept", "order": 1},
            {"key": "objectives", "title": "Visual Objectives", "order": 2},
            {"key": "scope_of_work", "title": "Pre & Post Production Scope", "order": 3},
            {"key": "deliverables", "title": "Video Masters & Raw Cuts", "order": 4},
            {"key": "timeline", "title": "Shooting & Editing Schedule", "order": 5},
            {"key": "payment_schedule", "title": "Production Milestones", "order": 6},
            {"key": "client_responsibilities", "title": "Talent & Location Clearances", "order": 7},
            {"key": "revision_policy", "title": "Rough Cut Revisions", "order": 8},
            {"key": "out_of_scope", "title": "Excluded Media Services", "order": 9},
            {"key": "assumptions", "title": "Production Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Delivery Specifications", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes up to two (2) rounds of video editing changes (color grading and cuts only) on the delivered rough cuts."
        },
        "payment_default": {
            "milestones": [
                {"label": "Pre-Production booking", "percentage": "50%", "condition": "Due upon scheduling the shoot"},
                {"label": "Rough cut submission", "percentage": "30%", "condition": "Due upon release of first watermark build"},
                {"label": "Master delivery", "percentage": "20%", "condition": "Due prior to raw master link upload"}
            ]
        },
        "exclusions_default": [
            "Studio space rental charges or external equipment hires",
            "Paid talent hire and clothing/wardrobe costs",
            "Licensing fees for premium commercial soundtracks",
            "Travel costs outside the immediate local agency zone"
        ],
        "risk_rules": [
            {"trigger": "weather", "warning": "Weather conditions might cause rescheduling of outdoor shoots.", "severity": "medium"}
        ]
    }'::jsonb
);

-- Industry 9: Ecommerce
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Ecommerce',
    'Ecommerce Store Integration Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Storefront Concept", "order": 1},
            {"key": "objectives", "title": "Sales & Platform Goals", "order": 2},
            {"key": "scope_of_work", "title": "Product Setup & Payment Scope", "order": 3},
            {"key": "deliverables", "title": "Shopify/Store Modules", "order": 4},
            {"key": "timeline", "title": "Launch Checklist Schedule", "order": 5},
            {"key": "payment_schedule", "title": "Integration Payment Milestones", "order": 6},
            {"key": "client_responsibilities", "title": "Inventory CSVs & Tax IDs", "order": 7},
            {"key": "revision_policy", "title": "Review Cycles", "order": 8},
            {"key": "out_of_scope", "title": "Store Exclusions", "order": 9},
            {"key": "assumptions", "title": "Gateway Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Checkout Verification", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 2,
            "policy_text": "Includes two (2) rounds of layout and product configuration adjustments before going live. Additional changes are billed as change requests."
        },
        "payment_default": {
            "milestones": [
                {"label": "Kickoff deposit", "percentage": "50%", "condition": "Due upon signing agreement"},
                {"label": "Store review", "percentage": "30%", "condition": "Due on password-protection staging release"},
                {"label": "Launch handover", "percentage": "20%", "condition": "Due before removing store password"}
            ]
        },
        "exclusions_default": [
            "Entering more than fifty (50) manual product listings",
            "Setting up payment processors outside Stripe/Shopify Payments",
            "Custom inventory ERP synchronization coding",
            "Dealing with tax registration approvals in foreign countries"
        ],
        "risk_rules": [
            {"trigger": "gateway", "warning": "Late payment gateway verification will delay test purchases.", "severity": "high"}
        ]
    }'::jsonb
);

-- Industry 10: Social Media
INSERT INTO templates (industry, template_name, structure_json, clause_library_json) VALUES (
    'Social Media',
    'Monthly Social Media Management Template',
    '{
        "sections": [
            {"key": "project_overview", "title": "Engagement Overview", "order": 1},
            {"key": "objectives", "title": "Audience Grow targets", "order": 2},
            {"key": "scope_of_work", "title": "Monthly Post & Asset Scope", "order": 3},
            {"key": "deliverables", "title": "Campaign Calendars & Reports", "order": 4},
            {"key": "timeline", "title": "Publishing Schedules", "order": 5},
            {"key": "payment_schedule", "title": "Monthly Investment Terms", "order": 6},
            {"key": "client_responsibilities", "title": "Media Asset Deliveries", "order": 7},
            {"key": "revision_policy", "title": "Calendar Review Limits", "order": 8},
            {"key": "out_of_scope", "title": "Out of Scope Work", "order": 9},
            {"key": "assumptions", "title": "Platform Guidelines Assumptions", "order": 10},
            {"key": "acceptance_criteria", "title": "Monthly Signoff Process", "order": 11}
        ]
    }'::jsonb,
    '{
        "revision_default": {
            "rounds": 1,
            "policy_text": "Includes one (1) correction round for each monthly post calendar. Edits must be provided 5 days prior to scheduled publication."
        },
        "payment_default": {
            "milestones": [
                {"label": "Monthly payment", "percentage": "100%", "condition": "Billed recurringly on the 1st of each campaign month"}
            ]
        },
        "exclusions_default": [
            "Responding directly to custom DM customer support queries",
            "Paid influencer acquisition fees or contracts",
            "Executing photo shoots (client must provide product images)",
            "Restoring accounts suspended by platform policy actions"
        ],
        "risk_rules": [
            {"trigger": "assets", "warning": "Lack of client images stops creative post schedules.", "severity": "medium"}
        ]
    }'::jsonb
);


-- 2. SEED MVP MOCK USER, PROJECT, AND DEMO DATA
-- ==========================================

-- Seeding a primary Demo User (matches backend authentication fallbacks)
INSERT INTO users (id, clerk_user_id, email, name, avatar_url) VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'user_demo_001',
    'founder@lumaretail.co',
    'Preethve Founder',
    'https://api.dicebear.com/7.x/bottts/svg?seed=founder'
) ON CONFLICT (clerk_user_id) DO UPDATE 
SET email = EXCLUDED.email, name = EXCLUDED.name;

-- Seeding an organization workspace
INSERT INTO organizations (id, name, owner_id, plan) VALUES (
    'b0000000-0000-0000-0000-000000000002',
    'Luma Retail Studio',
    'b0000000-0000-0000-0000-000000000001',
    'solo'
);

-- Seeding a Project for the Demo User
INSERT INTO projects (id, user_id, org_id, client_name, project_name, industry, status, tone) VALUES (
    'b0000000-0000-0000-0000-000000000003',
    'b0000000-0000-0000-0000-000000000001',
    'b0000000-0000-0000-0000-000000000002',
    'Luma Retail Co.',
    'Brand Identity + Webflow Website',
    'Web Design',
    'active',
    'Professional'
);

-- Seeding a Transcript for the Project
INSERT INTO transcripts (id, project_id, raw_text, cleaned_text, metadata_json, source) VALUES (
    'b0000000-0000-0000-0000-000000000004',
    'b0000000-0000-0000-0000-000000000003',
    'We want a new website, mobile responsive, SEO pages, launch in 4 weeks, with a brand book setup. Budget is flexible but we are thinking around $15k.',
    'The client wants a refreshed brand identity and an 8-page Webflow website to be launched within 4 weeks. Budget target is around $15,000.',
    '{"speakers": ["Founder", "Account Executive"], "duration_seconds": 320}'::jsonb,
    'manual'
);

-- Seeding a generated SOW for the Project
INSERT INTO sows (id, project_id, user_id, title, content_json, content_markdown, risk_flags_json, confidence_score, status, pdf_url) VALUES (
    'b0000000-0000-0000-0000-000000000005',
    'b0000000-0000-0000-0000-000000000003',
    'b0000000-0000-0000-0000-000000000001',
    'Webflow Design & Brand Identity SOW',
    '{
        "project_overview": "Comprehensive design of an 8-page marketing website and matching brand identity book.",
        "objectives": [
            "Modernize storefront brand visibility",
            "Integrate responsive Webflow templates",
            "Establish clean 8-page layout"
        ],
        "scope_of_work": [
            "Interactive moodboards & logo assets configuration",
            "8 Webflow landing layouts design & publishing",
            "Basic SEO redirects setup"
        ],
        "deliverables": [
            "Logo kit vector sheets",
            "Brandbook typography parameters doc",
            "Live Webflow URL redirect map"
        ],
        "timeline": [
            "Phase 1: Brand directions approval (Week 1-2)",
            "Phase 2: Coding and checkout tests (Week 3-4)"
        ],
        "payment_schedule": [
            "Deposit milestone: 50% due at signing",
            "Handover milestone: 50% due before launch"
        ],
        "client_responsibilities": [
            "Supply raw product pictures",
            "Provide all copy texts"
        ],
        "revision_policy": "Two rounds of visual updates are included. Further updates are billed at $150/hour.",
        "out_of_scope": [
            "Custom copywriting",
            "Paid photo shoots"
        ],
        "assumptions": [
            "Hosting is pre-purchased by client"
        ],
        "acceptance_criteria": [
            "Site works on Safari and Chrome mobile view",
            "Forms submit leads successfully"
        ],
        "signature_section": "Client Representative Signature: ______________ Agency Representative Signature: ______________"
    }'::jsonb,
    '# Statement of Work
**Client:** Luma Retail Co.

## Project Overview
Comprehensive design of an 8-page marketing website and matching brand identity book.

## Objectives
- Modernize storefront brand visibility
- Integrate responsive Webflow templates
- Establish clean 8-page layout

## Scope of Work
- Interactive moodboards & logo assets configuration
- 8 Webflow landing layouts design & publishing
- Basic SEO redirects setup

## Deliverables
- Logo kit vector sheets
- Brandbook typography parameters doc
- Live Webflow URL redirect map

## Timeline
- Phase 1: Brand directions approval (Week 1-2)
- Phase 2: Coding and checkout tests (Week 3-4)

## Payment Schedule
- Deposit milestone: 50% due at signing
- Handover milestone: 50% due before launch

## Client Responsibilities
- Supply raw product pictures
- Provide all copy texts

## Revision Policy
Two rounds of visual updates are included. Further updates are billed at $150/hour.

## Out of Scope
- Custom copywriting
- Paid photo shoots

## Assumptions
- Hosting is pre-purchased by client

## Acceptance Criteria
- Site works on Safari and Chrome mobile view
- Forms submit leads successfully

## Signature Section
Client Representative Signature: ______________ Agency Representative Signature: ______________',
    '[
        {
            "severity": "medium",
            "title": "Hosting access dependency",
            "description": "Lack of predefined server environment may delay server-side setup.",
            "suggested_fix": "Provide server credentials at technical kickoff."
        }
    ]'::jsonb,
    91.00,
    'draft',
    ''
);

-- Seeding SOW initial version
INSERT INTO sow_versions (id, sow_id, version_number, content_json, content_markdown, change_summary, diff_json) VALUES (
    'b0000000-0000-0000-0000-000000000006',
    'b0000000-0000-0000-0000-000000000005',
    1,
    '{
        "project_overview": "Comprehensive design of an 8-page marketing website and matching brand identity book.",
        "objectives": [
            "Modernize storefront brand visibility",
            "Integrate responsive Webflow templates",
            "Establish clean 8-page layout"
        ],
        "scope_of_work": [
            "Interactive moodboards & logo assets configuration",
            "8 Webflow landing layouts design & publishing",
            "Basic SEO redirects setup"
        ],
        "deliverables": [
            "Logo kit vector sheets",
            "Brandbook typography parameters doc",
            "Live Webflow URL redirect map"
        ],
        "timeline": [
            "Phase 1: Brand directions approval (Week 1-2)",
            "Phase 2: Coding and checkout tests (Week 3-4)"
        ],
        "payment_schedule": [
            "Deposit milestone: 50% due at signing",
            "Handover milestone: 50% due before launch"
        ],
        "client_responsibilities": [
            "Supply raw product pictures",
            "Provide all copy texts"
        ],
        "revision_policy": "Two rounds of visual updates are included. Further updates are billed at $150/hour.",
        "out_of_scope": [
            "Custom copywriting",
            "Paid photo shoots"
        ],
        "assumptions": [
            "Hosting is pre-purchased by client"
        ],
        "acceptance_criteria": [
            "Site works on Safari and Chrome mobile view",
            "Forms submit leads successfully"
        ],
        "signature_section": "Client Representative Signature: ______________ Agency Representative Signature: ______________"
    }'::jsonb,
    '# Statement of Work
**Client:** Luma Retail Co.

## Project Overview
Comprehensive design of an 8-page marketing website and matching brand identity book.

## Objectives
- Modernize storefront brand visibility
- Integrate responsive Webflow templates
- Establish clean 8-page layout

## Scope of Work
- Interactive moodboards & logo assets configuration
- 8 Webflow landing layouts design & publishing
- Basic SEO redirects setup

## Deliverables
- Logo kit vector sheets
- Brandbook typography parameters doc
- Live Webflow URL redirect map

## Timeline
- Phase 1: Brand directions approval (Week 1-2)
- Phase 2: Coding and checkout tests (Week 3-4)

## Payment Schedule
- Deposit milestone: 50% due at signing
- Handover milestone: 50% due before launch

## Client Responsibilities
- Supply raw product pictures
- Provide all copy texts

## Revision Policy
Two rounds of visual updates are included. Further updates are billed at $150/hour.

## Out of Scope
- Custom copywriting
- Paid photo shoots

## Assumptions
- Hosting is pre-purchased by client

## Acceptance Criteria
- Site works on Safari and Chrome mobile view
- Forms submit leads successfully

## Signature Section
Client Representative Signature: ______________ Agency Representative Signature: ______________',
    'Initial AI orchestration draft generated from meeting transcript.',
    '{}'::jsonb
);

-- Seeding an AI pipeline run trace log
INSERT INTO ai_pipeline_runs (id, sow_id, project_id, trace_id, model_configurations, prompt_versions, a1_cleaned, a2_brief, a3_scope, a4_risks, a5_clauses, a6_sow, a7_quality, latency_ms) VALUES (
    'b0000000-0000-0000-0000-000000000008',
    'b0000000-0000-0000-0000-000000000005',
    'b0000000-0000-0000-0000-000000000003',
    'a0000000-0000-0000-0000-000000000001',
    '{"A1": "gpt-4o-mini", "A2": "gpt-4o", "A3": "gpt-4o", "A4": "gpt-4o", "A5": "gpt-4o-mini", "A6": "gpt-4o", "A7": "gpt-4o"}'::jsonb,
    '{"A1": "v1.2", "A2": "v2.0", "A3": "v1.1", "A4": "v1.0", "A5": "v1.0", "A6": "v2.1", "A7": "v1.3"}'::jsonb,
    '{"cleaned_text": "The client wants a refreshed brand identity and an 8-page Webflow website to be launched within 4 weeks. Budget target is around $15,000."}'::jsonb,
    '{"client_name": "Luma Retail Co.", "project_type": "Web Design", "timeline": "4 weeks", "budget": "$15,000"}'::jsonb,
    '{"modules": ["Brand book guidelines design", "8 Webflow layouts construction", "Launch checks and SEO redirects integration"]}'::jsonb,
    '{"risks": [{"severity": "medium", "title": "Hosting access dependency", "description": "Lack of server credentials."}]}'::jsonb,
    '{"clauses": [{"section": "Revision Policy", "content": "Includes up to two rounds of revisions."}]}'::jsonb,
    '{"title": "Webflow Design & Brand Identity SOW", "content": "Full SOW structured document sections."}'::jsonb,
    '{"passed": true, "score": 91.00, "recommendations": []}'::jsonb,
    6430
);

-- Seeding usage analytics events
INSERT INTO usage_events (id, user_id, org_id, event_type, token_count, estimated_cost, metadata_json) VALUES (
    'b0000000-0000-0000-0000-000000000007',
    'b0000000-0000-0000-0000-000000000001',
    'b0000000-0000-0000-0000-000000000002',
    'sow_generated',
    12400,
    0.02480,
    '{"duration_ms": 7840, "model": "gpt-4o"}'::jsonb
);
