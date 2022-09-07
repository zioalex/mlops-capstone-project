.PHONY: localstack
MLFLOW := $(shell pgrep mlflow)
PREFECT := $(shell pgrep prefect)

all: start_prefect_server start_service
	echo "Start everything"

prepare_setup:
	@-mkdir data models models_pickle
	pipenv sync
	if [ -z ${VIRTUAL_ENV} ]; then  echo "start the pipenv environment with **pipenv shell** before using the make file"; fi

## Experiment tracking and Orchestration
start_mlflow: prepare_setup
	if [ "$(MLFLOW)" = "" ]; then \
		 echo "Start mlflow"; \
		 (cd ~/github/mlops-zoomcamp/07-project; mlflow ui --backend-store-uri sqlite:///mlflow.db --serve-artifacts --artifacts-destination ./artifacts &); \
	else \
	 	echo "mlflow process ${MLFLOW} already running"; \
	fi

start_prefect_server: start_mlflow
	if [ "$(PREFECT)" = "" ]; then \
		echo "Start mlflow"; \
		(cd ~/github/mlops-zoomcamp/07-project; prefect config set PREFECT_ORION_UI_API_URL="http://localhost:4200/api"; prefect orion start --host 0.0.0.0 &); \
	else \
	 	echo "prefect process $(PREFECT) already running"; \
	fi

prefect_client_side: start_prefect_server
	(cd ~/github/mlops-zoomcamp/07-project; prefect config set PREFECT_API_URL="http://localhost:4200/api"; prefect config view)

prefect_storage: prefect_client_side
	echo "Select local storage with path ./prefect and set it as default"
	prefect storage create
	prefect storage ls

stop_prefect:
	echo "Stop prefect"
	@-pkill -f prefect

stop_mlflow:
	echo "Stop Mlflow"
	@-pkill -f mlflow

stop_all: stop_prefect stop_mlflow

### Cleanup

cleanup_mlflow_db: stop_mlflow
	rm -Rf ./mlflow.db

cleanup_prefect_db: stop_prefect
	# prefect orion database reset
	rm -Rf .prefect/

## Model deployment
prefect_flow: prefect_client_sidec
	python prefect_flow.py

prefect_deployment:
	prefect deployment create prefect_deploy.py

## Docker service and monitoring
start_service: # It starts the docker service and mongodb
	(cd monitoring/; docker-compose -f docker-compose.yml up --build)

test_prediction:
	(cd monitoring/prediction_service; curl -X  POST -H "Content-Type: application/json" --data @data.json http://localhost:9696/predict-trade | jq)

drop_alembic_table:
	# When you got:
	# alembic.util.exc.CommandError: Can't locate revision identified by '061c7e518b40'
	# sqlite> SELECT * FROM alembic_version;
	# bd07f7e963c5                                                                        
	sqlite3 ~/.prefect/orion.db "DROP  TABLE alembic_version ;"
	# or sqlite3 ~/.prefect/orion.db "UPDATE alembic_version SET version_num = 'bd07f7e963c5' WHERE version_num = '061c7e518b40';"
	# or rm -Rf ~/.prefect/orion.db

send_data: # send data to predcton service and save to MongoDB
	(cd monirotng/prefect_monitoring; python send_data.py)

prefect_monitoring:
	(cd monirotng/prefect_monitoring; python prefect_monitoring_project.py)

## IaC, unittest and integration test
localstack: localstack/docker-compose.yaml
	@echo "Starting localstack"
	docker-compose -f localstack/docker-compose.yaml up -d

test_localstack_s3: localstack
	aws --endpoint-url=http://localhost:4566 s3 mb s3://russian-trade
	aws s3 ls --endpoint-url=http://localhost:4566

copy_data_to_s3: localstack test_localstack_s3
	export S3_ENDPOINT_URL="http://localhost:4566"
	aws s3 cp --endpoint-url=http://localhost:4566 data/RUStoWorldTrade_2007.pkl s3://russian-trade/
	aws s3 cp --endpoint-url=http://localhost:4566 data/RUStoWorldTrade_2008.pkl s3://russian-trade/
	aws s3 cp --endpoint-url=http://localhost:4566 data/iso3.csv s3://russian-trade/
	aws s3 ls --endpoint-url=http://localhost:4566 s3://russian-trade/

test: test_localstack_s3
	export S3_ENDPOINT_URL="http://localhost:4566"
	export INPUT_FILE_PATTERN=S3://russian-trade/
	( export S3_ENDPOINT_URL="http://localhost:4566"; pytest tests/ )

prepare_lamda_function:
	#cd mylambda
	pip install --target ./packages -r requirements.txt --no-deps
	(cd packages; zip -r ../my-lambda-package.zip .)
	zip -g my-lambda-package.zip batch.py
	#pipenv lock -r | sed 's/-e //g' | pipenv run pip install --upgrade -r /dev/stdin --target python/lib/python3.9/#site-packages/
	#zip -r my-lambda-package.zip python batch.py
	rm -rf packages

	#docker save stg_stream_model_duration_mlops-zoomcamp | zip > stg_stream_model_duration_mlops-zoomcamp.zip
	#aws s3 --endpoint-url=http://localhost:4566 cp stg_stream_model_duration_mlops-zoomcamp.zip s3://stg-mlflow-models-mlops-zoomcamp/
	# s3://stg-mlflow-models-mlops-zoomcamp/stg_stream_model_duration_mlops-zoomcamp.zip

full_stack: prepare_lamda_function
	(cd InfrastructureAsCode; terraform init; terraform plan -var-file=./vars/stg.tfvars; terraform apply -var-file=./vars/stg.tfvars --auto-approve)

