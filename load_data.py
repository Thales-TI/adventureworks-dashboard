from sqlalchemy import create_engine
import pandas as pd

def carregar_dados():
    # String de conexão com SQLAlchemy
    conn_str = "mssql+pyodbc://localhost/AdventureWorks?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(conn_str)

    # Consulta SQL
    query = """
    SELECT
        soh.SalesOrderID,
        soh.OrderDate,
        soh.TotalDue,
        sp.Name AS RegionName,
        p.Name AS ProductName,
        sod.OrderQty,
        sod.UnitPrice,
        (sod.OrderQty * sod.UnitPrice) AS TotalItemValue
    FROM
        Sales.SalesOrderHeader AS soh
    JOIN
        Sales.SalesOrderDetail AS sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN
        Production.Product AS p ON sod.ProductID = p.ProductID
    JOIN
        Person.Address AS addr ON soh.ShipToAddressID = addr.AddressID
    JOIN
        Person.StateProvince AS sp ON addr.StateProvinceID = sp.StateProvinceID
    """

    # Leitura dos dados
    df = pd.read_sql(query, engine)
    return df