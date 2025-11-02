import typing as t
import argparse
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
load_dotenv()

from serpapi.google_search import GoogleSearch
import google.generativeai as genai


class ResearchAgent:
    """LLM-powered researcher that combines Gemini 2.5 Flash model with SerpAPI and cites sources."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        topn: int = 10,
        debug: bool = False,
        gemini_key: t.Optional[str] = None,
        serpapi_key: t.Optional[str] = None,
    ) -> None:
        self.model = model
        self.topn = topn
        self.debug = debug
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.serp_key = serpapi_key or os.getenv("SERPAPI_API_KEY")

        if not self.gemini_key or not self.serp_key:
            raise RuntimeError("GEMINI_API_KEY and SERPAPI_API_KEY must be set.")
            
        genai.configure(api_key=self.gemini_key)
        self.model_instance = genai.GenerativeModel(self.model)

        self.sys_prompt = (
        "You are a research assistant working as of the current date, 2025-11-02. Your task is to provide answers based on today's date, ensuring all information is current and accurate.\n"
        "When the user requests information about current events, such as live scores, ongoing matches, or recent data, you are required to search relevant, authoritative websites for the most up-to-date information and present it.\n"
        "If the user asks for real-time data like the score of a cricket match, use web search tools to find and provide the most accurate and current results available.\n"
        "Always cite the sources you reference in Markdown format, like this: [Source](https://example.com).\n"
        "Your responses should be concise, factual, and supported by the most recent information from trustworthy sources."
        )

    def _search_web(self, query: str) -> dict:
        """Search Google using SerpAPI and return structured results (title, snippet, link)."""
        if self.debug:
            print(f"[DEBUG] → SerpAPI query: '{query}'")

        search = GoogleSearch({"q": query, "api_key": self.serp_key, "num": self.topn})
        data = search.get_dict().get("organic_results", [])[: self.topn]

        results = []
        for r in data:
            title = r.get("title", "(untitled)")
            snippet = r.get("snippet", "(no snippet)")
            link = r.get("link", "")
            results.append({"title": title, "snippet": snippet, "url": link})

        return {"query": query, "results": results}

    def run(self, question: str) -> dict[str, t.Any]:
        """Main reasoning loop with citations."""
        steps: list[dict[str, t.Any]] = []

        if self.debug:
            print(f"[DEBUG] → Starting research on: {question}")

        search_prompt = (
            f"{self.sys_prompt}\n\n"
            f"User question: {question}\n\n"
            f"List up to 5 specific Google search queries (in JSON array format) "
            f"that will help answer the question. Example:\n"
            f'["topic 1", "topic 2"]'
        )

        response = self.model_instance.generate_content(search_prompt)
        search_queries_text = response.text.strip()

        try:
            queries = json.loads(search_queries_text)
            if not isinstance(queries, list):
                queries = [search_queries_text]
        except Exception:
            queries = [search_queries_text]

        if self.debug:
            print(f"[DEBUG] → Suggested queries: {queries}")

        with ThreadPoolExecutor() as pool:
            results = list(pool.map(self._search_web, queries))

        # Combine results and URLs
        combined_context_parts = []
        all_urls = []
        for search_block in results:
            q = search_block["query"]
            block_text = f"### Search: {q}\n"
            for r in search_block["results"]:
                title, snippet, url = r["title"], r["snippet"], r["url"]
                block_text += f"- {title}: {snippet}\n(Source: {url})\n"
                if url:
                    all_urls.append(url)
            combined_context_parts.append(block_text)

        combined_context = "\n".join(combined_context_parts)

        # final answer with citations
        if self.debug:
            print("[DEBUG] → Gemini generating final synthesis with citations...")

        final_prompt = (
            f"{self.sys_prompt}\n\n"
            f"User question: {question}\n\n"
            f"Here are the gathered search results (with URLs):\n\n"
            f"{combined_context}\n\n"
            f"Now write a detailed, well-structured, and factually correct answer. "
            f"At the end, include a short 'Sources' section listing all relevant URLs in Markdown format."
        )

        final_response = self.model_instance.generate_content(final_prompt)
        answer = final_response.text.strip()

        steps.append({"type": "assistant_answer", "content": answer})
        return {"question": question, "answer": answer, "sources": list(set(all_urls)), "steps": steps}


def _cli():
    """Command-line interface."""
    p = argparse.ArgumentParser(description="Gemini + SerpAPI ResearchAgent CLI (with citations)")
    p.add_argument("-q", "--query", required=True, help="Research question to answer.")
    p.add_argument("-m", "--model", default="gemini-2.5-flash")
    p.add_argument("-n", "--topn", type=int, default=10)
    p.add_argument("-o", "--outfile", type=Path, help="Output JSON file.")
    p.add_argument("-d", "--debug", action="store_true", help="Enable debug output.")
    cfg = p.parse_args()

    agent = ResearchAgent(model=cfg.model, topn=cfg.topn, debug=cfg.debug)
    result = agent.run(cfg.query)

    print("=" * 80)
    print(result["answer"])
    print("=" * 80)

    print("\nSources:")
    for url in result["sources"]:
        print("-", url)

    if cfg.outfile:
        cfg.outfile.write_text(json.dumps(result, indent=2))
        print(f"Saved detailed trace → {cfg.outfile}")


if __name__ == "__main__":
    _cli()
