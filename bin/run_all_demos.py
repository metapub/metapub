#!/usr/bin/env python3
"""
Master script to run all demo scripts in the bin/ directory.
Handles argument requirements and provides a unified interface.
"""

import os
import sys
import subprocess
import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for metapub imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DemoRunner:
    """Main class for running all demo scripts with appropriate arguments."""

    def __init__(self, bin_dir: str = None):
        self.bin_dir = Path(bin_dir) if bin_dir else Path(__file__).parent
        self.scripts = self._discover_scripts()
        self.default_args = self._setup_default_arguments()

    def _discover_scripts(self) -> List[Path]:
        """Discover all Python scripts in the bin directory."""
        scripts = []
        for script_path in self.bin_dir.glob("*.py"):
            if script_path.name != "run_all_demos.py":  # Exclude this script
                scripts.append(script_path)
        return sorted(scripts)

    def _setup_default_arguments(self) -> Dict[str, Dict[str, Any]]:
        """Define default arguments for scripts that require them."""
        return {
            "demo_get_PubMedArticle_by_pmid.py": {
                "args": ["33157158"],  # Real PMID for testing
                "description": "Fetch PubMed article by PMID"
            },
            "demo_get_PubMedArticle_by_doi.py": {
                "args": ["10.1038/nature12373"],  # Real DOI
                "description": "Fetch PubMed article by DOI"
            },
            "demo_get_PubMedArticle_by_pmcid.py": {
                "args": ["PMC3458974"],  # Real PMC ID
                "description": "Fetch PubMed article by PMC ID"
            },
            "demo_disease2gene.py": {
                "args": ["diabetes"],
                "description": "Get genes associated with a disease"
            },
            "demo_gene2condition_basic.py": {
                "args": ["CFTR"],
                "description": "Get conditions associated with a gene"
            },
            "demo_get_MedGen_uid_for_CUI.py": {
                "args": ["C0039445"],  # CUI for HHT (her. hem. telang.)
                "description": "Get MedGen UID for a CUI"
            },
            "demo_get_concepts_for_medgen_term.py": {
                "args": ["diabetes"],
                "description": "Get MedGen concepts for a term"
            },
            "demo_get_doi_for_pmid.py": {
                "args": ["33157158"],
                "description": "Get DOI for a PMID"
            },
            "demo_get_related_pmids.py": {
                "args": ["33157158"],
                "description": "Get related PMIDs"
            },
            "demo_get_pmids_for_medgen_cui.py": {
                "args": ["C1306557"],  # CUI for chronic venous insufficiency
                "description": "Get PMIDs for a MedGen CUI"
            },
            "demo_findit_backup_url.py": {
                "args": ["33157158"],  # Use valid PMID instead
                "description": "Test FindIt backup URL functionality"
            },
            "demo_findit_nonverified.py": {
                "args": ["33157158"],
                "description": "Test FindIt with non-verified sources"
            },
            "demo_dx_doi_cache.py": {
                "args": ["30000000"],
                "description": "Test DOI cache functionality"
            },
            "demo_preload_FindIt.py": {
                "args": ["sample_pmids.txt"],
                "description": "Preload FindIt cache from file"
            },
            "demo_preload_pmids_for_CrossRef.py": {
                "args": ["sample_pmids.txt"],
                "description": "Preload CrossRef data from file"
            },
            "demo_query_list_of_pmids_with_crossref.py": {
                "args": ["sample_pmids.txt"],
                "description": "Query CrossRef for list of PMIDs"
            },
            "import_dois.py": {
                "args": ["sample_pmids.txt"],
                "description": "Import DOIs from file"
            },
            "demo_medgen_comprehensive_workflow.py": {
                "args": ["breast cancer"],
                "description": "Comprehensive MedGen+ClinVar workflow: medical term → genes → variants → literature"
            }
        }

    def _create_sample_files(self):
        """Create sample input files if they don't exist."""
        # Create output directory
        output_dir = self.bin_dir.parent / "output"
        output_dir.mkdir(exist_ok=True)

        sample_pmids_file = self.bin_dir / "sample_pmids.txt"
        if not sample_pmids_file.exists():
            sample_pmids = ["33157158", "32187540", "31653314", "30982822", "29977293"]
            with open(sample_pmids_file, 'w') as f:
                f.write('\n'.join(sample_pmids) + '\n')
            logger.info(f"Created {sample_pmids_file}")

    def _check_script_requirements(self, script_path: Path) -> bool:
        """Check if a script requires arguments by examining its source."""
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                return 'sys.argv' in content or 'argparse' in content or 'click' in content
        except Exception as e:
            logger.warning(f"Could not read {script_path}: {e}")
            return False

    def run_single_script(self, script_path: Path, custom_args: List[str] = None,
                         timeout: int = 60, capture_output: bool = True) -> Dict[str, Any]:
        """Run a single script and return results."""
        script_name = script_path.name

        # Determine arguments
        args = []
        if custom_args:
            args = custom_args
        elif script_name in self.default_args:
            args = self.default_args[script_name]["args"]

        # Adjust timeout for known slow scripts
        slow_scripts = {
            "demo_findit.py": 120,  # Tests many journal URLs
            "demo_preload_FindIt.py": 120,  # Processes multiple PMIDs
            "demo_preload_pmids_for_CrossRef.py": 120,  # CrossRef API calls
            "demo_query_list_of_pmids_with_crossref.py": 120,  # CrossRef queries
            "demo_get_pmids_for_medgen_cui.py": 90,  # MedGen API calls
            "demo_get_related_pmids.py": 90,  # PubMed API calls
        }

        if script_name in slow_scripts:
            timeout = max(timeout, slow_scripts[script_name])

        # Build command
        cmd = [sys.executable, str(script_path)] + args

        logger.info(f"Running {script_name} with args: {args} (timeout: {timeout}s)")

        try:
            # Run the script
            result = subprocess.run(
                cmd,
                cwd=self.bin_dir,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )

            return {
                "script": script_name,
                "args": args,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "success": result.returncode == 0,
                "description": self.default_args.get(script_name, {}).get("description", "")
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Script {script_name} timed out after {timeout} seconds")
            return {
                "script": script_name,
                "args": args,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Timeout after {timeout} seconds",
                "success": False,
                "description": self.default_args.get(script_name, {}).get("description", "")
            }
        except Exception as e:
            logger.error(f"Error running {script_name}: {e}")
            return {
                "script": script_name,
                "args": args,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "description": self.default_args.get(script_name, {}).get("description", "")
            }

    def run_all_scripts(self, timeout: int = 60, continue_on_error: bool = True,
                       exclude: List[str] = None, delay_between_scripts: float = 1.0,
                       quick_test: bool = False) -> List[Dict[str, Any]]:
        """Run all discovered scripts."""
        exclude = exclude or []

        # Add problematic scripts to exclusion list in quick test mode
        if quick_test:
            problematic_scripts = [
                "demo_dx_doi_cache.py",  # DOI cache operations
                "demo_findit_backup_url.py",  # Network timeouts
                "demo_findit_nonverified.py",  # Network timeouts
                "demo_findit.py",  # Tests many journal URLs
                "demo_preload_FindIt.py",  # Processes multiple PMIDs
                "demo_preload_pmids_for_CrossRef.py",  # CrossRef API calls
                "demo_query_list_of_pmids_with_crossref.py",  # CrossRef queries
                "demo_get_pmids_for_medgen_cui.py",  # Slow MedGen queries
                "demo_get_related_pmids.py",  # Slow PubMed queries
                "embargo_data_checker.py",  # Long-running embargo checks
            ]
            exclude = list(set(exclude + problematic_scripts))
            logger.info(f"Quick test mode: excluding {len(problematic_scripts)} slow scripts")

        results = []

        # Create sample files first
        self._create_sample_files()

        for script_path in self.scripts:
            if script_path.name in exclude:
                logger.info(f"Skipping excluded script: {script_path.name}")
                continue

            result = self.run_single_script(script_path, timeout=timeout)
            results.append(result)

            if not result["success"]:
                logger.warning(f"Script {script_path.name} failed: {result['stderr']}")
                if not continue_on_error:
                    break
            else:
                logger.info(f"Script {script_path.name} completed successfully")

            # Add delay between scripts to avoid overwhelming external APIs
            if delay_between_scripts > 0:
                time.sleep(delay_between_scripts)

        return results

    def list_scripts(self) -> None:
        """List all available scripts with their descriptions."""
        print("Available demo scripts:")
        print("=" * 50)

        for script_path in self.scripts:
            script_name = script_path.name
            info = self.default_args.get(script_name, {})
            description = info.get("description", "No description available")
            args = info.get("args", [])

            print(f"• {script_name}")
            print(f"  Description: {description}")
            if args:
                print(f"  Default args: {args}")
            print()

    def generate_report(self, results: List[Dict[str, Any]], output_file: str = None) -> None:
        """Generate a summary report of script execution results."""
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        report = {
            "summary": {
                "total_scripts": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": f"{len(successful)/len(results)*100:.1f}%" if results else "0%"
            },
            "results": results
        }

        if output_file:
            # Ensure output goes to output directory
            output_dir = self.bin_dir.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_path}")

        # Print summary
        print("\n" + "=" * 50)
        print("EXECUTION SUMMARY")
        print("=" * 50)
        print(f"Total scripts: {report['summary']['total_scripts']}")
        print(f"Successful: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success rate: {report['summary']['success_rate']}")

        if failed:
            print("\nFailed scripts:")
            for result in failed:
                print(f"• {result['script']}: {result['stderr'][:100]}...")


def main():
    parser = argparse.ArgumentParser(description="Run all metapub demo scripts")
    parser.add_argument("--list", action="store_true", help="List all available scripts")
    parser.add_argument("--script", help="Run a specific script by name")
    parser.add_argument("--args", nargs="*", help="Arguments to pass to the script")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per script in seconds")
    parser.add_argument("--exclude", nargs="*", default=[], help="Scripts to exclude from execution")
    parser.add_argument("--report", help="Save results report to JSON file")
    parser.add_argument("--continue-on-error", action="store_true", default=True,
                       help="Continue running other scripts if one fails")
    parser.add_argument("--verbose", action="store_true", help="Show script output in real-time")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between scripts in seconds")
    parser.add_argument("--quick-test", action="store_true", help="Run only fast, reliable scripts")

    args = parser.parse_args()

    runner = DemoRunner()

    if args.list:
        runner.list_scripts()
        return

    if args.script:
        # Run single script
        script_path = runner.bin_dir / args.script
        if not script_path.exists():
            logger.error(f"Script not found: {args.script}")
            sys.exit(1)

        result = runner.run_single_script(
            script_path,
            custom_args=args.args,
            timeout=args.timeout,
            capture_output=not args.verbose
        )

        if not args.verbose:
            print(result["stdout"])
            if result["stderr"]:
                print("STDERR:", result["stderr"], file=sys.stderr)

        sys.exit(0 if result["success"] else 1)

    # Run all scripts
    results = runner.run_all_scripts(
        timeout=args.timeout,
        continue_on_error=args.continue_on_error,
        exclude=args.exclude,
        delay_between_scripts=args.delay,
        quick_test=args.quick_test
    )

    runner.generate_report(results, args.report)


if __name__ == "__main__":
    main()
