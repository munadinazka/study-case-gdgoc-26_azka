
def test_test_database_connection(test_engine):
    with test_engine.connect() as connection:
        result = connection.exec_driver_sql("SELECT 1")

    assert result.scalar() == 1
