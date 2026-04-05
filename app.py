import asyncio
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from leadgen.core import LeadGenerator
from leadgen.models import SearchRequest, ScraperSource

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route("/api/search", methods=["POST"])
def search():
    data = request.json or {}
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    location = data.get("location", None)
    max_results = data.get("max_results", 50)
    
    # Handle sources if provided
    raw_sources = data.get("sources", None)
    sources = None
    if raw_sources:
        sources = []
        for s in raw_sources:
            try:
                sources.append(ScraperSource(s))
            except ValueError:
                pass
    else:
        sources = [ScraperSource.LINKEDIN, ScraperSource.GOOGLE_MAPS, ScraperSource.SCRAPEGRAPH]
        
    search_req = SearchRequest(
        query=query,
        location=location,
        sources=sources,
        max_results=max_results
    )
    
    async def _do_search():
        async with LeadGenerator() as lg:
            return await lg.search(search_req)

    result = run_async(_do_search())
    
    return jsonify({
        "leads": [lead.model_dump() for lead in result.leads],
        "total": result.total,
        "sources_used": [s.value for s in result.sources_used],
        "errors": result.errors,
    })

@app.route("/api/lookup", methods=["POST"])
def lookup():
    data = request.json or {}
    company_name = data.get("company_name")
    if not company_name:
        return jsonify({"error": "No company_name provided"}), 400
        
    raw_sources = data.get("sources", None)
    sources = None
    if raw_sources:
        sources = [ScraperSource(s) for s in raw_sources if s in (ScraperSource.LINKEDIN.value, ScraperSource.GOOGLE_MAPS.value, ScraperSource.SCRAPEGRAPH.value)]

    async def _do_lookup():
        async with LeadGenerator() as lg:
            return await lg.lookup(company_name, sources=sources)

    result = run_async(_do_lookup())
    
    if result:
        return jsonify({"lead": result.model_dump()})
    else:
        return jsonify({"error": "Lead not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
