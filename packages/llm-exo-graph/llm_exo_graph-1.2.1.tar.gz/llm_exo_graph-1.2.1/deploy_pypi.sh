source ./.venv/bin/activate
rm -rf dist/ build/
python -m build
twine upload dist/*
