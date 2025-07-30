"""Main client class for ScoutML API."""

import json
import sys
import time
from typing import Dict, List, Optional, Union, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

from .config import Config
from .exceptions import (
    ScoutMLError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError
)


class ScoutMLClient:
    """Main client for interacting with ScoutML API."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        if self.config.is_configured:
            self.session.headers.update(self.config.headers)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        url = self.config.get_endpoint(endpoint)
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.config.default_timeout,
                **kwargs
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or unauthorized access")
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise ScoutMLError("Failed to connect to API. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise ScoutMLError("Request timed out. Try again later.")
        except requests.exceptions.RequestException as e:
            raise ScoutMLError(f"Request failed: {str(e)}")
    
    def _poll_task(self, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """Poll a task until completion."""
        poll_interval = 2  # Start with 2 seconds
        elapsed = 0
        
        # Show progress if tqdm is available and we're in a TTY
        show_progress = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if show_progress:
            pbar = tqdm(total=max_wait, desc="Processing", unit="s", leave=False)
        
        while elapsed < max_wait:
            # Get task status
            try:
                result = self._request("GET", f"tasks/{task_id}/")
            except Exception as e:
                if show_progress:
                    pbar.close()
                raise ScoutMLError(f"Failed to poll task status: {str(e)}")
            
            status = result.get("status", "UNKNOWN")
            
            if status in ["COMPLETED", "SUCCESS"]:
                if show_progress:
                    pbar.close()
                # The result might be in different fields
                return result.get("result") or result.get("data") or result
            elif status in ["FAILED", "ERROR"]:
                if show_progress:
                    pbar.close()
                error_msg = result.get("error", result.get("detail", "Task failed without error message"))
                raise ScoutMLError(f"Task failed: {error_msg}")
            elif status not in ["PROCESSING", "PENDING", "RUNNING"]:
                # Unknown status, return the whole result
                if show_progress:
                    pbar.close()
                return result
            
            # Wait before next poll
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            if show_progress:
                pbar.update(poll_interval)
            
            # Increase poll interval up to 5 seconds
            poll_interval = min(poll_interval * 1.5, 5)
        
        if show_progress:
            pbar.close()
        
        raise ScoutMLError(f"Task timed out after {max_wait} seconds")
    
    def _handle_async_response(self, response: Dict[str, Any], max_wait: int = 300) -> Dict[str, Any]:
        """Handle async task responses by polling if needed."""
        if response.get("status") == "PROCESSING" and "task_id" in response:
            # This is an async task, poll for result
            return self._poll_task(response["task_id"], max_wait)
        elif response.get("status") in ["SUCCESS", "COMPLETED"] and "result" in response:
            # This is a completed task response, return just the result
            return response["result"]
        else:
            # This is a direct response or unknown format
            return response
    
    # Search endpoints
    
    def semantic_search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_citations: Optional[int] = None,
        venue: Optional[str] = None,
        sota_only: bool = False,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform semantic search on papers."""
        data = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "sota_only": sota_only
        }
        
        # Add optional filters
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        if min_citations:
            data["min_citations"] = min_citations
        if venue:
            data["venue"] = venue
        if domain:
            data["domain"] = domain
        
        return self._request("POST", "papers/semantic-search/", json=data)
    
    def method_search(
        self,
        method: str,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "citations",
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search papers by specific method."""
        data = {
            "method": method,
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by
        }
        
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        if domain:
            data["domain"] = domain
        
        return self._request("POST", "papers/method-search/", json=data)
    
    def dataset_search(
        self,
        dataset: str,
        limit: int = 20,
        offset: int = 0,
        include_benchmarks: bool = True,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search papers using specific dataset."""
        data = {
            "dataset": dataset,
            "limit": limit,
            "offset": offset,
            "include_benchmarks": include_benchmarks
        }
        
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        
        return self._request("POST", "papers/dataset-search/", json=data)
    
    def get_paper(
        self,
        arxiv_id: str,
        include_similar: bool = False,
        similar_limit: int = 5
    ) -> Dict[str, Any]:
        """Get detailed information about a specific paper."""
        params = {}
        if include_similar:
            params["include_similar"] = "true"
            params["similar_limit"] = similar_limit
        
        return self._request("GET", f"papers/{arxiv_id}/", params=params)
    
    # Comparison & Synthesis endpoints
    
    def compare_papers(self, paper_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple papers."""
        if len(paper_ids) < 2:
            raise ValueError("At least 2 paper IDs required for comparison")
        if len(paper_ids) > 10:
            raise ValueError("Maximum 10 papers can be compared at once")
        
        data = {"paper_ids": paper_ids}
        response = self._request("POST", "compare/papers/", json=data)
        return self._handle_async_response(response)
    
    def generate_literature_review(
        self,
        topic: str,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_citations: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Generate a literature review on a topic."""
        data = {
            "topic": topic,
            "min_citations": min_citations,
            "limit": limit
        }
        
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        
        response = self._request("POST", "synthesis/literature-review/", json=data)
        return self._handle_async_response(response)
    
    def get_similar_papers(self, arxiv_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get papers similar to a given paper using PostgreSQL endpoint."""
        params = {"limit": limit}
        return self._request("GET", f"papers/{arxiv_id}/similar/", params=params)
    
    def find_similar_papers(
        self,
        paper_id: Optional[str] = None,
        abstract_text: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Find papers similar to a given paper or abstract (MongoDB version)."""
        if not paper_id and not abstract_text:
            raise ValueError("Either paper_id or abstract_text must be provided")
        if paper_id and abstract_text:
            raise ValueError("Provide either paper_id or abstract_text, not both")
        
        data = {
            "limit": limit,
            "similarity_threshold": similarity_threshold
        }
        
        if paper_id:
            data["paper_id"] = paper_id
        else:
            data["abstract_text"] = abstract_text
        
        return self._request("POST", "papers/find-similar/", json=data)
    
    # Research Intelligence endpoints
    
    def get_reproducibility_ranked(
        self,
        domain: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get papers ranked by reproducibility score."""
        data = {
            "limit": limit,
            "offset": offset
        }
        
        if domain:
            data["domain"] = domain
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        
        return self._request("POST", "insights/reproducibility-ranked/", json=data)
    
    def analyze_compute_requirements(
        self,
        method: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        sample_size: int = 10
    ) -> Dict[str, Any]:
        """Analyze compute requirements and trends."""
        data = {
            "sample_size": sample_size
        }
        
        if method:
            data["method"] = method
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        
        return self._request("POST", "insights/compute-requirements/", json=data)
    
    def analyze_funding(
        self,
        institution: Optional[str] = None,
        funding_source: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        limit: int = 20,
        sample_size: int = 5
    ) -> Dict[str, Any]:
        """Analyze funding sources and trends."""
        data = {
            "limit": limit,
            "sample_size": sample_size
        }
        
        if institution:
            data["institution"] = institution
        if funding_source:
            data["funding_source"] = funding_source
        if year_min:
            data["year_min"] = year_min
        if year_max:
            data["year_max"] = year_max
        
        return self._request("POST", "insights/funding-analysis/", json=data)
    
    # Batch operations
    
    def batch_get_papers(
        self,
        arxiv_ids: List[str],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """Get details for multiple papers with progress bar."""
        results = []
        
        iterator = tqdm(arxiv_ids, desc="Fetching papers") if show_progress else arxiv_ids
        
        for arxiv_id in iterator:
            try:
                paper = self.get_paper(arxiv_id)
                results.append(paper["paper"])
            except NotFoundError:
                results.append({"arxiv_id": arxiv_id, "error": "Not found"})
            except Exception as e:
                results.append({"arxiv_id": arxiv_id, "error": str(e)})
        
        return results
    
    # Agent endpoints
    
    def implement_guide(
        self,
        arxiv_id: str,
        target_framework: str = "pytorch",
        experience_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Get implementation guide for a paper."""
        data = {
            "arxiv_id": arxiv_id,
            "target_framework": target_framework,
            "experience_level": experience_level
        }
        response = self._request("POST", "agent/implement-guide/", json=data)
        return self._handle_async_response(response)
    
    def research_critique(
        self,
        arxiv_id: str,
        critique_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive research critique."""
        data = {
            "arxiv_id": arxiv_id,
            "critique_aspects": critique_aspects or ["methodology", "experiments", "claims", "reproducibility"]
        }
        response = self._request("POST", "agent/research-critique/", json=data)
        return self._handle_async_response(response)
    
    def solve_limitations(
        self,
        arxiv_id: str,
        focus_limitation: Optional[str] = None,
        acceptable_tradeoffs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get solutions for paper limitations."""
        data = {
            "arxiv_id": arxiv_id,
            "focus_limitation": focus_limitation,
            "acceptable_tradeoffs": acceptable_tradeoffs or []
        }
        response = self._request("POST", "agent/limitation-solver/", json=data)
        return self._handle_async_response(response)
    
    def design_experiment(
        self,
        base_paper: str,
        hypothesis: str,
        resources: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Design experiment to test hypothesis."""
        data = {
            "base_paper": base_paper,
            "hypothesis": hypothesis,
            "resources": resources or {}
        }
        response = self._request("POST", "agent/experiment-designer/", json=data)
        return self._handle_async_response(response)