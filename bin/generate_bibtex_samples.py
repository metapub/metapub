#!/usr/bin/env python3
"""
Script to generate BibTeX citation samples for testing and validation.

This script fetches real PubMed articles and generates their BibTeX citations
to create sample data for regression testing.
"""

import json
import sys
import os
from pathlib import Path

# Add metapub to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metapub import PubMedFetcher, cite


def generate_sample_data():
    """Generate sample BibTeX data from real PubMed articles"""

    fetcher = PubMedFetcher()

    # Sample PMIDs for testing
    sample_pmids = [
        '23435529',  # Reproductive medicine
        '25633503',  # CRISPR/gene editing
        '30971826',  # Machine learning in medicine
        '20301546',  # GeneReviews book article
    ]

    samples = {
        "description": "Generated BibTeX citation samples for regression testing",
        "generated_date": "2025-07-30",
        "articles": []
    }

    for pmid in sample_pmids:
        try:
            print(f"Fetching PMID {pmid}...")
            article = fetcher.article_by_pmid(pmid)

            # Generate BibTeX
            bibtex = article.citation_bibtex

            sample = {
                "pmid": pmid,
                "title": article.title,
                "authors": article.authors[:10],  # Limit to first 10 authors
                "journal": article.journal,
                "year": article.year,
                "volume": article.volume,
                "pages": article.pages,
                "doi": article.doi,
                "is_book": bool(article.book_accession_id),
                "generated_bibtex": bibtex,
                "bibtex_entry_type": "book" if article.book_accession_id else "article"
            }

            if article.book_accession_id:
                sample["book_accession_id"] = article.book_accession_id

            samples["articles"].append(sample)
            print(f"  ✓ Generated BibTeX for: {article.title[:50]}...")

        except Exception as e:
            print(f"  ✗ Error fetching PMID {pmid}: {e}")
            continue

    # Test edge cases with synthetic data
    edge_cases = [
        {
            "description": "Multi-word last names",
            "input": {
                "authors": ["Van Der Berg JH", "De La Cruz M"],
                "title": "Test Article with Multi-word Names",
                "journal": "Test Journal",
                "year": 2023
            }
        },
        {
            "description": "Special characters",
            "input": {
                "authors": ["O'Brien J", "García-López M"],
                "title": 'Article with "quotes" & special chars',
                "journal": "International Journal",
                "year": 2023
            }
        },
        {
            "description": "Pre-formatted author names",
            "input": {
                "authors": ["Smith, John H", "Jones, Kate M"],
                "title": "Pre-formatted Author Names",
                "journal": "Test Journal",
                "year": 2023
            }
        },
        {
            "description": "Single author",
            "input": {
                "authors": ["Einstein A"],
                "title": "Theory of Relativity",
                "journal": "Annalen der Physik",
                "year": 1905,
                "volume": 17,
                "pages": "891-921"
            }
        },
        {
            "description": "Book entry",
            "input": {
                "authors": ["Author A", "Author B"],
                "title": "Test Book Title",
                "year": 2022,
                "isbook": True
            }
        }
    ]

    print("\nGenerating edge case samples...")
    samples["edge_cases"] = []

    for case in edge_cases:
        try:
            bibtex = cite.bibtex(**case["input"])
            case["generated_bibtex"] = bibtex
            samples["edge_cases"].append(case)
            print(f"  ✓ Generated: {case['description']}")
        except Exception as e:
            print(f"  ✗ Error generating {case['description']}: {e}")

    return samples


def save_samples(samples, output_file):
    """Save samples to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSamples saved to: {output_file}")


def validate_bibtex_format(bibtex):
    """Validate basic BibTeX format structure"""
    errors = []

    # Check basic structure
    if not bibtex.startswith('@'):
        errors.append("BibTeX should start with @")

    if not bibtex.endswith('}'):
        errors.append("BibTeX should end with }")

    # Check brace balance
    open_braces = bibtex.count('{')
    close_braces = bibtex.count('}')
    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

    # Check entry type
    if not ('@article{' in bibtex or '@book{' in bibtex):
        errors.append("Should contain @article{ or @book{")

    return errors


def validate_samples(samples):
    """Validate generated samples"""
    print("\nValidating generated samples...")

    total_errors = 0

    # Validate articles
    for i, article in enumerate(samples.get("articles", [])):
        bibtex = article.get("generated_bibtex", "")
        errors = validate_bibtex_format(bibtex)

        if errors:
            print(f"  ✗ Article {i+1} (PMID: {article.get('pmid', 'unknown')}) errors:")
            for error in errors:
                print(f"    - {error}")
            total_errors += len(errors)
        else:
            print(f"  ✓ Article {i+1} (PMID: {article.get('pmid', 'unknown')}) valid")

    # Validate edge cases
    for i, case in enumerate(samples.get("edge_cases", [])):
        bibtex = case.get("generated_bibtex", "")
        errors = validate_bibtex_format(bibtex)

        if errors:
            print(f"  ✗ Edge case {i+1} ({case.get('description', 'unknown')}) errors:")
            for error in errors:
                print(f"    - {error}")
            total_errors += len(errors)
        else:
            print(f"  ✓ Edge case {i+1} ({case.get('description', 'unknown')}) valid")

    if total_errors == 0:
        print("\n🎉 All samples validated successfully!")
    else:
        print(f"\n⚠️  Validation completed with {total_errors} errors")

    return total_errors == 0


def main():
    """Main function"""
    print("🧬 BibTeX Citation Sample Generator")
    print("=" * 50)

    try:
        # Generate samples
        samples = generate_sample_data()

        # Validate samples
        is_valid = validate_samples(samples)

        # Save to file
        output_file = Path(__file__).parent.parent / "tests" / "data" / "generated_bibtex_samples.json"
        save_samples(samples, output_file)

        # Summary
        article_count = len(samples.get("articles", []))
        edge_case_count = len(samples.get("edge_cases", []))

        print(f"\n📊 Summary:")
        print(f"  • {article_count} real articles processed")
        print(f"  • {edge_case_count} edge cases generated")
        print(f"  • Validation: {'✓ PASSED' if is_valid else '✗ FAILED'}")

        if is_valid:
            print(f"\n✅ Sample generation completed successfully.")
        else:
            print(f"\n❌ Sample generation completed with validation errors.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Error during sample generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
