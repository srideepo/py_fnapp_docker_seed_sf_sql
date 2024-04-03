
--// SNOWFLAKE scripts //---------------------------------------------------------------------------------
CREATE DATABASE DEMO;

--DROP STAGE IF EXISTS BlobSource
CREATE STAGE BlobSource
  URL='<CONTAINER URL>'
  CREDENTIALS=(AZURE_SAS_TOKEN='?<SAS TOKEN>');

CREATE TEMPORARY TABLE DataExtract AS
SELECT 'Col1Row1' AS Col1, 'Col2Row1' AS Col2 UNION
SELECT 'Col1Row2', 'Col2Row2'

COPY INTO @BlobSource/unload/ FROM DataExtract;

LIST @BlobSource;

CREATE OR REPLACE FILE FORMAT csvFormat TYPE = 'csv' FIELD_DELIMITER = ',';

SELECT t.$1, t.$2 
--FROM @BlobSource (file_format => 'csvFormat', pattern=>'[A-Za-z0-9]*.csv') t;
FROM @BlobSource (file_format => 'csvFormat', pattern=>'.*[.]csv.gz') t;
