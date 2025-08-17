#!/usr/bin/env python3
"""
Enhanced analysis utilities for FindIt coverage testing.

This module provides functions for detecting Open Access types, repository types,
alternative identifiers, and detailed failure categorization.
"""

import re
import json
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse


class OADetector:
    """Detect Open Access type and repository information from URLs and metadata."""
    
    # Repository URL patterns
    REPOSITORY_PATTERNS = {
        'PMC': [
            r'europepmc\.org',
            r'pubmedcentral\.nih\.gov',
            r'ncbi\.nlm\.nih\.gov/pmc',
            r'pmc\.ncbi\.nlm\.nih\.gov'
        ],
        'arXiv': [
            r'arxiv\.org'
        ],
        'bioRxiv': [
            r'biorxiv\.org'
        ],
        'medRxiv': [
            r'medrxiv\.org'
        ],
        'institutional': [
            r'\.edu/',
            r'\.ac\.uk/',
            r'repository\.',
            r'eprints\.',
            r'digital\.library\.',
            r'scholarworks\.',
            r'ir\.library\.',
            r'dspace\.',
            r'handle\.net'
        ],
        'researchgate': [
            r'researchgate\.net'
        ],
        'academia': [
            r'academia\.edu'
        ]
    }
    
    # Known Green OA repository indicators
    GREEN_OA_INDICATORS = {
        'PMC', 'arXiv', 'bioRxiv', 'medRxiv', 'institutional',
        'researchgate', 'academia'
    }
    
    # Known publisher repository patterns
    PUBLISHER_REPO_PATTERNS = {
        'springer': [r'link\.springer\.com', r'springeropen\.com'],
        'elsevier': [r'sciencedirect\.com'],
        'wiley': [r'onlinelibrary\.wiley\.com'],
        'nature': [r'nature\.com'],
        'plos': [r'plos\.org', r'plosjournals\.org'],
        'frontiers': [r'frontiersin\.org'],
        'mdpi': [r'mdpi\.com'],
        'bmj': [r'bmj\.com'],
        'taylor_francis': [r'tandfonline\.com'],
        'sage': [r'sagepub\.com']
    }
    
    @classmethod
    def detect_repository_type(cls, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect repository type and OA type from URL.
        
        Returns:
            Tuple of (repository_type, oa_type)
        """
        if not url:
            return None, None
        
        url_lower = url.lower()
        
        # Check repository patterns
        for repo_type, patterns in cls.REPOSITORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    oa_type = 'green' if repo_type in cls.GREEN_OA_INDICATORS else 'unknown'
                    return repo_type, oa_type
        
        # Check publisher repositories
        for publisher, patterns in cls.PUBLISHER_REPO_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return f'publisher_{publisher}', 'unknown'  # Need more analysis for OA type
        
        # Default to unknown
        return 'unknown', 'unknown'
    
    @classmethod
    def analyze_content_type(cls, content_type: str, url: str) -> Dict[str, Any]:
        """Analyze content type for additional OA indicators."""
        analysis = {
            'is_pdf': False,
            'is_html': False,
            'repository_hint': None
        }
        
        if not content_type:
            return analysis
        
        content_type_lower = content_type.lower()
        
        if 'pdf' in content_type_lower:
            analysis['is_pdf'] = True
        elif 'html' in content_type_lower:
            analysis['is_html'] = True
        
        # Some repositories serve PDFs with different content types
        if url and 'europepmc.org' in url.lower() and 'pdf' in url.lower():
            analysis['is_pdf'] = True
            analysis['repository_hint'] = 'PMC'
        
        return analysis


class AlternativeIdDetector:
    """Detect alternative identifiers in article metadata."""
    
    @classmethod
    def detect_alternative_ids(cls, article) -> Dict[str, Any]:
        """
        Detect alternative identifiers from article metadata.
        
        Args:
            article: PubMed article object
            
        Returns:
            Dictionary with alternative ID information
        """
        result = {
            'has_pmc': False,
            'has_arxiv_id': False,
            'has_alternative_ids': False,
            'other_identifiers': {}
        }
        
        if not article:
            return result
        
        # Check PMC ID
        pmc = getattr(article, 'pmc', None)
        if pmc:
            result['has_pmc'] = True
            result['has_alternative_ids'] = True
            result['other_identifiers']['pmc'] = pmc
        
        # Check for arXiv ID in various fields
        title = getattr(article, 'title', '') or ''
        abstract = getattr(article, 'abstract', '') or ''
        
        arxiv_patterns = [
            r'arXiv:(\d{4}\.\d{4,5})',
            r'arxiv\.org/abs/(\d{4}\.\d{4,5})'
        ]
        
        for pattern in arxiv_patterns:
            for text in [title, abstract]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result['has_arxiv_id'] = True
                    result['has_alternative_ids'] = True
                    result['other_identifiers']['arxiv'] = match.group(1)
                    break
            if result['has_arxiv_id']:
                break
        
        # Check for other common identifiers
        doi = getattr(article, 'doi', None)
        if doi:
            result['other_identifiers']['doi'] = doi
        
        pii = getattr(article, 'pii', None)
        if pii:
            result['other_identifiers']['pii'] = pii
            result['has_alternative_ids'] = True
        
        return result


class FailureAnalyzer:
    """Analyze and categorize PDF finding failures."""
    
    FAILURE_CATEGORIES = {
        'no_doi_available': 'Article has no DOI identifier',
        'doi_present_but_no_pdf': 'DOI exists but no PDF URL found',
        'journal_not_supported': 'Journal not in FindIt registry',
        'publisher_not_supported': 'Publisher not supported by FindIt',
        'paywall_detected': 'PDF behind paywall',
        'link_broken': 'PDF link exists but broken/inaccessible',
        'no_journal_info': 'Missing journal information',
        'findit_error': 'FindIt processing error',
        'network_error': 'Network or connectivity issue',
        'unknown_error': 'Unclassified error'
    }
    
    @classmethod
    def categorize_failure(cls, article, findit_reason: str, error_msg: str = None) -> str:
        """
        Categorize the reason for PDF finding failure.
        
        Args:
            article: PubMed article object
            findit_reason: Reason from FindIt
            error_msg: Additional error message
            
        Returns:
            Detailed failure reason category
        """
        if not article:
            return 'no_article_metadata'
        
        # Check for missing DOI
        doi = getattr(article, 'doi', None)
        if not doi or doi.strip() == '':
            return 'no_doi_available'
        
        # Check for missing journal info
        journal = getattr(article, 'journal', None)
        if not journal or journal.strip() == '':
            return 'no_journal_info'
        
        # Analyze FindIt reason
        if findit_reason:
            reason_lower = findit_reason.lower()
            
            if 'no pdf' in reason_lower or 'no_pdf' in reason_lower:
                return 'doi_present_but_no_pdf'
            elif 'link' in reason_lower and ('no' in reason_lower or 'not found' in reason_lower):
                return 'journal_not_supported'
            elif 'paywall' in reason_lower or 'subscription' in reason_lower:
                return 'paywall_detected'
            elif 'error' in reason_lower or 'exception' in reason_lower:
                return 'findit_error'
        
        # Analyze error message
        if error_msg:
            error_lower = error_msg.lower()
            
            if 'network' in error_lower or 'connection' in error_lower or 'timeout' in error_lower:
                return 'network_error'
            elif 'not found' in error_lower and 'journal' in error_lower:
                return 'journal_not_supported'
            elif 'broken' in error_lower or '404' in error_lower or '403' in error_lower:
                return 'link_broken'
        
        return 'unknown_error'


class MeshExtractor:
    """Extract MeSH (Medical Subject Headings) terms from articles."""
    
    @classmethod
    def extract_mesh_terms(cls, article) -> List[Dict[str, Any]]:
        """
        Extract MeSH terms using metapub's existing functionality.
        
        Args:
            article: PubMed article object with mesh attribute
            
        Returns:
            List of MeSH term dictionaries
        """
        mesh_terms = []
        
        if not article or not hasattr(article, 'mesh'):
            return mesh_terms
        
        for mesh_id, mesh_data in article.mesh.items():
            # Base MeSH term (without qualifier)
            mesh_terms.append({
                'mesh_id': mesh_id,
                'mesh_term': mesh_data['descriptor_name'],
                'is_major_topic': mesh_data['descriptor_major_topic'],
                'qualifier': None,
                'qualifier_major_topic': False
            })
            
            # MeSH term with qualifiers (subheadings)
            for qualifier in mesh_data.get('qualifiers', []):
                mesh_terms.append({
                    'mesh_id': mesh_id,
                    'mesh_term': mesh_data['descriptor_name'],
                    'is_major_topic': mesh_data['descriptor_major_topic'],
                    'qualifier': qualifier['qualifier_name'],
                    'qualifier_major_topic': qualifier.get('qualifier_major_topic', False)
                })
        
        return mesh_terms
    
    @classmethod
    def get_mesh_summary(cls, mesh_terms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for MeSH terms.
        
        Args:
            mesh_terms: List of MeSH term dictionaries
            
        Returns:
            Summary dictionary with counts and flags
        """
        if not mesh_terms:
            return {
                'has_mesh_terms': False,
                'mesh_term_count': 0,
                'major_mesh_count': 0,
                'unique_descriptors': 0,
                'has_qualifiers': False
            }
        
        unique_descriptors = set()
        major_topics = 0
        has_qualifiers = False
        
        for term in mesh_terms:
            unique_descriptors.add(term['mesh_term'])
            if term['is_major_topic']:
                major_topics += 1
            if term['qualifier']:
                has_qualifiers = True
        
        return {
            'has_mesh_terms': True,
            'mesh_term_count': len(mesh_terms),
            'major_mesh_count': major_topics,
            'unique_descriptors': len(unique_descriptors),
            'has_qualifiers': has_qualifiers
        }


class MetadataEnhancer:
    """Extract enhanced metadata from articles."""
    
    ARTICLE_TYPE_PATTERNS = {
        'research': [
            r'research article', r'original article', r'original research',
            r'research paper', r'empirical study'
        ],
        'review': [
            r'review', r'systematic review', r'meta-analysis',
            r'literature review', r'narrative review'
        ],
        'editorial': [
            r'editorial', r'editor', r'commentary', r'opinion'
        ],
        'case_report': [
            r'case report', r'case study', r'case series'
        ],
        'letter': [
            r'letter', r'correspondence', r'reply', r'response'
        ],
        'news': [
            r'news', r'announcement', r'update'
        ],
        'correction': [
            r'correction', r'corrigendum', r'erratum', r'retraction'
        ]
    }
    
    @classmethod
    def extract_publication_year(cls, article) -> Optional[int]:
        """Extract publication year from article."""
        if not article:
            return None
        
        # Try different date fields
        date_fields = ['year', 'pub_date', 'date', 'publication_date']
        
        for field in date_fields:
            value = getattr(article, field, None)
            if value:
                try:
                    # Handle various date formats
                    if isinstance(value, int):
                        return value
                    elif isinstance(value, str):
                        # Extract year from date string
                        year_match = re.search(r'(\d{4})', value)
                        if year_match:
                            year = int(year_match.group(1))
                            if 1900 <= year <= 2030:  # Reasonable year range
                                return year
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    @classmethod
    def detect_article_type(cls, article) -> Optional[str]:
        """Detect article type from title and metadata."""
        if not article:
            return None
        
        title = getattr(article, 'title', '') or ''
        abstract = getattr(article, 'abstract', '') or ''
        
        # Combine title and first part of abstract for analysis
        text_to_analyze = (title + ' ' + abstract[:200]).lower()
        
        for article_type, patterns in cls.ARTICLE_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_to_analyze, re.IGNORECASE):
                    return article_type
        
        return 'research'  # Default assumption
    
    @classmethod
    def check_retraction(cls, article) -> bool:
        """Check if article appears to be retracted."""
        if not article:
            return False
        
        title = getattr(article, 'title', '') or ''
        abstract = getattr(article, 'abstract', '') or ''
        
        retraction_indicators = [
            r'retract', r'withdraw', r'correction', r'erratum'
        ]
        
        text_to_check = (title + ' ' + abstract).lower()
        
        for indicator in retraction_indicators:
            if re.search(indicator, text_to_check):
                return True
        
        return False


def get_findit_registry_status(journal: str, publisher: str) -> Tuple[bool, bool]:
    """
    Check if journal/publisher is supported by FindIt registry.
    
    This is a placeholder - in real implementation, this would check
    against the actual FindIt registry database.
    
    Returns:
        Tuple of (journal_in_registry, publisher_supported)
    """
    # TODO: Implement actual registry checking
    # For now, return reasonable defaults
    
    if not journal:
        return False, False
    
    # Some heuristics based on common patterns
    journal_lower = journal.lower()
    publisher_lower = (publisher or '').lower()
    
    # Known major publishers that are well-supported
    major_publishers = [
        'elsevier', 'springer', 'wiley', 'nature', 'taylor', 'sage',
        'oxford', 'cambridge', 'ieee', 'acm', 'aaas', 'acs'
    ]
    
    publisher_supported = any(pub in publisher_lower for pub in major_publishers)
    
    # Assume journal is in registry if it's from a major publisher
    # or if it has common academic journal indicators
    journal_indicators = ['journal', 'proceedings', 'transactions', 'letters']
    journal_in_registry = (
        publisher_supported or 
        any(indicator in journal_lower for indicator in journal_indicators)
    )
    
    return journal_in_registry, publisher_supported