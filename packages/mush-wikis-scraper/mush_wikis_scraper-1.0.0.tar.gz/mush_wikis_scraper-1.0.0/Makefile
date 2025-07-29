all: setup-git-hooks install check test 

check: check-format check-lint check-types

check-format:
	uv run ruff format . --diff

check-lint:
	uv run ruff check .

check-types:
	uv run mypy .

install:
	uv lock --locked
	uv sync --locked --group dev --group lint --group test

lint:
	uv run ruff format .
	uv run ruff check . --fix

scrap:
	uv run mush-wikis-scrap --format text > text_data.json
	uv run mush-wikis-scrap --format markdown > markdown_data.json
	uv run mush-wikis-scrap --format html > html_data.json
	uv run mush-wikis-scrap --format trafilatura-markdown > trafilatura_markdown_data.json
	uv run mush-wikis-scrap --format trafilatura-html > trafilatura_html_data.json
	uv run mush-wikis-scrap --format trafilatura-text > trafilatura_text_data.json

semantic-release:
	uv run semantic-release version --no-changelog --no-push --no-vcs-release --skip-build --no-commit --no-tag
	uv lock
	git add pyproject.toml uv.lock
	git commit --allow-empty --amend --no-edit 

setup-git-hooks:
	chmod +x hooks/pre-commit
	chmod +x hooks/pre-push
	chmod +x hooks/post-commit
	git config core.hooksPath hooks

test:
	uv run pytest -vv --cov=mush_wikis_scraper --cov-report=xml

.PHONY: all check check-format check-lint check-types install lint semantic-release setup-git-hooks test