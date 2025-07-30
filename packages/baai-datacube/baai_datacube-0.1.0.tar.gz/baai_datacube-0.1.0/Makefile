test:
	poetry run pytest -v tests/test_download.py -s
build:
	maturin develop
	poetry run pytest -v tests/test_download.py -s

publish:
	MATURIN_PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJGQxOTM4Yzg5LWRjOTgtNDhmMS1hMDIyLWY5NTJhNmI0NjVhNQACKlszLCI2NTE0MTRiYy03ZWFkLTRkOTctYjQ5Mi0zOTg4MWFlMTNkZGIiXQAABiAJZlMSIiY1ROdAUysD1I7mLZxuUGPgxY1LiCxBBxFQKQ" maturin publish