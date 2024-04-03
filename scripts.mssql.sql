
--// MSSQL scripts //---------------------------------------------------------------------------------
CREATE MASTER KEY ENCRYPTION BY PASSWORD='<PASSWORD>';
GO

DROP DATABASE SCOPED CREDENTIAL BlobCred;
GO

CREATE DATABASE SCOPED CREDENTIAL BlobCred
WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
     SECRET = '<SAS TOKEN>';
GO

DROP EXTERNAL DATA SOURCE IF EXISTS BlobSource;
GO

CREATE EXTERNAL DATA SOURCE BlobSource
WITH (
    TYPE = BLOB_STORAGE,
    LOCATION = 'https://<STORAGE ACCOUNT>.blob.core.windows.net',
    CREDENTIAL = BlobCred
);
GO

DROP TABLE IF EXISTS Status;
GO

CREATE TABLE Status (Activity VARCHAR(255), Status VARCHAR(255), Timestamp DATETIME2 DEFAULT sysdatetime());
GO

DROP TABLE IF EXISTS ExecutionLog;
GO

CREATE TABLE ExecutionLog ([Timestamp] DATETIME2 DEFAULT(SYSDATETIME()), [Status] VARCHAR(255), [Message] NVARCHAR(2550));
GO

DROP TABLE IF EXISTS BlobImport;
GO 

CREATE TABLE BlobImport (Col1 VARCHAR(255));
GO

--///------------------------------------------------------------------
DROP PROCEDURE IF EXISTS [dbo].[sp_logMessage];
GO

CREATE PROCEDURE [dbo].[sp_logMessage]
	@Status NVARCHAR(55),
	@Message NVARCHAR(2550)
AS
BEGIN
	INSERT INTO [dbo].[ExecutionLog] ([Status], [Message])
	VALUES (@Status, @Message);
END
GO

DROP PROCEDURE IF EXISTS [dbo].[sp_getCommands];
GO

CREATE PROCEDURE [dbo].[sp_getCommands]
	@json NVARCHAR(2550) = '',
	@filename NVARCHAR(2550) = ''
AS
BEGIN
	IF @json LIKE '%inbound%'
	BEGIN
		SELECT CAST(1.4 AS VARCHAR) AS ExecutionOrder, 'INBOUND' AS Action, 'EXECUTE [dbo].[ImportBlob] ''datafiles/Book1.csv''' AS Command, 'MSSQL' AS Target UNION
		SELECT CAST(2.4 AS VARCHAR) AS ExecutionOrder, 'PUBLISH' AS Action, 'SELECT CURRENT_TIMESTAMP();CALL SYSTEM$WAIT(2, ''MINUTES'');' AS Command, 'SNOWFLAKE' AS Target UNION
		SELECT CAST(3.4 AS VARCHAR) AS ExecutionOrder, 'PUBLISH' AS Action, 'SELECT CURRENT_TIMESTAMP();' AS Command, 'BLOB' AS Target UNION
		SELECT CAST(4.4 AS VARCHAR) AS ExecutionOrder, 'PUBLISH' AS Action, 'SELECT CURRENT_TIMESTAMP();' AS Command, 'BLOB1' AS Target
	END
END
GO

DROP PROCEDURE IF EXISTS [dbo].[ImportBlob];
GO

ALTER PROCEDURE [dbo].[ImportBlob]
	@SourceFile NVARCHAR(2550)
AS
BEGIN
	DECLARE @_SQL NVARCHAR(MAX)
	SET @_SQL = 'BULK INSERT BlobImport
					FROM ''' + @SourceFile + '''' +
					' WITH (DATA_SOURCE = ''BlobSource'', FORMAT = ''CSV'');'
	EXECUTE sp_executeSQL @_SQL;
END
GO
