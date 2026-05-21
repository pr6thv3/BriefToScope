-- ========================================================
-- BriefToScope - Industry Templates Database Seeding SQL
-- Inserts 10 industry configurations matching Pydantic schemas
-- ========================================================

-- Clean up existing templates to prevent duplicate key errors
TRUNCATE TABLE templates CASCADE;

-- 1. Web Design
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Web Design',
    'Standard Responsive Website Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Website strategy", "Information architecture", "Responsive page design", "Webflow or CMS development", "Contact form setup", "Basic SEO metadata", "Launch support"],
        "common_out_of_scope_items": ["Copywriting", "Photography", "Advanced animations", "Custom backend functionality", "Third-party integrations", "Ongoing maintenance"],
        "revision_policy": "Each major design deliverable includes up to two rounds of revisions unless otherwise specified.",
        "payment_schedule_options": [
            {
                "label": "Standard 50/25/25",
                "milestones": [
                    { "percentage": "50%", "condition": "Due before project kickoff" },
                    { "percentage": "25%", "condition": "Due upon design approval" },
                    { "percentage": "25%", "condition": "Due before final launch or handoff" }
                ]
            }
        ],
        "client_responsibilities": ["Provide final website copy", "Provide images and brand assets", "Provide timely approvals", "Provide domain or hosting access if needed"],
        "timeline_assumptions": ["Client feedback is provided within agreed review windows.", "Required content and assets are provided before development begins."],
        "acceptance_criteria": ["All approved pages are built and responsive.", "Contact forms are tested.", "Client approves final website preview."]
    }'::jsonb,
    '{
        "revision": ["Each major deliverable includes up to two rounds of revisions unless otherwise specified."],
        "payment": ["Project timelines may pause if invoices remain unpaid beyond the agreed payment period."],
        "out_of_scope": ["Work outside the approved scope may require a separate estimate and written approval."],
        "client_responsibilities": ["Client is responsible for providing final content, assets, feedback, and approvals required for project delivery."],
        "ip_ownership": ["Final approved deliverables become the property of the client upon receipt of full project payment."],
        "change_request": ["Additional requests outside the approved scope will be reviewed and may require adjusted pricing and timeline."],
        "timeline": ["Project timelines depend on timely client feedback, approvals, and asset delivery."]
    }'::jsonb,
    '[
        {
            "risk": "Copywriting ownership unclear",
            "trigger_terms": ["copy", "content", "website text"],
            "recommended_fix": "Define whether the client or agency provides final copy."
        },
        {
            "risk": "Animations undefined",
            "trigger_terms": ["animations", "interactions", "motion"],
            "recommended_fix": "Specify animation complexity and limits."
        }
    ]'::jsonb
);

-- 2. Branding
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Branding',
    'Creative Brand Identity Kit Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Discovery and visual research", "Moodboards and color palettes", "Primary logo and logo variations", "Typography rules and pairings", "Brand guidelines style book", "Asset formatting for digital use"],
        "common_out_of_scope_items": ["Trademark registration or legal filing", "Physical packaging print setup", "Copywriting or brand naming services", "Domain registration", "Custom illustration sets beyond logos"],
        "revision_policy": "Includes up to three rounds of visual revisions on the selected direction.",
        "payment_schedule_options": [
            {
                "label": "Standard 50/30/20",
                "milestones": [
                    { "percentage": "50%", "condition": "Due upon signing SOW" },
                    { "percentage": "30%", "condition": "Due on final concept selection" },
                    { "percentage": "20%", "condition": "Due before release of raw files" }
                ]
            }
        ],
        "client_responsibilities": ["Fill out discovery branding questionnaire", "Provide clear feedback during creative reviews", "Handle all trademark validation searches"],
        "timeline_assumptions": ["Feedback is gathered from all stakeholders and submitted as a unified list.", "Concept reviews occur within 3 working days of delivery."],
        "acceptance_criteria": ["Brand guide style book is finalized.", "Logo vector and rasters are exported and shared.", "Client signs off on brand rules."]
    }'::jsonb,
    '{
        "revision": ["Revisions are confined to refinements of the selected design direction. Pivot changes require a formal scope adjustment."],
        "payment": ["All master branding source files are released only after all project balances are fully settled."],
        "out_of_scope": ["Additional visual asset requests will be scoped separately at a standard rate of $150/hr."],
        "client_responsibilities": ["Client maintains responsibility for visual and legal clearance of corporate naming before asset creation."],
        "ip_ownership": ["Intellectual property rights for the finalized logo transfer to the client upon final milestone payment clearance."],
        "change_request": ["Changes to primary layout requirements after layout sign-off require a formal design change order fee."],
        "timeline": ["Timeline delays resulting from client review latency will push subsequent deliverable checkpoints."]
    }'::jsonb,
    '[
        {
            "risk": "Subjective reviews delay project",
            "trigger_terms": ["subjective", "taste", "opinion", "style preference"],
            "recommended_fix": "Incorporate structured visual feedback templates to keep reviews objective."
        },
        {
            "risk": "Naming conflicts or trademark overlap",
            "trigger_terms": ["trademark", "availability check", "legal name"],
            "recommended_fix": "Specify that naming is not legally vetted and trademark check is client responsibility."
        }
    ]'::jsonb
);

-- 3. Marketing
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Marketing',
    'Digital Acquisition Campaign Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Target audience and market research", "Campaign architecture and setup", "Ad creatives and graphic assets", "Copywriting for ads and landing pages", "Conversion tracking and pixels setup", "Monthly performance dashboard reports"],
        "common_out_of_scope_items": ["Direct payment of platform media spend", "Website landing page technical development", "Handling negative public review events", "Attribution tool subscription fees"],
        "revision_policy": "Includes two rounds of copy and asset adjustments prior to launch.",
        "payment_schedule_options": [
            {
                "label": "Flat Setup + Monthly Retainer",
                "milestones": [
                    { "percentage": "100%", "condition": "Campaign setup fee due upfront" },
                    { "percentage": "100%", "condition": "Retainer billed on the 1st of each campaign month" }
                ]
            }
        ],
        "client_responsibilities": ["Provide access to ad accounts and billing setup", "Provide raw media assets and brand guidelines", "Approve ad content before publishing schedules"],
        "timeline_assumptions": ["Ad accounts are verified by platforms before launch.", "Required media guidelines are provided at project kickoff."],
        "acceptance_criteria": ["Tracking pixels are firing successfully.", "Ad creatives are approved and live.", "First monthly dashboard report is generated."]
    }'::jsonb,
    '{
        "revision": ["Mid-campaign changes to ad creatives after live publishing are billed as an hourly update order."],
        "payment": ["All setup and campaign management costs are billed independently of performance outcomes."],
        "out_of_scope": ["Managing additional marketing channels (e.g. SEO, email) requires separate scope addenda."],
        "client_responsibilities": ["Client must fund platform accounts directly and resolve any platform credit issues."],
        "ip_ownership": ["Campaign strategy data remains agency property, while creatives transfer to client upon payment."],
        "change_request": ["Targeting updates and budget adjustments must be submitted in writing at least 72 hours before implementation."],
        "timeline": ["Platform compliance review times are out of agency control and may push campaign launches."]
    }'::jsonb,
    '[
        {
            "risk": "Ad spend payment delays",
            "trigger_terms": ["media spend", "ad account billing", "credit card limit"],
            "recommended_fix": "Add clause that ad campaign stops if platform payment card fails."
        },
        {
            "risk": "Tracking pixel setup blockers",
            "trigger_terms": ["tracking pixel", "conversions", "tag manager"],
            "recommended_fix": "Client developers must place code snippets within 5 days of request."
        }
    ]'::jsonb
);

-- 4. Copywriting
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Copywriting',
    'Strategic Copywriting & Editorial Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Content strategy and style alignment", "SEO keyword strategy integration plan", "First copy draft creation", "Feedback review revisions", "Final polished copy sheets"],
        "common_out_of_scope_items": ["Design or styling layout of page copy", "Direct uploading of text into client CMS tools", "Legality check of content claims", "Interviews with third-party experts"],
        "revision_policy": "Includes two rounds of copy reviews on the initial drafts.",
        "payment_schedule_options": [
            {
                "label": "50/50 Billing",
                "milestones": [
                    { "percentage": "50%", "condition": "Due upon signing SOW" },
                    { "percentage": "50%", "condition": "Due prior to delivery of final raw files" }
                ]
            }
        ],
        "client_responsibilities": ["Provide brand style and tone references", "Provide factual notes and business data points", "Submit clear text correction edits within review windows"],
        "timeline_assumptions": ["Reviews of drafts are completed within 5 business days.", "Required factual information is provided at project kickoff."],
        "acceptance_criteria": ["All copy matches the approved tone directives.", "Draft files pass SEO check requirements.", "Client approves final copy layout sheets."]
    }'::jsonb,
    '{
        "revision": ["Rewrites based on changes in content direction after outlines are approved are billed as new project orders."],
        "payment": ["Invoices are payable within 7 days of draft delivery, regardless of review status."],
        "out_of_scope": ["Proofreading pre-existing client text is out of scope unless added as a line item."],
        "client_responsibilities": ["Client is responsible for verifying the accuracy of all technical details in the copy before publishing."],
        "ip_ownership": ["IP rights to all text drafts transfer to the client upon full payment clearance."],
        "change_request": ["Changes to primary layout requirements after outlines are approved require a layout change order fee."],
        "timeline": ["Delays in client feedback beyond 10 days will result in project closure and billing of completed work."]
    }'::jsonb,
    '[
        {
            "risk": "Tone preferences shift mid-draft",
            "trigger_terms": ["tone", "voice", "vibe", "style direction"],
            "recommended_fix": "Secure written approval on tone examples before starting primary outlines."
        },
        {
            "risk": "Information delay stalls drafting",
            "trigger_terms": ["information", "details", "subject details"],
            "recommended_fix": "Set a timeline limit where delay in information auto-extends project delivery."
        }
    ]'::jsonb
);

-- 5. Social Media
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Social Media',
    'Monthly Social Media Management Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Social media channel strategy setup", "Monthly content calendar structure", "Visual graphic assets and copy drafts", "Hashtag and tags research mapping", "Monthly engagement and analytics report"],
        "common_out_of_scope_items": ["Responding directly to DM support messages", "Paid social media ad account operations", "Organizing on-site photo shoots", "Restoring banned platform accounts"],
        "revision_policy": "Includes one round of adjustments for each monthly content calendar.",
        "payment_schedule_options": [
            {
                "label": "Monthly Retainer Billing",
                "milestones": [
                    { "percentage": "100%", "condition": "Due monthly in advance on the 1st of each service month" }
                ]
            }
        ],
        "client_responsibilities": ["Provide product and brand media assets", "Review and approve draft calendars within review windows", "Provide credentials to scheduling platforms safely"],
        "timeline_assumptions": ["Post calendars are submitted for review by the 20th of the preceding month.", "Approvals are granted within 3 working days of submission."],
        "acceptance_criteria": ["Monthly post calendar is fully approved.", "Graphics and copy align with brand guidelines.", "Monthly analytics report is delivered."]
    }'::jsonb,
    '{
        "revision": ["Edits to scheduled posts after approval and scheduling must be requested at least 24 hours prior to post times."],
        "payment": ["Campaign execution will pause if monthly retainer invoices remain unpaid for more than 5 days."],
        "out_of_scope": ["Managing additional channels (e.g. YouTube, newsletters) is outside the scope of this retainer."],
        "client_responsibilities": ["Client is responsible for providing all legal credentials and assets necessary to execute posting calendars."],
        "ip_ownership": ["Final visual assets belong to the client, while analytical strategy templates remain the property of the agency."],
        "change_request": ["Requests to add additional emergency posts outside the monthly calendar scope will require separate fees."],
        "timeline": ["Posting schedules may shift temporarily to align with platform outages or major industry events."]
    }'::jsonb,
    '[
        {
            "risk": "Late client asset delivery pauses feed",
            "trigger_terms": ["images", "assets", "product photos", "late delivery"],
            "recommended_fix": "Add clause that post calendar will repeat evergreen posts if assets are not received 5 days before scheduled date."
        },
        {
            "risk": "Platform guideline changes affect visibility",
            "trigger_terms": ["guidelines", "banned terms", "algorithm change"],
            "recommended_fix": "State that algorithm changes are out of agency control and reports will focus on direct engagement metrics."
        }
    ]'::jsonb
);

-- 6. Video Production
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Video Production',
    'Commercial Video & Post-Production Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Concept development and script writing", "Storyboard layout sheets", "Raw shooting session setups", "Rough cut edit assemblies", "Color grading and audio mixing", "Master video file exports"],
        "common_out_of_scope_items": ["External studio space rentals", "Talent/actor hiring and payroll costs", "Premium commercial music licenses", "Travel expenses outside agency zone", "Physical distribution setup"],
        "revision_policy": "Includes two rounds of post-production edits on the rough cuts.",
        "payment_schedule_options": [
            {
                "label": "50/30/20 Production Milestones",
                "milestones": [
                    { "percentage": "50%", "condition": "Due upon scheduling the shoot" },
                    { "percentage": "30%", "condition": "Due upon delivery of first rough cut review" },
                    { "percentage": "20%", "condition": "Due prior to delivery of master raw files" }
                ]
            }
        ],
        "client_responsibilities": ["Provide product details and brand guidelines", "Approve storyboards and script files before shooting", "Secure permission rights for shooting locations"],
        "timeline_assumptions": ["Shooting dates are finalized at least 14 days in advance.", "Review comments on rough cuts are submitted within 5 business days."],
        "acceptance_criteria": ["Storyboards are finalized and signed off.", "Master video matches approved script directions.", "Final video files meet exporting specs."]
    }'::jsonb,
    '{
        "revision": ["Re-shoots after storyboard sign-off are billed as separate creative changes, not revision rounds."],
        "payment": ["Invoices for shooting milestones must be cleared before camera crews go active on location."],
        "out_of_scope": ["Any extra voiceover edits or foreign translation work is scoped separately."],
        "client_responsibilities": ["Client is responsible for getting clearance waivers for all employee faces appearing in the video."],
        "ip_ownership": ["Full usage rights transfer to client, while raw camera assets remain property of the studio."],
        "change_request": ["Changes to shooting dates within 7 days of production trigger a rescheduling fee of 15%."],
        "timeline": ["Timeline estimates assume standard weather patterns, and shifts may occur for natural safety factors."]
    }'::jsonb,
    '[
        {
            "risk": "Weather disrupts outdoor shoots",
            "trigger_terms": ["weather", "outdoor", "location", "rain"],
            "recommended_fix": "Incorporate a weather contingency backup shoot date in the schedule assumptions."
        },
        {
            "risk": "Music copyright clearance delays",
            "trigger_terms": ["music license", "copyright", "soundtrack"],
            "recommended_fix": "Add standard licensing clause stating client covers all royalty fees."
        }
    ]'::jsonb
);

-- 7. SEO
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'SEO',
    'Search Engine Optimization Strategy Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Technical website SEO audit", "Keyword research and mapping sheet", "On-page tags optimization sheet", "Competitor rankings assessment report", "Monthly search console reporting dashboard"],
        "common_out_of_scope_items": ["Developer programming to implement technical edits", "Purchasing backlinks or directory listings", "Copywriting blog articles", "Guarantees of page one ranking status", "Managing Google Ad account spending"],
        "revision_policy": "Includes one round of adjustments for each monthly keyword strategy sheet.",
        "payment_schedule_options": [
            {
                "label": "Monthly SEO retainer",
                "milestones": [
                    { "percentage": "100%", "condition": "Due recurringly on the 1st of each service month" }
                ]
            }
        ],
        "client_responsibilities": ["Provide Google Search Console access permissions", "Direct client developer resources to implement audit suggestions", "Share target business product priorities monthly"],
        "timeline_assumptions": ["Technical recommendations audits are completed by week 3 of kickoff.", "Client developers deploy code within 10 days of audit delivery."],
        "acceptance_criteria": ["Technical SEO audits are delivered.", "Target keyword mapping sheets are approved.", "Access configuration parameters are verified."]
    }'::jsonb,
    '{
        "revision": ["Subsequent keyword strategy adjustments outside the monthly audit schedule require change requests."],
        "payment": ["All services are billed at the beginning of each monthly cycle, and work stops if billing is delayed by 5 days."],
        "out_of_scope": ["Copywriting services for creating new landing page content must be scoped under separate SOW additions."],
        "client_responsibilities": ["Client is responsible for managing developer resources and ensuring recommendations are implemented accurately."],
        "ip_ownership": ["Keyword datasets and analysis reports become client property upon receipt of monthly retainer payment."],
        "change_request": ["Requests to add additional tracking domains require a proportional retainer upgrade."],
        "timeline": ["Ranking timelines assume technical changes are deployed within the agreed timelines."]
    }'::jsonb,
    '[
        {
            "risk": "Developer execution backlog stalls ranking",
            "trigger_terms": ["developer", "cms access", "site updates", "implementation delay"],
            "recommended_fix": "State that ranking changes depend on the client developer implementing technical recommendations within 14 days."
        },
        {
            "risk": "Search algorithm update alters ranking",
            "trigger_terms": ["algorithm update", "google update", "indexing change"],
            "recommended_fix": "Add standard search disclaimer explaining that indexing shifts are determined by search engines."
        }
    ]'::jsonb
);

-- 8. App Development
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'App Development',
    'Custom Software & Application Development Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["System architecture and database design", "API integration and endpoints engineering", "User interface front-end coding", "Admin control panel dashboard", "User Acceptance Testing (UAT) deployment", "Production server launch and handover"],
        "common_out_of_scope_items": ["App store developer registration fees", "Third-party SMS/email API gateway usage pricing", "Refactoring legacy external systems", "Subsequent major operating system upgrades", "Data entry of client product catalogs"],
        "revision_policy": "Includes up to two rounds of bug fixing during the designated 14-day User Acceptance Testing (UAT) window.",
        "payment_schedule_options": [
            {
                "label": "Sprint Milestones 30/40/30",
                "milestones": [
                    { "percentage": "30%", "condition": "Due before technical architecture setup" },
                    { "percentage": "40%", "condition": "Due upon staging release alpha launch" },
                    { "percentage": "30%", "condition": "Due prior to production server deployment" }
                ]
            }
        ],
        "client_responsibilities": ["Provide API endpoint documentation and access keys", "Assign a technical contact for integration queries", "Execute UAT test cases within 7 business days of release"],
        "timeline_assumptions": ["Integration credentials are provided within 5 days of kickoff.", "UAT feedback is returned as a single unified ticket list."],
        "acceptance_criteria": ["Application compiles and runs without crashes.", "APIs return correct mock data structures.", "Staging release matches approved UI visual layouts."]
    }'::jsonb,
    '{
        "revision": ["Feature additions requested during UAT that deviate from the specification are treated as Change Requests."],
        "payment": ["Staging release approval must be signed off, and balances cleared, before codebase keys are handed over."],
        "out_of_scope": ["Ongoing app maintenance and database hosting costs are out of scope unless covered under a separate SLA."],
        "client_responsibilities": ["Client is responsible for maintaining all external platform subscriptions and billing configurations."],
        "ip_ownership": ["Ownership of custom-developed codebase transfers to the client upon full payment clearance."],
        "change_request": ["Approved change requests will be billed at $175/hr and may impact the project delivery date."],
        "timeline": ["Delays in resolving integration credential errors will automatically push subsequent milestones."]
    }'::jsonb,
    '[
        {
            "risk": "Legacy API dependency is unstable",
            "trigger_terms": ["legacy api", "external database", "third-party integrations"],
            "recommended_fix": "Specify a mock API implementation path if the legacy API is down for over 48 hours."
        },
        {
            "risk": "Feature scope creep mid-sprint",
            "trigger_terms": ["sprint adjustment", "scope changes", "extra feature"],
            "recommended_fix": "Any changes to agreed specifications will be queued for post-launch sprint updates."
        }
    ]'::jsonb
);

-- 9. Consulting
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Consulting',
    'Management Consulting & Advisory Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Discovery workshops and analysis sheets", "Competitor evaluation framework", "Operations recommendations workbook", "Final strategic advisory deck"],
        "common_out_of_scope_items": ["Direct execution or staffing of operations", "Providing legal or accounting compliance advice", "Software configuration and license purchases", "Recruitment vetting and interviews"],
        "revision_policy": "Includes one round of revision adjustments to the final strategy deck.",
        "payment_schedule_options": [
            {
                "label": "50/50 Engagement Milestones",
                "milestones": [
                    { "percentage": "50%", "condition": "Due upon execution of agreement" },
                    { "percentage": "50%", "condition": "Due upon delivery of final deck" }
                ]
            }
        ],
        "client_responsibilities": ["Coordinate calendar invites for key team stakeholders", "Provide access to internal business analytics data", "Provide timely review feedback on strategy directions"],
        "timeline_assumptions": ["Advisory sessions occur weekly as scheduled.", "Client team responds to questionnaires within 3 working days."],
        "acceptance_criteria": ["Discovery workshops are completed.", "Strategic analysis documents are finalized.", "Final advisory presentation is delivered."]
    }'::jsonb,
    '{
        "revision": ["Subsequent revisions to recommendations after deck approval are billed as separate advisory hours."],
        "payment": ["Invoices are payable within 7 days of milestone completions, before subsequent phases start."],
        "out_of_scope": ["Any ongoing training or execution oversight requires a separate consulting retainer agreement."],
        "client_responsibilities": ["Client is responsible for verifying internal data accuracy before analysis sessions."],
        "ip_ownership": ["Methodology frameworks remain agency property, while custom insights transfer to client on payment."],
        "change_request": ["Requests to add additional team interviews require a proportional scope adjustment fee."],
        "timeline": ["Project timelines depend on timely client feedback, approvals, and asset delivery."]
    }'::jsonb,
    '[
        {
            "risk": "Stakeholder meeting cancellations",
            "trigger_terms": ["meeting cancellation", "reschedule", "availability"],
            "recommended_fix": "Add clause that meetings cancelled with less than 24 hours notice count against consulting hour limits."
        },
        {
            "risk": "Scope expansion of data queries",
            "trigger_terms": ["extra audit", "more data", "unplanned queries"],
            "recommended_fix": "Specify a cap on data analysis items included in the primary audit."
        }
    ]'::jsonb
);

-- 10. Ecommerce
INSERT INTO templates (industry, template_name, structure_json, clause_library_json, risk_rules_json) VALUES (
    'Ecommerce',
    'Ecommerce Store Integration Template',
    '{
        "default_sections": ["Project Overview", "Objectives", "Scope of Work", "Deliverables", "Timeline", "Payment Schedule", "Client Responsibilities", "Revision Policy", "Out of Scope", "Assumptions", "Acceptance Criteria", "Signature Section"],
        "standard_deliverables": ["Storefront styling and module configurations", "Product catalog import and categorization (up to 50 items)", "Payment gateway integration (PayPal/Shopify Payments)", "Shipping and tax calculation configurations", "Transactional email notifications styling", "End-to-end checkout testing validation"],
        "common_out_of_scope_items": ["Manual data entry of more than 50 product pages", "Setting up merchant accounts on platforms other than PayPal", "Custom inventory ERP synchronization development", "Handling legal business tax filings in foreign regions"],
        "revision_policy": "Includes two rounds of styling and category revisions before going live.",
        "payment_schedule_options": [
            {
                "label": "Standard 50/30/20 Setup",
                "milestones": [
                    { "percentage": "50%", "condition": "Due upon signing SOW" },
                    { "percentage": "30%", "condition": "Due on password-protected staging site release" },
                    { "percentage": "20%", "condition": "Due prior to removing store password" }
                ]
            }
        ],
        "client_responsibilities": ["Provide verified business tax IDs and bank details", "Provide product descriptions, price sheets, and image assets", "Configure custom domain DNS redirects"],
        "timeline_assumptions": ["Gateway approval parameters are handled at project kickoff.", "Product catalog data is provided in a single CSV file."],
        "acceptance_criteria": ["Store pages load properly and adapt to mobile layouts.", "Test transactions are completed successfully.", "Order notification emails are triggered."]
    }'::jsonb,
    '{
        "revision": ["Layout alterations requested after store structure is approved will require extra estimation fees."],
        "payment": ["Store password constraints will be removed only after the final milestone invoice is paid."],
        "out_of_scope": ["Ongoing store inventory management or bulk discount code additions require monthly SLAs."],
        "client_responsibilities": ["Client is responsible for setting up tax rules and verifying legal compliance."],
        "ip_ownership": ["All custom themes and store templates transfer to client ownership upon milestone completion payments."],
        "change_request": ["Requests to add additional payment plugins require scope updates at standard hourly design rates."],
        "timeline": ["Delays in bank account verifications will pause checkout launch dates."]
    }'::jsonb,
    '[
        {
            "risk": "Merchant account verification delays",
            "trigger_terms": ["merchant account", "payout verification", "payment gateway"],
            "recommended_fix": "Client must submit merchant documents within 7 days of kickoff to avoid gateway integration delays."
        },
        {
            "risk": "Inventory CSV data is corrupted",
            "trigger_terms": ["inventory sheet", "product csv", "import list"],
            "recommended_fix": "State that product imports assume client-provided spreadsheet follows agreed templates."
        }
    ]'::jsonb
);
