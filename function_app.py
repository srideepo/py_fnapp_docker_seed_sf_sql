import azure.functions as func
import datetime
import json
import logging
import snowflake.connector
import pyodbc
from io import BytesIO
import pandas as pd
import os

app = func.FunctionApp()

VERSION_ID = 4
AZSQL_CONN_STR = ("<AZURE CONNECTION STRING>")
SF_CONN_STR = "<SF CONNECTION STRING>"

##// HTTP trigger //###################################################
@app.route(route="DemoHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello (v{VERSION_ID}), {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
##// //###############################################################

##// BLOB input/output //#############################################
@app.function_name(name="DemoBlobOutput")
@app.route(route="inbound", auth_level=func.AuthLevel.ANONYMOUS)
@app.blob_input(arg_name="inputblob",
                path="inbound/Book1.csv",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob",
                path="newblob/test.txt",
                connection="AzureWebJobsStorage")
def main(req: func.HttpRequest, inputblob: str, outputblob: func.Out[str]):
    logging.info(f'Python Queue trigger function processed {len(inputblob)} bytes')
    outputblob.set(inputblob)
    return "ok"
##// //###############################################################


##// BLOB trigger //##################################################
@app.function_name(name="DemoBlobTrigger")
@app.blob_trigger(arg_name="myblob", 
                  path="trigger/{name}.trigger",
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob",
                path="newblob/{rand-guid}.txt",
                connection="AzureWebJobsStorage")
def test_function(myblob: func.InputStream, outputblob: func.Out[bytes]):
    try:
        logging.info(f"Python blob trigger function processed blob \n"
                    f"Name: {myblob.name}\n"
                    f"Blob Size: {myblob.length} bytes")
        _jsonData= json.load(myblob)
        #_mssql_response = _mssql_access(AZSQL_CONN_STR, f"EXECUTE sp_getCommands '{json.dumps(_jsonData)}', '{myblob.name}'")

        #from metadata get commands to execute in target
        _dfCommandsList = _mssql_access_sync(AZSQL_CONN_STR, 'EXECUTE [dbo].[sp_getCommands] ''inbound'';')
        for i, dfCommands in enumerate(_dfCommandsList):
            for j, cmd in enumerate(dfCommands):
                _cmd = cmd['Command']
                if len(_cmd) == 0:
                    raise Exception("Empty command not allowed.")

                logging.info(f"[{i}{j}] Preparing to execute on Target[{cmd['Target']}], Command[{_cmd}]")
                if cmd['Target'] == 'MSSQL':
                    _resultset = _mssql_access_sync(AZSQL_CONN_STR, _cmd)
                elif cmd['Target'] == 'SNOWFLAKE':
                    _resultset = _snowflake_access_async(SF_CONN_STR, _cmd)
                elif cmd['Target'] == 'BLOB':
                    outputblob.set('{"col1":"val1"}')
                else:
                    logging.info(f"WARNING! Unknown Target[{cmd['Target']}] specified in the command. No action performed.")

                logging.info(f"Command execution completed!")
    except Exception as error:
        raise error

##// //###############################################################

##// PRIVATE FUNCTIONS //#############################################

##// SQL access SYNC //###############################################
def _mssql_access_sync(AZSQL_CONN_STR, SQL_SCRIPT):
    try:
        logging.info("MSSQL call starting...")
        conn: pyodbc.Connection = pyodbc.connect(AZSQL_CONN_STR)
        cursor: pyodbc.Cursor = conn.cursor()
        cursor.execute(SQL_SCRIPT)

        _df_list = []
        while True:
            _columns = [column[0] for column in cursor.description]
            _results = []
            for _row in cursor.fetchall():
                _results.append(dict(zip(_columns, _row)))
            _df_list.append(_results)        
            if not cursor.nextset():
                break

        cursor.close()
        conn.close()
        logging.info(f"MSSQL call completed! Received results, count[{len(_df_list)}]")
        return _df_list
    except Exception as error:
        return f"EXCEPTION: {error}"

##// //###############################################################

##// SNOWFLAKE access SYNC //#########################################

def _snowflake_access_sync(SF_CONN_STR, SQL_SCRIPT) -> list:
    try:
        logging.info("SNOWFLAKE (sync) call starting...")
        sfConn = snowflake.connector.connect(**SF_CONN_STR)
        _pddf = sfConn.execute_string(SQL_SCRIPT)
        _dfdata = []
        for c in _pddf:
            _df = c.fetch_pandas_all()
            _dfdata.append(_df)
        sfConn.close()
        logging.info(f"SNOWFLAKE (sync) call completed! Received results, count[{len(_dfdata)}].")
        return _dfdata
    except Exception as error:
        #print (f"ERROR! {error}")
        return error

##// //###############################################################

##// SNOWFLAKE access ASYNC //########################################

def _snowflake_access_async(SF_CONN_STR, SQL_SCRIPT):
    try:
        logging.info("SNOWFLAKE call starting...")
        sfConn = snowflake.connector.connect(**SF_CONN_STR)
        sfCur = sfConn.cursor()
        _query_ref = sfCur.execute_async(SQL_SCRIPT)
        sfConn.close()
        logging.info(f"SNOWFLAKE (async) call completed! Submitted query[{_query_ref}].")
        return _query_ref  
    except Exception as error:
        logging.info(error)
        return f"EXCEPTION: {error}"

##// //###############################################################
