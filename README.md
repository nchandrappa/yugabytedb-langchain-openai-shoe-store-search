# Shoe Store Search Tool with LangChain, OpenAI and YugabyteDB

This is a sample application written in Python that demonstrates how use LangChain to build applications with LLM integration. By using the [SQL](https://python.langchain.com/docs/use_cases/qa_structured/sql) chain capabilities of LangChain in conjunction with an [OpenAI](https://openai.com/) LLM, the application can query a [PostgreSQL-compatible](https://www.yugabyte.com/postgresql/postgresql-compatibility/) YugabyteDB database from natural language.

# Prerequisites

* Install Python3
* Install Docker

## Set up the application

Download the application and provide settings specific to your deployment:

1. Clone the repository.

    ```sh
    git clone https://github.com/YugabyteDB-Samples/yugabytedb-langchain-openai-shoe-store-search.git
    ```

2. Install the application dependencies.

    Dependencies can be installed in a virtual environment, or globally on your machine.

    * Option 1 (recommended): Install Dependencies from *requirements.txt* in virtual environment

        ```sh
        python3 -m venv yb-langchain-env
        source yb-langchain-env/bin/activate
        pip install -r requirements.txt
        # NOTE: Users with M1 Mac machines should use requirements-m1.txt instead:
        # pip install -r requirements-m1.txt
        ```

    * Option 2: Install Dependencies Globally

        ```sh
        pip install langchain
        pip install psycopg2-binary
        pip install langchain_openai
        pip install langchain_experimental
        pip install flask
        pip install python-dotenv
        ```

3. Create an [OpenAI API Key](https://platform.openai.com/api-keys) and store it's value in a secure location. This will be used to connect the application to the LLM to generate SQL queries and an appropriate response from the database.

4. Configure the application environment variables in `{project_directory/.env}`.

# Get Started with YugabyteDB

YugabyteDB is a [PostgreSQL-compatible](https://www.yugabyte.com/postgresql/postgresql-compatibility/) distributed database.  

Start a 3-node YugabyteDB cluster in Docker (or feel free to use another deployment option):

```sh
# NOTE: if the ~/yb_docker_data already exists on your machine, delete and re-create it
mkdir ~/yb_docker_data

docker network create yb-network

docker run -d --name ybnode1 --hostname ybnode1 --net yb-network \
    -p 15433:15433 -p 7001:7000 -p 9001:9000 -p 5433:5433 \
    -v ~/yb_docker_data/node1:/home/yugabyte/yb_data --restart unless-stopped \
    yugabytedb/yugabyte:2.25.2.0-b359 \
    bin/yugabyted start \
    --base_dir=/home/yugabyte/yb_data --background=false

docker run -d --name ybnode2 --hostname ybnode2 --net yb-network \
    -v ~/yb_docker_data/node2:/home/yugabyte/yb_data --restart unless-stopped \
    yugabytedb/yugabyte:2.25.2.0-b359 \
    bin/yugabyted start --join=ybnode1 \
    --base_dir=/home/yugabyte/yb_data --background=false

docker run -d --name ybnode3 --hostname ybnode3 --net yb-network \
    -v ~/yb_docker_data/node3:/home/yugabyte/yb_data --restart unless-stopped \
    yugabytedb/yugabyte:2.25.2.0-b359 \
    bin/yugabyted start --join=ybnode1 \
    --base_dir=/home/yugabyte/yb_data --background=false
```

The database connectivity settings are provided in the `{project_dir}/.env` file and do not need to be changed if you started the cluster with the preceding command.

Navigate to the YugabyteDB UI to confirm that the database is up and running, at <http://127.0.0.1:15433>.

# Load the E-Commerce Schema and Seed Data

This application requires an e-commerce database with a product catalog and inventory information. This schema includes `products`, `users`, `purchases` and `product_inventory`. It also creates a read-only user role to prevent any destructive actions while querying the database directly from LangChain.

The `pg_trgm` PostgreSQL extension is installed to execute similarity searches on alphanumeric text.

1. Copy the schema to the first node's Docker container.

    ```sh
    docker cp sql/schema.sql ybnode1:/home
    ```

2. Copy the seed data file to the Docker container.

    ```sh
    docker cp sql/generated_data.sql ybnode1:/home
    ```

3. Execute the SQL files against the database.

    ```sh
     docker exec -it ybnode1 bin/ysqlsh -h ybnode1 -c '\i /home/schema.sql'
     docker exec -it ybnode1 bin/ysqlsh -h ybnode1 -c '\i /home/generated_data.sql'
    ```

# Start the Command Line Chatbot

The application starts a Command Line Chatbot which returns results from the connected database.

1. Start the python app.

```sh
python app.py
```

```output
What is your question?
```

2. Provide a relevant question. For instance:

```sh

# What purchases have been made by user1?

# What colors do the Intelligent Racer come in?

# How many narrow shoes come in pink?

# Find me shoes that are in stock and available in size 15.

What is your question? 

Find me shoes that are in stock and available in size 15.
```

```output
[
  {
    "color": [
      "yellow",
      "blue"
    ],
    "description": null,
    "name": "Efficient Jogger 1",
    "price": "110.08",
    "quantity": 22,
    "width": [
      "narrow",
      "wide"
    ]
  },
  {
    "color": [
      "blue",
      "yellow"
    ],
    "description": null,
    "name": "Efficient Jogger 8",
    "price": "143.63",
    "quantity": 85,
    "width": [
      "wide",
      "narrow"
    ]
  },
  ...
]
```
