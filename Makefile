PROFILES ?= .github/dbt-profiles
DBT = dbt --profiles-dir $(PROFILES)

.PHONY: setup seed build test lint docs demo clean

setup:            ## install Python deps and dbt packages
	pip install -r requirements.txt
	$(DBT) deps

seed:             ## regenerate and load the synthetic raw data (DuckDB)
	python scripts/generate_seed_data.py
	$(DBT) seed

build:            ## load seeds, then build + test every model on the DuckDB demo target
	$(DBT) seed --target demo
	$(DBT) build --target demo --exclude resource_type:seed

test:             ## run only the tests (after `make build`)
	$(DBT) test --target demo

lint:             ## sqlfluff + yamllint
	sqlfluff lint models tests
	yamllint .

docs:             ## generate and serve dbt docs
	$(DBT) docs generate --target demo
	$(DBT) docs serve --target demo

demo: build       ## build, then open the Streamlit dashboard
	pip install -r demo/requirements.txt
	streamlit run demo/app.py

clean:
	rm -rf target dbt_packages logs
