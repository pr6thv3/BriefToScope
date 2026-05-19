"""Rich demo / fallback data for hackathon reliability."""

SAMPLE_TRANSCRIPT = """
Sarah (Client): Hey Mike, thanks for jumping on. So we need to completely redesign our e-commerce platform. Right now we're on Magento 1, it's ancient, security patches are a nightmare. We want something modern, probably Shopify Plus or headless. Budget-wise we're thinking around $120,000. Timeline is aggressive — we need to launch before Black Friday, so that's basically end of September for soft launch, mid-October for full rollout.

Mike (Agency): Got it. What about the design system? Are you keeping the current brand or full rebrand?

Sarah: Full rebrand actually. New logo, new color palette, the works. Our current site looks like 2012. We need mobile-first, obviously. Conversion rate on mobile is terrible, like 0.8%.

Mike: And content? Product photography, descriptions?

Sarah: We have an in-house team for photography but descriptions are outsourced. We'll handle all content migration. Oh and we need multi-currency and multi-language. English, French, German to start.

Mike: Payment gateways?

Sarah: Stripe and PayPal for sure. Maybe Klarna later but not phase 1.

Mike: What about integrations? ERP, CRM?

Sarah: We use NetSuite for ERP and Salesforce for CRM. Those need to sync orders, inventory, and customer data.

Mike: Any third-party tools? Reviews, loyalty, email?

Sarah: Yotpo for reviews, Smile for loyalty, Klaviyo for email. All need to integrate.

Mike: And post-launch support?

Sarah: We'd want a 90-day warranty period for bug fixes. After that maybe a retainer.

Mike: Who's the decision maker on your side?

Sarah: I'm the VP of Digital. My CEO needs to approve anything over $50k but I've already got sign-off for this budget.

Mike: Perfect. I'll send over a proposal by Friday.

Sarah: Great. One thing — we need accessibility compliance. WCAG 2.1 AA minimum.

Mike: Noted. Anything else?

Sarah: SEO migration is critical. We can't lose our rankings. And we need a staging environment for UAT.

Mike: All clear. I'll capture all of this in the SOW.
"""


def get_fallback_sow():
    return {
        "project_overview": (
            "Redesign and rebuild the client's e-commerce platform from Magento 1 to a modern, "
            "headless commerce solution. The project includes a full brand redesign, mobile-first "
            "responsive frontend, multi-currency / multi-language support (EN/FR/DE), and integrations "
            "with NetSuite (ERP), Salesforce (CRM), Yotpo (reviews), Smile (loyalty), and Klaviyo (email). "
            "The target soft-launch is end of September with full rollout by mid-October, ahead of Black Friday."
        ),
        "objectives": [
            "Migrate from Magento 1 to a modern, secure e-commerce platform",
            "Deliver a full brand redesign with new logo, color palette, and design system",
            "Improve mobile conversion rate from 0.8% to industry benchmark (2.5%+)",
            "Launch multi-currency (USD, EUR, GBP) and multi-language (EN, FR, DE) storefronts",
            "Integrate NetSuite ERP, Salesforce CRM, Yotpo, Smile, and Klaviyo",
            "Maintain existing SEO equity and organic search rankings during migration",
            "Ensure WCAG 2.1 AA accessibility compliance across all storefronts",
            "Provide staging environment and 90-day post-launch warranty",
        ],
        "scope_of_work": [
            "Discovery & audit of existing Magento 1 codebase, data schema, and third-party integrations",
            "Platform architecture design: headless commerce stack recommendation (Shopify Plus / custom)",
            "UI/UX design system: wireframes, high-fidelity mockups, interactive prototypes",
            "Frontend development: responsive, mobile-first React/Next.js storefront",
            "Backend development: API layer, middleware for ERP/CRM integrations, custom business logic",
            "Content migration strategy: product catalog, customer data, order history, SEO redirects",
            "Payment gateway setup: Stripe, PayPal (phase 1); Klarna scoping (phase 2)",
            "Multi-language and multi-currency configuration with geo-IP routing",
            "Third-party integrations: Yotpo, Smile, Klaviyo, NetSuite, Salesforce",
            "Accessibility audit and remediation to WCAG 2.1 AA",
            "SEO migration: URL mapping, meta data transfer, sitemap submission",
            "QA, UAT on staging environment, load testing, security penetration testing",
            "Production deployment, monitoring setup, and knowledge transfer",
            "90-day post-launch warranty for critical bug fixes",
        ],
        "deliverables": [
            "Discovery report with technical audit, migration plan, and risk register",
            "Design system: component library, style guide, Figma files",
            "High-fidelity UI/UX designs for all core page templates (homepage, PLP, PDP, cart, checkout)",
            "Production-ready frontend codebase (React / Next.js)",
            "API documentation and middleware source code",
            "Content migration scripts and runbook",
            "Staging environment with automated deployment pipeline",
            "WCAG 2.1 AA accessibility audit report",
            "SEO migration checklist and 301 redirect mapping",
            "Test plan, UAT sign-off, load test results, and security scan report",
            "Deployment runbook and monitoring dashboard configuration",
            "90-day warranty support log and handover documentation",
        ],
        "timeline": [
            "Week 1-2: Discovery, audit, architecture decisions, and tech stack finalization",
            "Week 3-6: Design system, wireframes, high-fidelity mockups, and client approvals",
            "Week 7-12: Frontend and backend development, integration development",
            "Week 13-14: Content migration, data validation, and SEO redirect implementation",
            "Week 15-16: QA, accessibility audit, load testing, security testing, UAT on staging",
            "Week 17: Soft launch (limited traffic), monitoring, and hotfix window",
            "Week 18: Full rollout, performance validation, and final sign-off",
            "Week 19-30: 90-day post-launch warranty and support",
        ],
        "payment_schedule": [
            "20% deposit upon SOW signature and kick-off",
            "30% upon design system approval and development start",
            "30% upon successful UAT completion and staging sign-off",
            "20% upon production launch and 30-day stability confirmation",
        ],
        "client_responsibilities": [
            "Provide brand assets: logo files, brand guidelines, color codes, typography specifications",
            "Provide all product photography, descriptions, and category taxonomy",
            "Assign a dedicated project liaison with decision-making authority",
            "Provide timely feedback on designs and deliverables within 3 business days",
            "Facilitate API access credentials for NetSuite, Salesforce, Yotpo, Smile, and Klaviyo",
            "Coordinate internal UAT resources and approve test cases before staging deployment",
            "Manage CEO approval for any budget changes or scope additions exceeding $5,000",
            "Provide translated content for French and German storefronts by Week 10",
        ],
        "revision_policy": (
            "Two rounds of revisions are included per design milestone at no additional cost. "
            "Additional revision rounds will be scoped and billed at the standard hourly rate of $175/hr. "
            "Change requests that materially alter the agreed scope will trigger a change order process."
        ),
        "out_of_scope": [
            "Content creation (copywriting) beyond migration of existing descriptions",
            "Photography shoots or image editing beyond template implementation",
            "Ongoing SEO content strategy or link-building campaigns post-launch",
            "Custom native mobile app development (iOS/Android)",
            "Phase 2 features: Klarna buy-now-pay-later, subscription commerce, marketplace",
            "Infrastructure hosting costs (client bears cloud provider fees directly)",
            "Training beyond two 2-hour knowledge-transfer sessions",
        ],
        "assumptions": [
            "Client provides all brand assets and content within 5 business days of request",
            "Third-party APIs (NetSuite, Salesforce, Yotpo, Smile, Klaviyo) are stable and well-documented",
            "Magento 1 database schema is accessible and not corrupted",
            "Client UAT team is available within the scheduled UAT windows",
            "No major Magento 1 security incidents occur during the migration window",
            "All required legal/compliance approvals (GDPR, accessibility) are client-side responsibilities",
            "Staging environment will use client-provided hosting or agreed cloud infrastructure",
        ],
        "acceptance_criteria": [
            "All core user journeys (browse, search, cart, checkout, account) pass automated and manual QA",
            "Mobile Lighthouse performance score >= 90 and accessibility score >= 95",
            "ERP/CRM integration tests pass with 99.9% data sync accuracy over 7-day period",
            "SEO redirect mapping achieves <1% 404 error rate on top 1,000 legacy URLs",
            "WCAG 2.1 AA audit passes with zero critical and <=3 minor findings",
            "Load test confirms site handles 5x average daily traffic without degradation",
            "Client signs UAT completion checklist and production go-live authorization",
        ],
        "signature_section": (
            "CLIENT: ___________________________  Date: _______________\n"
            "Name: Sarah Johnson, VP of Digital\n\n"
            "AGENCY: ___________________________  Date: _______________\n"
            "Name: Mike Chen, Account Director\n\n"
            "This Statement of Work is valid upon signature by both parties."
        ),
    }


def get_fallback_brief():
    return {
        "client_name": "Sarah Johnson / VP of Digital",
        "project_type": "E-commerce Platform Redesign & Migration",
        "goals": [
            "Migrate from Magento 1 to modern platform",
            "Full brand redesign",
            "Improve mobile conversion rate",
            "Launch multi-currency / multi-language",
            "Integrate ERP, CRM, and marketing stack",
            "Maintain SEO equity",
            "WCAG 2.1 AA compliance",
        ],
        "deliverables": [
            "Modern e-commerce platform",
            "Design system",
            "Multi-language storefront",
            "ERP/CRM integrations",
            "Staging environment",
            "90-day warranty",
        ],
        "budget_mentions": ["$120,000"],
        "deadline_mentions": ["End of September soft launch", "Mid-October full rollout", "Before Black Friday"],
        "unclear_items": [
            "Final platform choice: Shopify Plus vs headless custom",
            "Exact scope of Klarna integration (phase 1 vs phase 2)",
            "Specific NetSuite API endpoints and data sync frequency",
        ],
    }


def get_fallback_risks():
    return [
        {
            "severity": "high",
            "title": "Magento 1 data corruption risk",
            "description": "Legacy database may have inconsistent or corrupted records that complicate migration.",
            "suggested_fix": "Run a full database health audit in Week 1 and build a data-cleansing step into migration.",
        },
        {
            "severity": "high",
            "title": "Black Friday immovable deadline",
            "description": "Hard stop deadline creates limited buffer for post-launch stabilization.",
            "suggested_fix": "Plan soft launch 4 weeks before Black Friday with a feature freeze 2 weeks prior.",
        },
        {
            "severity": "medium",
            "title": "Platform decision unresolved",
            "description": "Shopify Plus vs custom headless decision will impact timeline and cost.",
            "suggested_fix": "Include a platform comparison deliverable in Discovery with decision gate by end of Week 2.",
        },
        {
            "severity": "medium",
            "title": "Third-party API instability",
            "description": "NetSuite and Salesforce APIs can be flaky; integration delays are common.",
            "suggested_fix": "Build API mocks for parallel development and schedule integration testing early.",
        },
        {
            "severity": "low",
            "title": "Translated content delivery delay",
            "description": "French and German content may not arrive by Week 10.",
            "suggested_fix": "Negotiate a hard deadline for content delivery and scope EN-only launch as fallback.",
        },
    ]


def get_fallback_clauses():
    return {
        "revision_policy": (
            "Two rounds of revisions are included per design milestone at no additional cost. "
            "Additional revision rounds will be scoped and billed at the standard hourly rate of $175/hr. "
            "Change requests that materially alter the agreed scope will trigger a change order process."
        ),
        "out_of_scope": [
            "Content creation beyond migration of existing descriptions",
            "Photography shoots or image editing",
            "Ongoing SEO content strategy",
            "Custom native mobile app development",
            "Phase 2 features: Klarna, subscriptions, marketplace",
            "Infrastructure hosting costs",
            "Training beyond two 2-hour sessions",
        ],
        "assumptions": [
            "Client provides all brand assets within 5 business days",
            "Third-party APIs are stable and well-documented",
            "Magento 1 database is accessible and not corrupted",
            "Client UAT team is available during scheduled windows",
            "Staging environment uses client-provided or agreed cloud infrastructure",
        ],
        "acceptance_criteria": [
            "All core user journeys pass automated and manual QA",
            "Mobile Lighthouse performance >= 90 and accessibility >= 95",
            "ERP/CRM sync accuracy >= 99.9% over 7 days",
            "SEO 404 rate <1% on top 1,000 URLs",
            "WCAG 2.1 AA audit passes with zero critical findings",
            "Load test confirms 5x traffic capacity",
            "Client signs UAT and go-live authorization",
        ],
        "client_responsibilities": [
            "Provide brand assets and guidelines",
            "Provide product content and taxonomy",
            "Assign dedicated project liaison",
            "Provide feedback within 3 business days",
            "Facilitate third-party API credentials",
            "Coordinate UAT resources",
            "Manage budget approvals for scope changes",
            "Deliver translated content by Week 10",
        ],
    }
