# `ss.py`: a cli wrapper for SemanticScholar.com

I wrote a cli to streamline my research workflow. It allows me to
search, download, and inspect papers and more through the semantic
scholar API. `ss.py` plays nicely with tools like `jq`, `jtbl`, and
`fold`. I'll show some common uses here:

```sh
$ git clone https://github.com/mattf1n/ss.git # Clone the repo
$ ln ss/ss.py .local/bin/ss                   # copy the script to a location on my PATH.
$ chmod +x .local/bin/ss                      # make it executable.
$ ss --help
usage: ss [-h] {search,dl,citations,paper,id,author} ...

positional arguments:
  {search,dl,citations,paper,id,author}

optional arguments:
  -h, --help            show this help message and exit
$ ss search "Matthew Finlayson" | jtbl        # search my papers and display them in a table
╒══════╤═════════════════════════╤════════╤═════════════════════════╕
│ id   │ title                   │   year │ authors                 │
╞══════╪═════════════════════════╪════════╪═════════════════════════╡
│ 75be │ Donald Trump and vaccin │   2020 │ M. Hornsey (5048), M. F │
│      │ ation: The effect of po │        │ inlayson (1529), Gabrie │
│      │ litical identity, consp │        │ lle Chatwood (1581), C. │
│      │ iracist ideation and pr │        │  Begeny (4302)          │
│      │ esidential tweets on va │        │                         │
│      │ ccine hesitancy         │        │                         │
├──────┼─────────────────────────┼────────┼─────────────────────────┤
│ 488d │ Causal Analysis of Synt │   2021 │ Matthew Finlayson (1580 │
│      │ actic Agreement Mechani │        │ ), Aaron Mueller (4935) │
│      │ sms in Neural Language  │        │ , S. Shieber (1692), Se │
│      │ Models                  │        │ bastian Gehrmann (3159) │
│      │                         │        │ , Tal Linzen (2467), Yo │
│      │                         │        │ natan Belinkov (2083)   │
╘══════╧═════════════════════════╧════════╧═════════════════════════╛
```

List my papers using the `authorId` 1580 found above.
`"Matthew Finlayson"` would work as well after this search.

```sh
$ ss author 1580 | jtbl 
╒══════╤═════════════════════════╤════════╤═════════════════════════╕
│ id   │ title                   │   year │ authors                 │
╞══════╪═════════════════════════╪════════╪═════════════════════════╡
│ cb16 │ What Makes Instruction  │   2022 │ Matthew Finlayson (1580 │
│      │ Learning Hard? An Inves │        │ ), Kyle Richardson (466 │
│      │ tigation and a New Chal │        │ 6), Ashish Sabharwal (4 │
│      │ lenge in a Synthetic En │        │ 822), Peter Clark (4832 │
│      │ vironment               │        │ )                       │
├──────┼─────────────────────────┼────────┼─────────────────────────┤
│ 488d │ Causal Analysis of Synt │   2021 │ Matthew Finlayson (1580 │
│      │ actic Agreement Mechani │        │ ), Aaron Mueller (4935) │
│      │ sms in Neural Language  │        │ , S. Shieber (1692), Se │
│      │ Models                  │        │ bastian Gehrmann (3159) │
│      │                         │        │ , Tal Linzen (2467), Yo │
│      │                         │        │ natan Belinkov (2083)   │
╘══════╧═════════════════════════╧════════╧═════════════════════════╛
```

You can look at citations and traverse the citation graph.

```sh
$ ss citations cb16 | jtbl
╒══════╤═════════════════════════╤════════╤═════════════════════════╕
│ id   │ title                   │   year │ authors                 │
╞══════╪═════════════════════════╪════════╪═════════════════════════╡
│ e46f │ Simplicity Bias in Tran │   2022 │ S. Bhattamishra (9295), │
│      │ sformers and their Abil │        │  Arkil Patel (1443), Va │
│      │ ity to Learn Sparse Boo │        │ run Kanade (2080), P. B │
│      │ lean Functions          │        │ lunsom (1685)           │
├──────┼─────────────────────────┼────────┼─────────────────────────┤
│ 82cd │ Learning Instructions w │   2022 │ Yuxian Gu (2116), Pei K │
│      │ ith Unlabeled Data for  │        │ e (1886), Xiaoyan Zhu ( │
│      │ Zero-Shot Cross-Task Ge │        │ 1452), Minlie Huang (17 │
│      │ neralization            │        │ 30)                     │
╘══════╧═════════════════════════╧════════╧═════════════════════════╛
```

You can get paper info by ID as well and extract things like bibtex and
abstracts with `jq`.

```sh
$ ss paper cb16 | jq -r '.citationStyles.bibtex, .abstract' | fold -s 
@['JournalArticle', 'Conference']{Finlayson2022WhatMI,
 author = {Matthew Finlayson and Kyle Richardson and Ashish Sabharwal and Peter 
Clark},
 booktitle = {Conference on Empirical Methods in Natural Language Processing},
 pages = {414-426},
 title = {What Makes Instruction Learning Hard? An Investigation and a New 
Challenge in a Synthetic Environment},
 year = {2022}
}

The instruction learning paradigm—where a model learns to perform new tasks 
from task descriptions alone—has become popular in research on general-purpose 
models. The capabilities of large transformer models as instruction learners, 
however, remain poorly understood. We use a controlled synthetic environment to 
...
```

Downloading is easy as well!

```sh
$ ss dl cb16
/Users/matthewf/papers/Finlayson2022WhatMI.pdf
Already downloaded.
```
