#!/usr/bin/env python

import argparse, requests, os, json, re, sys, operator

IDS = os.path.expanduser("~/.ss/ids.json")
URL = "http://api.semanticscholar.org/graph/v1/"
FIELDS = "title,year,authors,abstract,citationStyles,paperId,openAccessPdf"
API_KEY = os.environ.get("S2_API_KEY")


def main():
    args = parse_args()
    args.func(**vars(args))


def parse_args():
    alias_help = "Paper or author ID or alias"
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=hello)
    subparsers = parser.add_subparsers()

    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument("query", help="Search term")
    search_parser.set_defaults(func=search)

    dl_parser = subparsers.add_parser("dl", help="Download a paper")
    dl_parser.add_argument("alias", help=alias_help)
    dl_parser.add_argument(
        "--url", action="store_true", help="Print paper url to stdout"
    )
    dl_parser.set_defaults(func=dl)

    citations_parser = subparsers.add_parser(
        "citations", help="Get the articles that cite a paper"
    )
    citations_parser.add_argument("alias", help=alias_help)
    citations_parser.set_defaults(func=citations)

    paper_parser = subparsers.add_parser("paper", help="Get info on a paper")
    paper_parser.add_argument("alias", help=alias_help)
    paper_parser.add_argument(
        "--fields", type=str, default=FIELDS, help="Which fields to get from the API"
    )
    paper_parser.set_defaults(func=paper)

    identifier_parser = subparsers.add_parser("id", help="Get a paper identifier")
    identifier_parser.add_argument("alias", help=alias_help)
    identifier_parser.set_defaults(func=identifier)

    author_parser = subparsers.add_parser("author", help="Get an author's papers")
    author_parser.add_argument("alias", help=alias_help)
    author_parser.add_argument(
        "--fields",
        type=str,
        default="papers.year,papers.title,papers.authors",
        help="Which fields to retrieve",
    )
    author_parser.set_defaults(func=author)

    return parser.parse_args()


def hello(**kwargs):
    print("ss: a Semantic Scholar CLI by Matt Fin")


def paper(alias=None, fields=None, **_):
    paper_id = get_id(alias)
    response = requests.get(
        os.path.join(URL, "paper", paper_id),
        params=dict(fields=fields),
        headers={"X-API-KEY": API_KEY},
    )
    sys.stdout.write(response.text)


def search(query=None, **_):
    response = requests.get(
        os.path.join(URL, "paper/search"),
        params=dict(query=query, fields=FIELDS),
        headers={"X-API-KEY": API_KEY},
    )
    if response.ok and "data" in response.json():
        papers = response.json()["data"]
        save_alias(get_aliases(papers))
        json.dump(list(map(flatten_paper, papers)), sys.stdout)
    else:
        print(response.text, file=sys.stderr)


def author(alias=None, fields=None, **_):
    author_id = get_id(alias)
    response = requests.get(
        os.path.join(URL, "author", author_id),
        params=dict(fields=fields),
        headers={"X-API-KEY": API_KEY},
    )
    papers = response.json()["papers"]
    save_alias(get_aliases(papers))
    json.dump(list(map(flatten_paper, papers)), sys.stdout)


def citations(alias=None, **_):
    paper_id = get_id(alias)
    response = requests.get(
        os.path.join(URL, "paper", paper_id, "citations"),
        params=dict(fields=FIELDS),
        headers={"X-API-KEY": API_KEY},
    )
    papers = [item["citingPaper"] for item in response.json()["data"]]
    save_alias(get_aliases(papers))
    json.dump(list(map(flatten_paper, papers)), sys.stdout)


def dl(alias=None, url=False, **_):
    paper_id = get_id(alias)
    response = requests.get(
        os.path.join(URL, "paper", paper_id),
        params=dict(fields="openAccessPdf,externalIds,citationStyles,isOpenAccess"),
        headers={"X-API-KEY": API_KEY},
    ).json()
    bibtex_id = get_bibtex_id(response["citationStyles"]["bibtex"])
    save_alias({bibtex_id: paper_id})
    pdf_path = os.path.expanduser(f"~/papers/{bibtex_id}.pdf")
    if response["isOpenAccess"]:
        paper_url = response["openAccessPdf"]["url"]
    elif "ArXiv" in response["externalIds"]:
        paper_url = f"https://arxiv.org/pdf/{response['externalIds']['ArXiv']}"
    else:
        print("No paper url", file=sys.stderr)
        return
    if url:
        print(paper_url)
    elif os.path.exists(pdf_path):
        print("Already downloaded.", file=sys.stderr)
        print(pdf_path)
    else:
        paper_response = requests.get(paper_url)
        with open(pdf_path, "wb") as f:
            f.write(paper_response.content)
        print(pdf_path)


def identifier(alias=None, **_):
    sys.stdout.write(get_id(alias))


def flatten_paper(paper):
    return {
        "id": paper["paperId"][:4],
        "title": paper["title"],
        "year": paper["year"],
        "authors": authors_string(paper["authors"]),
    }


def authors_string(authors, max_authors=10):
    max_authors = min(max_authors, len(authors))
    truncated_authors = authors[:max_authors]
    aliases = (
        None if a["authorId"] is None else a["authorId"][:4] for a in truncated_authors
    )
    names = (a["name"] for a in truncated_authors)
    items = map("{} ({})".format, names, aliases)
    suffix = ", and {} others".format(len(authors) - max_authors)
    return ", ".join(items) + suffix * (len(authors) > max_authors)


def get_aliases(papers: list[dict]):
    aliases = dict()
    for paper in papers:
        if paper["paperId"] is not None:
            for alias in (paper["paperId"], paper["paperId"][:4]):
                aliases[alias] = paper["paperId"]
        for author in paper["authors"]:
            if author["authorId"] is not None:
                for alias in [
                    *author["name"].split(),
                    author["name"],
                    author["authorId"],
                    author["authorId"][:4],
                ]:
                    aliases[alias] = author["authorId"]
    return aliases


def get_bibtex_id(bibtex: str):
    return re.findall(r"\w+\d+\w+", bibtex)[0]


def save_alias(new_alias):
    with open(IDS, "r") as f:
        aliases = json.load(f)
    with open(IDS, "w") as f:
        json.dump(aliases | new_alias, f)


def get_id(alias):
    with open(IDS) as f:
        return json.load(f)[alias]


if __name__ == "__main__":
    main()
