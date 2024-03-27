import azure.functions as func
import datetime
import json
import logging
import snowflake.connector
import pyodbc


app = func.FunctionApp()

##// HTTP trigger //###################################################
@app.route(route="MyHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    sql_read()

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello (v2), {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
##// //###############################################################

##// BLOB input/output //#############################################
@app.function_name(name="BlobOutput1")
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
@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob", 
                  path="inbound/{name}.trigger",
                  connection="AzureWebJobsStorage")
def test_function(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                f"Name: {myblob.name}\n"
                f"Blob Size: {myblob.length} bytes")
    return "ok"

##// //###############################################################

##// private functions SQL access //##################################
def sql_read():
    try:
        logging.info(">>>Inside function")
        AZSQL_CONN_STR = <CONNECTION STRING>
        conn: pyodbc.Connection = pyodbc.connect(AZSQL_CONN_STR)
        logging.info(">>>Inside function")
        cursor: pyodbc.Cursor = conn.cursor()
        cursor.execute("SELECT @@version;")
        row = cursor.fetchone()
        while row:
            outstr = row[0]
            logging.info(row[0])
            row = cursor.fetchone()
        return f"Hello, this is sql endpoint! {outstr}"    
    except Exception as error:
        return f"EXCEPTION: {error}"

##// //###############################################################
