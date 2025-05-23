from peewee import PostgresqlDatabase


db = PostgresqlDatabase(
    'bees', 
    user='postgres', 
    password='postgres',
    port=5432
)
