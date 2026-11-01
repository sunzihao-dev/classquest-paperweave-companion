# Reproducing the companion

Use Python 3.9 or newer for the offline audit. The PDF-source check additionally needs Python 3.10+ and `pypdf==6.10.0`. A CPU is sufficient; no GPU, model key or student data are needed.

## 1. Offline numerical and structural checks

From the repository root:

```sh
python3 scripts/reproduce.py
```

The command works in a temporary copy, preserving the published records. It recomputes questionnaire summaries from frequency counts; reruns the 5,456-composition audit and companion example; checks the frozen module hashes; reruns the nine-edge census; and checks card coverage, identifiers, judgments and claim-bank hash. It writes a report to `build/reproduction_report.json`. Runtime strings can differ; numerical results must match.

## 2. Full source-PDF traceability and teaching-pack regeneration

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/fetch_sources.py
python scripts/reproduce.py --with-sources
```

`fetch_sources.py` obtains only the five explicitly listed academic PDFs, checks their SHA-256 hashes and writes them under ignored `literature/`. Third-party PDFs are not part of this repository. If a provider blocks access or changes the bytes, the script fails rather than silently changing the source snapshot. You may manually obtain the named version and place it at `literature/{dpr,bart,t5,rag,fid}.pdf`; the hash must match the manifest.

The full check regenerates all six teaching files in a temporary directory and compares them byte-for-byte. It also verifies 15 short anchors at the declared PDF pages. Successful execution does not validate the meaning of the source interpretation or demonstrate student learning. Reading the surrounding passages remains necessary.

## 3. Build the papers

Install a LaTeX distribution with ACM dependencies, `pdflatex` and `bibtex` on PATH, then run:

```sh
sh manuscripts/build_submission.sh
```

The exact `acmart` 1.75 class and bibliography style used for the supplied snapshots are bundled with their original notices. The original build used TeX Live 2021. Other font/package versions can alter layout or PDF metadata, so byte-identical PDFs are not promised. Expected snapshots are ClassQuest 7 pages / 25 references and PaperWeave 8 pages / 29 references. Inspect the rendered output after changing the manuscript or toolchain.

## 4. Use the teaching materials

Open `teaching_materials/paperweave/teacher_guide.html` locally. Print `student_workbook.html` separately; it omits the answer key. The guide proposes an eight-card core with ten extension cards. This is a proposed adoption sequence, not a reconstruction of the earlier classroom study. Teachers should check the source judgments before using them for assessment.
