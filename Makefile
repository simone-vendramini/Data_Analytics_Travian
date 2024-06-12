VENV := .venv/bin/activate

enter-env :
	. $(VENV) 

install-dipendences : enter-env
	pip install -r requirements.txt

create-communities : enter-env
	python ./scripts/create_communities.py

run-dash : enter-env
	python ./scripts/dashboard.py