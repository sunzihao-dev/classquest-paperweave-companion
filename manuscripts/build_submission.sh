#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p ../build ../output/pdf
for paper in classquest_submission paperweave_submission; do
  pdflatex -interaction=nonstopmode -halt-on-error "$paper.tex" > "../build/$paper.log"
  bibtex "$paper" >> "../build/$paper.log"
  pdflatex -interaction=nonstopmode -halt-on-error "$paper.tex" >> "../build/$paper.log"
  pdflatex -interaction=nonstopmode -halt-on-error "$paper.tex" >> "../build/$paper.log"
  cp "$paper.pdf" ../output/pdf/
done
