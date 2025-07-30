import traceback
from typing import Optional

from arbol import asection, aprint
from ddgs import DDGS

from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.python.pip_utils import pip_install_single_package


def summary_ddg(
    query: str,
    num_results: int = 3,
    lang: str = "en",
    do_summarize: bool = True,
) -> str:
    try:

        results = search_ddg(query=query, num_results=num_results, lang=lang)

        # Are there any results?
        if len(results) == 0:
            return "No results."

        text = f"The following results were found for the web search query: '{query}'"

        for result in results:
            text += f"Title: {result['title']}\n Description: {result['body']}\n URL: {result['href']}\n\n "

        if do_summarize:
            # summary prompt:
            text += "Please summarise these results and list facts and information that help answer the query:"
            text = summarize(text)

        return text

    except Exception as e:
        traceback.format_exc()
        return f"Web search failed for: '{query}'"

        install_latest_ddg


def search_ddg(
    query: str, num_results: int = 3, lang: str = "en", safe_search: str = "moderate"
) -> str:
    lang = "en-us" if lang == "en" else lang

    results = DDGS().text(
        query=query, region=lang, safesearch=safe_search, max_results=num_results
    )

    if results:
        results = list(results)
    else:
        results = []

    return results


def search_images_ddg(
    query: str, num_results: int = 3, lang: str = "en", safesearch: str = "moderate"
) -> list[dict[str, Optional[str]]]:
    lang = "en-us" if lang == "en" else lang

    results = DDGS().images(
        query=query,
        region=lang,
        safesearch=safesearch,
        size=None,
        color=None,
        type_image=None,
        layout=None,
        license_image=None,
        max_results=num_results,
    )

    results = list(results)

    return results


def install_latest_ddg():
    # Make sure we have the latest version installed:
    try:
        with asection("Installing the latest version of duckduckgo_search:"):
            aprint(pip_install_single_package("duckduckgo_search", upgrade=True))
    except Exception as e:
        traceback.print_exc()
