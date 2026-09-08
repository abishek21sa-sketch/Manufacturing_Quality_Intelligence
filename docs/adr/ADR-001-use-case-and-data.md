# ADR-001: Canonical process-quality use case with benchmark adapters

**Status:** Accepted

The platform uses a generic discrete-manufacturing process-quality domain model instead of hard-coding one public dataset. This preserves quality-engineering semantics (process variables, inspection results, MSA, SPC, defect risk) while still allowing benchmark adapters such as UCI SECOM.

Synthetic fixed-seed data is used only for reproducible repository validation. Real-data adapters are separate and cannot silently change the domain contract.
