# py_fnapp_docker_seed_sf_sql
Based on `py_fnapp_docker_seed`, adding drivers for Snowflake, MSSQL, Blob storage.
Using SQL server ODBC driver 18 on Ubuntu 20.04 (WSL).
Using Python Snowflake driver on Ubuntu 20.04 (WSL).

# Prerequisites
- Blob storge with connection string
- MSSQL db with connection string
- MSSQL external data source with blob
- Snowflake db with connection string
- Snowflake external stage with blob
- pip install "snowflake-connector-python[pandas]"

# Development environment
Platform: WSL Ubuntu on windows  
IDE: Visual Studio Code in Windows  
    - Install WSL plugin  
    - Click bottom left icon >< WSL:Ubuntu-20.04  
    - New WSL window  
    - Select remote Ubuntu folder  
    - Start development  
Core tools
    - Install Core tools in Ubuntu
    - func --version 4.0.5530

# Development from scratch
    - `cd` Project folder
    - `virtualenv .venv`
    - `func init --worker-runtime python --model V2 --docker`
    - `func new --template "Http Trigger" --name MyHttpTrigger`
    - `func templates list`
    - `func new --template "Azure Blob Storage trigger" --name MyBlobTrigger`
        <mark>this gives error `Object reference not set to an instance of an object.`, therefore handcraft the function to handle blob</mark>

# Run
    In local (Ubuntu)
    - update `local.settings.json`, set `AzureWebJobsStorage` to <CONNECTION STRING>
    - apt install unixodbc (to avoid pyodbc not found error)
        (Use reference #4 to setup odbc on Ubuntu)
    - `func start`

    In Docker
    - update Dockerfile, set ENV AzureWebJobsStorage=<CONNECTION STRING>
    - update Dockerfile, change unixodbc-dev to unixodbc in line `RUN apt install unixodbc -y`
    - `docker build --no-cache -t <ACR NAME>.azurecr.io/<IMAGE NAME>:<TAG> .`
    - `docker run -d -p 8080:80 <ACR NAME>.azurecr.io/<IMAGE NAME>:<TAG>`

# Deploy
    - `docker login <ACR NAME>.azurecr.io -u <USER NAME> -p <PASSWORD>`
    - `docker push <ACR NAME>.azurecr.io/<IMAGE NAME>:<TAG>`
    - Create a Function App in Azure -> Choose `Container Image` option for deployment
    - update variable `AzureWebJobsStorage` in Function app settings
    - Deployment Center
        Source - Container Registry
        Registry source - Azure Container Registry
        Registry - <ACR NAME>
        Image - <IMAGE NAME>
        Tag - <TAG>

# Usage
    In Local/Docker
    http://localhost:8080/api/MyHttpTrigger

    In Azure
    https://<FNAPP URL>.azurewebsites.net/api/MyHttpTrigger

# References
1. [Develop Azure Functions locally using Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python)

2. [create-supporting-azure-resources-for-your-function](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container?tabs=core-tools%2Cacr%2Cazure-cli2%2Cazure-cli&pivots=azure-functions#create-supporting-azure-resources-for-your-function)

3. [programming-language-python#build-the-container-image-and-verify-locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-container-registry?tabs=acr%2Cbash&pivots=programming-language-python#build-the-container-image-and-verify-locally)

4. [installing-the-microsoft-odbc-driver-for-sql-server](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=ubuntu18-install%2Calpine17-install%2Cdebian8-install%2Cubuntu16-13-install%2Crhel7-offline)

