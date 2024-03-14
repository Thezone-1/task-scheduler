# tasky
 tasky is a task scheduler that allows users to schedule tasks to be executed at a specified time. It interacts with mysql database to store task information and provides functionality to create, read, update, and delete tasks. It also handles concurrent access to the database.

### Specification
tasky creates tasks, stores them in the mysql database and executes them as at execution time provided.

- Each task takes name, execution time, recurrance and task definition.

- The scheduler can execute the tasks written under task definition at the execution time.

- The docker file is also written to make an image.

- A helm chart is prepared which can take task informations from the cli and store it in the database performing CRUD operations.

### Getting Started

First setup the environment via activating it and then install the dependencies
```
pip install fastapi uvicorn sqlalchemy pymysql
```

Connect the database by creating a database v.i.z task_scheduler then the database user and password has to be added in the DATABASE_URL in the database/database_config.py file. Now from the terminal use the task_scheduler database.

For running the task scheduler run
 ```
python ./main.py
```

To use the task scheduler a basic html form is created which can be accessed from http://localhost:8000/static/index.html
and stores the data and executes the tasks via the fastapi Endpoints.

### Functionality

The Task Scheduler has two threads which run as new tasks arrive and then executes them by initiating processes when the execution time is hit. This whole thing is stored and accessed from a mysql database named task_scheduler.

### Containerization

to run the docker container run
```
docker build -t task-scheduler .
docker run -d --name task-scheduler-container -p 8000:8000 task-scheduler
```

Additionally the kubernates pod can be set using the command
```
kubectl apply -f create_task_job.yaml

```

Once the docker image is created the helm chart can be created using the following command :
```
helm install task-scheduler ./task-scheduler --namespace your-namespace --set image.repository=your-docker-repo/task-scheduler --set image.tag=latest
--create-namespace
```

Here it is important to note that the docker repo name and the namespace has to be given properly.

Now for running the CRUD operation the following commands can be used for example
```
curl -X POST http://<service_ip>:<service_port>/tasks/ -d '{"name": "New Task", "execution_time": "2025-03-01T12:00:00"}' -H 'Content-Type: application/json'
```
