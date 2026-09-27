.PHONY: all arxiv

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex

arxiv: all
	python3 prepare_arxiv.py
