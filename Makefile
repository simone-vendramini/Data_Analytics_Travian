install-dipendences :
	pip install -r requirements.txt

create-communities :
	python ./scripts/create_communities.py
dashboard :
	python ./scripts/dashboard.py