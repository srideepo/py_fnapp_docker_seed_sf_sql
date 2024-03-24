# py_fnapp_docker_seed_sf_sql
Based on `py_fnapp_docker_seed`, adding drivers for Snowflake, MSSQL, Blob storage

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
    - `func init --worker-runtime python --model V2 --docker`
    - `func new --template "Http Trigger" --name MyHttpTrigger`
    - `func templates list`
    - `func new --template "Azure Blob Storage trigger" --name MyBlobTrigger`
        <mark>this gives error `Object reference not set to an instance of an object.`, therefore handcraft the function to handle blob</mark>

# Run
    In local
    - update `local.settings.json`, set `AzureWebJobsStorage` to <CONNECTION STRING>
    - `func start`

    In Docker
    - update Dockerfile, set ENV AzureWebJobsStorage=<CONNECTION STRING>
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
[Develop Azure Functions locally using Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python)

[create-supporting-azure-resources-for-your-function](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container?tabs=core-tools%2Cacr%2Cazure-cli2%2Cazure-cli&pivots=azure-functions#create-supporting-azure-resources-for-your-function)

[programming-language-python#build-the-container-image-and-verify-locally](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-container-registry?tabs=acr%2Cbash&pivots=programming-language-python#build-the-container-image-and-verify-locally)
