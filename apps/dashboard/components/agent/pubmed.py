"""PubMed / NCBI E-utilities client for biomedical literature search."""

from __future__ import annotations

import re
import urllib.parse

import httpx

from config import NCBI_EMAIL, NCBI_API_KEY, NCBI_TOOL_NAME

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(
    query: str,
    max_results: int = 10,
    sort: str = "relevance",
) -> list[dict]:
    """Search PubMed and return list of {pmid, title, authors, year, abstract}."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": sort,
        "tool": NCBI_TOOL_NAME or "oura-health-assistant",
        "email": NCBI_EMAIL or "user@example.com",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    url = f"{BASE_URL}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    resp = httpx.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    id_list = data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return []

    # Fetch details for PMIDs
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
        "tool": NCBI_TOOL_NAME or "oura-health-assistant",
        "email": NCBI_EMAIL or "user@example.com",
    }
    if NCBI_API_KEY:
        fetch_params["api_key"] = NCBI_API_KEY

    fetch_url = f"{BASE_URL}/efetch.fcgi?{urllib.parse.urlencode(fetch_params)}"
    fetch_resp = httpx.get(fetch_url, timeout=15)
    fetch_resp.raise_for_status()

    import xml.etree.ElementTree as ET
    root = ET.fromstring(fetch_resp.text)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _el_text(article, ".//ArticleId[@IdType='pubmed']")
        if not pmid:
            pmid_el = article.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else None
        art = article.find(".//Article")
        if art is None:
            continue
        title_el = art.find(".//ArticleTitle")
        title = (title_el.text or "").strip() if title_el is not None else ""
        abstract_el = art.find(".//Abstract")
        abstract = ""
        if abstract_el is not None:
            abs_texts = abstract_el.findall(".//AbstractText")
            abstract = " ".join(t.text or "" for t in abs_texts)
        auth_list = article.find(".//AuthorList")
        authors = []
        if auth_list is not None:
            for a in auth_list.findall(".//Author"):
                last = a.find("LastName")
                init = a.find("Initials")
                if last is not None and last.text:
                    authors.append(f"{last.text} {init.text or ''}".strip())
        pubdate_el = article.find(".//PubDate")
        year = ""
        if pubdate_el is not None:
            year_el = pubdate_el.find("Year")
            if year_el is not None and year_el.text:
                year = (year_el.text or "").strip()[:4]
            else:
                medline_el = pubdate_el.find("MedlineDate")
                if medline_el is not None and medline_el.text:
                    match = re.search(r"\d{4}", medline_el.text)
                    if match:
                        year = match.group(0)
        articles.append({"pmid": pmid, "title": title, "authors": authors[:5], "year": year, "abstract": abstract[:500]})
    return articles


def _el_text(parent, path):
    el = parent.find(path)
    return el.text if el is not None and el.text else None
