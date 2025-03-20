"""Search tool using Serper.dev API."""

from __future__ import annotations

import datetime
import logging
import os
from typing import Any, Literal


logger = logging.getLogger(__name__)


class SerperTool:
    """A tool for searching the web using the Serper.dev API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://google.serper.dev",
        n_results: int = 10,
        save_results: bool = False,
    ):
        """Initialize the SerperTool.

        Args:
            api_key: Serper.dev API key (defaults to SERPER_API_KEY env var)
            base_url: Base URL for the Serper API
            n_results: Number of results to return
            save_results: Whether to save results to file
        """
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        if not self.api_key:
            error_msg = "SERPER_API_KEY not found in environment variables"
            raise ValueError(error_msg)

        self.base_url = base_url
        self.n_results = n_results
        self.save_results = save_results

    async def search(
        self,
        query: str,
        *,
        search_type: Literal["search", "news"] = "search",
        location: str | None = None,
        country: str | None = None,
        language: str | None = None,
        date_range: Literal["d", "w", "m", "y"] | None = None,
    ) -> str | dict[str, Any]:
        """Search the web using Serper.dev API.

        Args:
            query: Search query string
            search_type: Type of search ('search' or 'news')
            location: Geographic location for search
            country: Country code (e.g. 'us', 'gb')
            language: Language code (e.g. 'en', 'es')
            date_range: Time range for results
                        ('h'=hour, 'd'=day, 'w'=week, 'm'=month, 'y'=year)

        Returns:
            Markdown-formatted search results or JSON dict if return_json=True
        """
        import anyenv

        if search_type not in {"search", "news"}:
            error_msg = f"Invalid search type: {search_type}. Must be 'search' or 'news'"
            raise ValueError(error_msg)

        # Build payload
        payload = {"q": query, "num": self.n_results}
        if location:
            payload["location"] = location
        if country:
            payload["gl"] = country.lower()
        if language:
            payload["hl"] = language.lower()
        if date_range:
            payload["tbs"] = f"qdr:{date_range}"

        # Make API request
        search_url = f"{self.base_url}/{search_type}"
        assert self.api_key, "API key is required"
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        results = await anyenv.post_json(
            search_url, headers=headers, json_data=payload, return_type=dict
        )

        # Process results
        processed_results = self._process_results(results, search_type)

        # Save to file if requested
        if self.save_results:
            self._save_results_to_file(processed_results)

        # Convert to markdown
        return self._format_as_markdown(processed_results, query, search_type)

    def _process_results(self, results: dict, search_type: str) -> dict[str, Any]:
        """Process raw API results into a cleaner format.

        Args:
            results: Raw results from the API
            search_type: Type of search that was performed

        Returns:
            Processed results dictionary
        """
        # Add search parameters to results
        query = results.get("searchParameters", {}).get("q", "")
        params = {"query": query, "type": search_type}
        credit = results.get("credits", 1)
        processed = {"searchParameters": params, "credits": credit}

        # Process different result types
        if search_type == "search":
            # Knowledge Graph
            if kg := results.get("knowledgeGraph"):
                processed["knowledgeGraph"] = {
                    "title": kg.get("title", ""),
                    "type": kg.get("type", ""),
                    "website": kg.get("website", ""),
                    "description": kg.get("description", ""),
                    "attributes": kg.get("attributes", {}),
                }

            # Organic results
            if organic := results.get("organic"):
                processed["organic"] = [
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    for item in organic[: self.n_results]
                    if "title" in item and "link" in item
                ]

            # People also ask
            if paa := results.get("peopleAlsoAsk"):
                processed["peopleAlsoAsk"] = [
                    {
                        "question": item.get("question", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    for item in paa[: self.n_results]
                    if "question" in item
                ]

            # Related searches
            if related := results.get("relatedSearches"):
                processed["relatedSearches"] = [
                    {"query": item.get("query", "")}
                    for item in related[: self.n_results]
                    if "query" in item
                ]

        elif search_type == "news":
            # News results
            if news := results.get("news"):
                processed["news"] = [
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "date": item.get("date", ""),
                        "source": item.get("source", ""),
                    }
                    for item in news[: self.n_results]
                    if "title" in item and "link" in item
                ]

        return processed

    def _format_as_markdown(
        self, results: dict[str, Any], query: str, search_type: str
    ) -> str:
        """Format search results as markdown text.

        Args:
            results: Processed search results
            query: Original search query
            search_type: Type of search performed

        Returns:
            Markdown-formatted string of search results
        """
        md_parts = [f"# Search Results: {query}\n"]

        # Knowledge Graph section
        if kg := results.get("knowledgeGraph"):
            md_parts.append(f"## {kg.get('title')}")

            if kg_type := kg.get("type"):
                md_parts.append(f"*{kg_type}*\n")

            if desc := kg.get("description"):
                md_parts.append(f"{desc}\n")

            if website := kg.get("website"):
                md_parts.append(f"Website: [{website}]({website})\n")

            if attrs := kg.get("attributes"):
                md_parts.append("### Details")
                for key, value in attrs.items():
                    md_parts.append(f"- **{key}**: {value}")
                md_parts.append("")

        # Organic search results
        if organic := results.get("organic"):
            md_parts.append("## Search Results")

            for i, result in enumerate(organic, 1):
                title = result.get("title", "No title")
                link = result.get("link", "#")
                snippet = result.get("snippet", "No description available")

                md_parts.append(f"### {i}. [{title}]({link})")
                md_parts.append(f"{snippet}\n")
                md_parts.append(f"[Read more]({link})\n")

        # People also ask
        if paa := results.get("peopleAlsoAsk"):
            md_parts.append("## People Also Ask")

            for item in paa:
                question = item.get("question", "")
                snippet = item.get("snippet", "No answer available")

                md_parts.append(f"### Q: {question}")
                md_parts.append(f"A: {snippet}\n")

        # News results
        if news := results.get("news"):
            md_parts.append("## News")

            for i, item in enumerate(news, 1):
                title = item.get("title", "No title")
                link = item.get("link", "#")
                source = item.get("source", "")
                date = item.get("date", "")
                snippet = item.get("snippet", "")

                md_parts.append(f"### {i}. [{title}]({link})")

                if source or date:
                    sources = []
                    if source:
                        sources.append(f"Source: {source}")
                    if date:
                        sources.append(f"Date: {date}")
                    md_parts.append(f"*{' | '.join(sources)}*")

                if snippet:
                    md_parts.append(f"\n{snippet}\n")

                md_parts.append(f"[Read more]({link})\n")

        # Related searches
        if related := results.get("relatedSearches"):
            md_parts.append("## Related Searches")

            for item in related:
                related_query = item.get("query", "")
                if related_query:
                    md_parts.append(f"- {related_query}")

        # Footer with search metadata
        result_count = 0
        if search_type == "search" and "organic" in results:
            result_count = len(results["organic"])
        elif search_type == "news" and "news" in results:
            result_count = len(results["news"])

        # Add the footer
        md_parts.append(f"\n---\n*Search type: {search_type} | Results: {result_count}*")

        return "\n".join(md_parts)

    def _save_results_to_file(self, results: dict):
        """Save results to a file with timestamp in filename.

        Args:
            results: Processed results to save
        """
        import anyenv
        import upath

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = upath.UPath(f"search_results_{timestamp}.json")

        try:
            with filename.open("w", encoding="utf-8") as file:
                text = anyenv.dump_json(results, indent=True)
                file.write(text)
            logger.info("Results saved to %r", filename)
        except OSError as e:
            error_msg = f"Failed to save results to file: {e}"
            logger.exception(error_msg)


async def example():
    """Example usage of SerperTool."""
    tool = SerperTool()
    results = await tool.search("Python programming")
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
