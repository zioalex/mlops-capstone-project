- [Info](#info)
- [What you will find inside.](#what-you-will-find-inside)
- [The Context - The war, Russia, Ukrain and the economic world.](#the-context---the-war-russia-ukrain-and-the-economic-world)
- [Software requirements](#software-requirements)
- [The Implementation](#the-implementation)
  - [Prepare the environment](#prepare-the-environment)
  - [Prediction Service](#prediction-service)
  - [Monitoring](#monitoring)
- [What you can expect](#what-you-can-expect)
- [References](#references)

# Info
This is the capstone project of the [MLOps course](https://github.com/DataTalksClub/mlops-zoomcamp), started on the 16 of May.
As final step in the course, a project following al the main part of the course, needs to be implemented.
Here you can find my project.

# What you will find inside.
- Experiment tracking and model management (mlflow)
- Orchestration and ML Pipelines (prefect)
- Model Deployment (batch deployment)
- Model Monitoring (prefect monitoring)
- Best practices (unit and integration tests, linting, formatting, pre-commit hooks, makefiles)

# The Context - The war, Russia, Ukrain and the economic world.
For this project I chose a Russian trade dataset. 

Who will be the major contributor in Russia economic in the next years?
And indirectly who could influence the war and Russia behaviour in the next years through economic actions?

The ML model is pretty simple as of today.
The basic features are:

    categorical = ['Partner ISO', 'Commodity Code']
    numerical = ['Year']

while the target is `Trade Value (US$)`

So the goal is to forecast who will have the heavier economic influence in Russia.

# Software requirements
- Anaconda
- Python
- pre-commit
- docker
- docker-compose

# The Implementation
The initial data analysis has been done on Kaggle and can be seen here: https://www.kaggle.com/code/zioalex/russia-world-export-eda.
## Prepare the environment
To facilitate the development process I created a Makefile with all the software requirements codified.

To start activate the default conda environment:
    
    conda activate base

and enable the Pipenv provided with:

    pipenv shell
    pipenv sync

Now you can start Jupyter notebook and follow the development process in the notebook. I personally use VSCode with the Jupyter extension (ms-toolsai.jupyter).

At this point you can start all the software components with:

    make all

It will start mlflow and prefect and make everything ready to work with the Jupyter notebook [ml_training_fit.ipynb](07-project/ml_training_fit.ipynb) and follow up with development process.

Mlflow can be accessed at http://127.0.0.1:5000 .
While prefect at http://127.0.0.1:4200/ .

## Prediction Service
The model has been dockerized and it is ready for deployment in the cloud. The code is available in [./monitoring/predicition_service](./monitoring/predicition_service).

The service is up&running and you can test it with:

    make test_prediction
    {
      "data": {
        "Commodity Code": 68,
        "Partner ISO": "ZWE",
        "model_version": "2",
        "status": 200,
        "trade_value": 1854.0041121851355
      },
      "statusCode": 200
    }

## Monitoring
To test the monitoring you can send data to mongoDB with the script send_data.py

    make send_data

And the create a prefect report with:

    make prefect_monitoring

# What you can expect
Follow some screenshots of the project:
![EDA](img/Screenshot%20from%202022-09-02%2001-17-35.png)
![Dataframe](img/Screenshot%20from%202022-09-02%2001-17-49.png)
![Parter and Parter ISO](img/Screenshot%20from%202022-09-02%2001-35-00.png)
![Commodity and Commodity code](img/Screenshot%20from%202022-09-02%2001-35-16.png)
![Top Importers of Russian goods](img/Screenshot%20from%202022-09-02%2001-39-36.png)
![Top 10 importing Organic, In-Organic, & Pharmaceutical](img/Screenshot%20from%202022-09-02%2001-39-51.png)
![Prefect report](./img/Screenshot%20from%202022-09-01%2023-00-01.png)



[Here you can find the complete report on the model.](
./monitoring/prefect-monitoring/trade_value_drift_report_2022-08-28-13-56.html)

# References
[Course homepage](https://github.com/DataTalksClub/mlops-zoomcamp)
https://pipenv.pypa.io/en/latest/basics/
https://pipenv.pypa.io/en/latest/advanced/
https://machinelearningmastery.com/hyperopt-for-automated-machine-learning-with-scikit-learn/
https://neptune.ai/blog/ml-experiment-tracking
https://mlflow.org/docs/latest/tracking.html#automatic-logging
https://github.com/mlflow/mlflow/blob/master/mlflow/store/db_migrations/README.md

[My course notes](https://github.com/zioalex/mlops-zoomcamp)