"""
Android bridge for Chaquopy integration
Exposes Python functions for WebView communication
"""

import json
from typing import Dict, Any, List, Optional
from .scraper import LeadScraper
from .models import Lead, LeadStatus


class AndroidBridge:
    """Bridge between Android/WebView and Python scraping logic"""

    def __init__(
        self,
        linkedin_session: Optional[str] = None,
        scrapegraph_key: Optional[str] = None
    ):
        """Initialize the bridge"""
        self.scraper = LeadScraper(linkedin_session, scrapegraph_key)
        self.current_search_results = []
        self.current_leads_db = []

    # ===== Search Operations =====

    def search_industry(self, industry: str, location: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Search for leads by industry
        Args: {"industry": "Software Development", "location": "San Francisco", "limit": 50}
        """
        try:
            print(f"[Android] Searching industry: {industry}")
            results = self.scraper.search_by_industry(
                industry=industry,
                location=location,
                limit=limit,
                enrich=True
            )

            self.current_search_results = results
            return self._success_response(
                data=[lead.to_dict() for lead in results],
                message=f"Found {len(results)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    def search_company(self, company_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for leads by company
        Args: {"company_name": "Google", "limit": 20}
        """
        try:
            print(f"[Android] Searching company: {company_name}")
            results = self.scraper.search_by_company(
                company_name=company_name,
                limit=limit,
                enrich=True
            )

            self.current_search_results = results
            return self._success_response(
                data=[lead.to_dict() for lead in results],
                message=f"Found {len(results)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    def search_location(
        self,
        location: str,
        keywords: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search for leads by location
        Args: {"location": "New York", "keywords": "Sales", "limit": 50}
        """
        try:
            print(f"[Android] Searching location: {location}")
            results = self.scraper.search_by_location(
                location=location,
                keywords=keywords,
                limit=limit,
                use_gmap=True,
                enrich=True
            )

            self.current_search_results = results
            return self._success_response(
                data=[lead.to_dict() for lead in results],
                message=f"Found {len(results)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    def search_keywords(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Advanced search by keywords
        Args: {"keywords": "CTO", "location": "San Francisco", "limit": 50}
        """
        try:
            print(f"[Android] Searching keywords: {keywords}")
            results = self.scraper.search_by_keywords(
                keywords=keywords,
                location=location,
                limit=limit,
                enrich=True
            )

            self.current_search_results = results
            return self._success_response(
                data=[lead.to_dict() for lead in results],
                message=f"Found {len(results)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    # ===== Lead Management =====

    def get_current_results(self) -> Dict[str, Any]:
        """Get current search results"""
        try:
            return self._success_response(
                data=[lead.to_dict() for lead in self.current_search_results],
                message=f"Retrieved {len(self.current_search_results)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    def add_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a lead to the database
        Args: {lead_dict}
        """
        try:
            lead = self._dict_to_lead(lead_data)
            lead.id = str(len(self.current_leads_db))
            self.current_leads_db.append(lead)
            return self._success_response(
                data={"id": lead.id, "lead": lead.to_dict()},
                message="Lead added successfully"
            )
        except Exception as e:
            return self._error_response(str(e))

    def get_leads(self) -> Dict[str, Any]:
        """Get all leads from database"""
        try:
            return self._success_response(
                data=[lead.to_dict() for lead in self.current_leads_db],
                message=f"Retrieved {len(self.current_leads_db)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a lead
        Args: {"lead_id": "0", "updates": {...}}
        """
        try:
            for i, lead in enumerate(self.current_leads_db):
                if lead.id == lead_id:
                    # Update fields
                    for key, value in updates.items():
                        if hasattr(lead, key):
                            if key == "status" and isinstance(value, str):
                                lead.status = LeadStatus(value)
                            else:
                                setattr(lead, key, value)

                    from datetime import datetime
                    lead.last_updated = datetime.now().isoformat()
                    self.current_leads_db[i] = lead

                    return self._success_response(
                        data=lead.to_dict(),
                        message="Lead updated successfully"
                    )

            return self._error_response(f"Lead not found: {lead_id}")
        except Exception as e:
            return self._error_response(str(e))

    def delete_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Delete a lead
        Args: {"lead_id": "0"}
        """
        try:
            self.current_leads_db = [
                lead for lead in self.current_leads_db if lead.id != lead_id
            ]
            return self._success_response(
                message=f"Lead {lead_id} deleted successfully"
            )
        except Exception as e:
            return self._error_response(str(e))

    def search_leads(self, query: str) -> Dict[str, Any]:
        """
        Search leads in database
        Args: {"query": "company_name or contact_name"}
        """
        try:
            query_lower = query.lower()
            results = [
                lead for lead in self.current_leads_db
                if query_lower in lead.company_name.lower()
                or query_lower in lead.contact_name.lower()
                or query_lower in lead.email.lower()
            ]

            return self._success_response(
                data=[lead.to_dict() for lead in results],
                message=f"Found {len(results)} matching leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    # ===== Analytics =====

    def get_stats(self) -> Dict[str, Any]:
        """Get lead database statistics"""
        try:
            total = len(self.current_leads_db)
            by_status = {}
            by_industry = {}
            avg_score = 0

            if total > 0:
                for lead in self.current_leads_db:
                    status = lead.status.value
                    by_status[status] = by_status.get(status, 0) + 1

                    industry = lead.industry or "Unknown"
                    by_industry[industry] = by_industry.get(industry, 0) + 1

                avg_score = sum(lead.lead_score for lead in self.current_leads_db) // total

            return self._success_response(
                data={
                    "total_leads": total,
                    "by_status": by_status,
                    "by_industry": by_industry,
                    "avg_lead_score": avg_score
                }
            )
        except Exception as e:
            return self._error_response(str(e))

    def export_leads(self, format: str = "json") -> Dict[str, Any]:
        """
        Export leads
        Args: {"format": "json" or "csv"}
        """
        try:
            if format == "json":
                data = json.dumps(
                    [lead.to_dict() for lead in self.current_leads_db],
                    indent=2
                )
            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                if self.current_leads_db:
                    writer = csv.DictWriter(
                        output,
                        fieldnames=self.current_leads_db[0].to_dict().keys()
                    )
                    writer.writeheader()
                    for lead in self.current_leads_db:
                        writer.writerow(lead.to_dict())
                data = output.getvalue()
            else:
                return self._error_response(f"Unsupported format: {format}")

            return self._success_response(
                data={"export": data},
                message=f"Exported {len(self.current_leads_db)} leads"
            )
        except Exception as e:
            return self._error_response(str(e))

    # ===== Utility Methods =====

    def _dict_to_lead(self, data: Dict[str, Any]) -> Lead:
        """Convert dict to Lead object"""
        status = data.get("status", "new")
        if isinstance(status, str):
            status = LeadStatus(status)

        source = data.get("source", "linkedin")
        from .models import ScrapeSource
        if isinstance(source, str):
            source = ScrapeSource(source)

        return Lead(
            company_name=data.get("company_name", ""),
            contact_name=data.get("contact_name", ""),
            job_title=data.get("job_title", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            linkedin_url=data.get("linkedin_url", ""),
            industry=data.get("industry", ""),
            location=data.get("location", ""),
            company_size=data.get("company_size", ""),
            revenue_estimate=data.get("revenue_estimate", ""),
            lead_score=data.get("lead_score", 0),
            status=status,
            notes=data.get("notes", ""),
            source=source,
            tags=data.get("tags", [])
        )

    def _success_response(
        self,
        data: Any = None,
        message: str = "Success"
    ) -> Dict[str, Any]:
        """Format success response for WebView"""
        return {
            "success": True,
            "message": message,
            "data": data or {}
        }

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Format error response for WebView"""
        return {
            "success": False,
            "error": error,
            "data": {}
        }

    def handle_message(self, message_json: str) -> str:
        """
        Handle WebView messages
        Called from WebMessageListener in Android

        Args:
            message_json: JSON string with action and params

        Returns:
            JSON response string
        """
        try:
            message = json.loads(message_json)
            action = message.get("action")
            params = message.get("params", {})

            print(f"[Android] Received action: {action}")

            if action == "search_industry":
                result = self.search_industry(**params)
            elif action == "search_company":
                result = self.search_company(**params)
            elif action == "search_location":
                result = self.search_location(**params)
            elif action == "search_keywords":
                result = self.search_keywords(**params)
            elif action == "add_lead":
                result = self.add_lead(params.get("lead_data", {}))
            elif action == "get_leads":
                result = self.get_leads()
            elif action == "update_lead":
                result = self.update_lead(
                    params.get("lead_id", ""),
                    params.get("updates", {})
                )
            elif action == "delete_lead":
                result = self.delete_lead(params.get("lead_id", ""))
            elif action == "search_leads":
                result = self.search_leads(params.get("query", ""))
            elif action == "get_stats":
                result = self.get_stats()
            elif action == "export_leads":
                result = self.export_leads(params.get("format", "json"))
            elif action == "get_results":
                result = self.get_current_results()
            else:
                result = self._error_response(f"Unknown action: {action}")

            return json.dumps(result)

        except json.JSONDecodeError as e:
            error = self._error_response(f"Invalid JSON: {str(e)}")
            return json.dumps(error)
        except Exception as e:
            error = self._error_response(f"Error: {str(e)}")
            return json.dumps(error)


# Global bridge instance for Chaquopy
_bridge = None


def get_bridge(linkedin_session=None, scrapegraph_key=None) -> AndroidBridge:
    """Get or create the Android bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = AndroidBridge(linkedin_session, scrapegraph_key)
    return _bridge


def bridge_handler(message_json: str) -> str:
    """Direct handler for WebMessageListener"""
    bridge = get_bridge()
    return bridge.handle_message(message_json)
