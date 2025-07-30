test:
	poetry run pytest -v tests/test_download.py -s
build:
	maturin develop
	poetry run pytest -v tests/test_download.py -s

publish:
	MATURIN_PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJDA1MDJhN2FmLTBhODQtNDcwMi1iMzlhLTkwNTFjNTQ5YjY0MwACFVsxLFsiYmFhaS1kYXRhY3ViZSJdXQACLFsyLFsiOGI3MmQxNzEtZGJkMy00NThmLWEzY2QtNmQ5NTVmNzU0ZTFhIl1dAAAGIL1vjl1L9VgsZ_YdT1CB9SNdRiQmZDHkuxmVLbC8Xzux" maturin publish