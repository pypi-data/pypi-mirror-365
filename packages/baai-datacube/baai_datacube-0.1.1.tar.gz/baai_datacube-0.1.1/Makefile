test:
	poetry run pytest -v tests/test_download.py -s
build:
	maturin develop
	poetry run pytest -v tests/test_download.py -s

publish:
	MATURIN_PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcCJGNiNDIwMGM4LTIzOGYtNGY4Mi05ZWIxLTdlN2JmMjMyNDY4ZgACFVsxLFsiYmFhaS1kYXRhY3ViZSJdXQACLFsyLFsiOGI3MmQxNzEtZGJkMy00NThmLWEzY2QtNmQ5NTVmNzU0ZTFhIl1dAAAGIMnznOaxzt3uV6BjMUpbq0b4r0B3ttYe-IPyRqFHU6jX" maturin publish