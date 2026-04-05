# metapub Design Philosophy

This document captures the design principles behind metapub's data model classes
(`PubMedArticle`, `ClinVarVariant`, and related objects). It exists to guide
contributors and inform code review decisions.

---

## Faithfulness to the Source Data Model

`PubMedArticle`, `ClinVarVariant`, and related classes are first and foremost
**faithful reproductions of the upstream data model** — the NLM XML schema for
PubMed and the ClinVar VCV/SCV formats respectively.

**What this means in practice:**

- Field names and structure should reflect what's actually in the XML, not what
  we wish were there.
- If the source data has multiple values for a field, the metapub representation
  should preserve that multiplicity — not flatten it into a single value.
- If the source data is inconsistent (mixed casing, optional fields, format
  variations across records), metapub should expose that inconsistency rather
  than silently normalizing it away. Normalization hides real-world data quality
  issues that callers need to know about.
- Don't second-guess what the data means. A field that returns `"Likely
  pathogenic"` in mixed case should return it that way because that's what
  ClinVar says. It's not metapub's job to decide what the canonical casing is.

**Why this matters:**

Downstream researchers and tools depend on metapub to give them an accurate
picture of what's in PubMed and ClinVar. A metapub object that quietly
transforms the data is a source of subtle, hard-to-detect errors — especially
when the upstream data changes format.

---

## Developer-Friendly Access to Common Information

Faithfulness to the data model doesn't mean the API has to be painful to use.
metapub should also provide **convenient access to the most commonly needed
information**.

The two goals are compatible when we keep them separate:

- **Raw/faithful properties** give back exactly what the source says.
- **Convenience properties** may aggregate, summarize, or simplify — but they
  should do so transparently and without destroying information.

A convenience property that aggregates submitter classifications into a summary
is a good addition. A convenience property that silently lowercases a
classification field and changes the return type of an existing property is a
breaking change that violates faithfulness.

When adding convenience properties, ask:
- Does this *add* something useful, or does it *replace* information with a
  simplified version?
- If a caller uses only the convenience property, can they still get back to the
  original data if they need it?
- Is the return type consistent and predictable regardless of how many values
  the source data contains?

---

## Practical Guidelines

- **Don't normalize casing on source fields.** If ClinVar returns
  `"Pathogenic"` with a capital P, return that. Don't lowercase it.
- **Don't collapse list fields into scalars.** If a variant can have multiple
  modes of inheritance, the faithful representation is a list. A scalar
  convenience property (`mode_of_inheritance`) should have a defined, consistent
  type — `str | None`, not `str | list` depending on the count.
- **Prefer `None` over empty string or zero for missing data.** Missing is
  meaningfully different from empty.
- **New summary/aggregation properties are welcome** — alongside the faithful
  representation, not instead of it.
