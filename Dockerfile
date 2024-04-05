# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.8-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice

RUN apt-get update

# PYODBC DEPENDENCES
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt install unixodbc -y
RUN apt-get clean -y
ADD odbcinst.ini /etc/odbcinst.ini

# UPGRADE pip3
RUN pip3 install --upgrade pip

# DEPENDECES FOR DOWNLOAD ODBC DRIVER
RUN apt-get install apt-transport-https 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update

# INSTALL ODBC DRIVER
RUN ACCEPT_EULA=Y apt-get install msodbcsql18 --assume-yes

# CONFIGURE ENV FOR /bin/bash TO USE MSODBCSQL17
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile 
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc 

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=<ACCOUNTNAME>;AccountKey=<ACCOUNTKEY>;EndpointSuffix=core.windows.net \
    AzureSQLConnectionString='Driver={ODBC Driver 18 for SQL Server};Server=tcp:<STORAGEACCOUNT>.database.windows.net,1433;Database=<DBNAME>;Uid=<USERID>;Pwd=<PASSWORD>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;' \
    SnowflakeConnectionString='{"account":"<ACCOUNT>","user":"<USER>","password":"<PASSWORD>","role":"ACCOUNTADMIN","warehouse":"COMPUTE_WH","database":"SNOWFLAKE_SAMPLE_DATA","session_parameters":{"QUERY_TAG": "TAG01","MULTI_STATEMENT_COUNT": 0}}'

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot