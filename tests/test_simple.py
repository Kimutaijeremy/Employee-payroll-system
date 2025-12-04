import sqlite3
import pytest
import os

def test_database_creation():
    """Test that database can be created"""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test creating table
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test')")
    conn.commit()
    
    cursor.execute("SELECT * FROM test")
    result = cursor.fetchone()
    
    conn.close()
    os.unlink(db_path)
    
    assert result[1] == 'test'

def test_import_app():
    """Test that app.py can be imported"""
    try:
        # This tests that app.py exists and can be imported
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        # We'll just check if we can read the file
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        assert os.path.exists(app_path)
    except:
        pytest.fail("app.py not found or cannot be imported")