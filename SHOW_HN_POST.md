# Show HN: Refyne – Clean messy financial data for ML in seconds, not weeks

Hi HN! I'm Sam, and I built Refyne to solve a problem I kept seeing in fintech: ML teams spending 60-80% of their time cleaning messy transaction data instead of building models.

**What it does:**
Refyne automatically cleans, validates, and transforms messy business data into ML-ready datasets. Think of it as a specialized data janitor for financial ML pipelines.

**Demo:** [Your deployed URL here]
**GitHub:** [Your repo URL]

**The Problem:**
When building fraud detection or credit scoring models, you're dealing with:
- Transaction data from 10 different systems with inconsistent formats
- Mixed currency symbols ($1,500 vs 1500.00 USD)
- Duplicate records
- Invalid ISINs/CUSIPs
- Missing timestamps
- PII that needs masking for compliance

Current solutions:
- Manual Excel cleaning → slow, error-prone, not reproducible
- Custom Python scripts → everyone reinvents the wheel
- Enterprise tools (Trifacta) → $50k/year, overkill for most teams

**What makes Refyne different:**
1. **Finance-specific** - Validates ISINs, CUSIPs, currency formats, account numbers
2. **Compliance built-in** - Audit logs, PII masking, data lineage for SOX/GDPR
3. **ML-native** - API-first, integrates with feature stores, outputs clean Parquet
4. **10x cheaper** than enterprise alternatives

**Technical Stack:**
- FastAPI backend
- Pandas + custom validators
- Real-time API + web interface
- Audit logging for every transformation

**Example:**
Upload messy transaction CSV → Get back:
- Standardized currency formats
- Validated security identifiers  
- Deduplicated records
- PII masked for compliance
- Audit trail of all changes

**Pricing:**
- Free tier: 100 rows/month
- Pro: $99/mo for 10k rows
- Enterprise: Custom for banks/hedge funds

**What I'd love feedback on:**
1. Is $99/mo the right price point for ML teams?
2. Should I focus on B2B SaaS or also offer managed services?
3. What integrations matter most? (Snowflake, Databricks, Feature stores?)

I've been working on this for [timeframe] after seeing this pain point repeatedly at [previous company/experience]. Happy to answer any questions!

Try it: [Demo link]
Docs: [API docs link]

---

**FAQ (preemptive):**

**Q: Why not just use pandas?**
A: You can! But you'd need to write 500+ lines of validation logic, handle edge cases, build audit logs for compliance, etc. Refyne packages all that into an API.

**Q: Data security?**
A: All processing happens on your infrastructure (on-premise option), SOC 2 Type II cert in progress, audit logs for everything.

**Q: How's this different from AWS Glue/DataBrew?**
A: More specialized for finance, simpler UX, 10x cheaper, better for ML pipelines vs ETL.

**Q: Open source?**
A: Core cleaning engine will be open-sourced. Enterprise features (SSO, audit logs, integrations) are paid.

Looking forward to your feedback!
