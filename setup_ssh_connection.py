"""
Script to add SSH connection to Airflow
Run this inside the Airflow container or as part of initialization
"""
from airflow.models import Connection
from airflow.settings import Session

def add_ssh_connection():
    """Add Windows SSH connection to Airflow"""
    conn_id = 'windows_ssh'
    
    # Check if connection already exists
    session = Session()
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    
    if existing_conn:
        print(f"Connection '{conn_id}' already exists. Updating...")
        existing_conn.conn_type = 'ssh'
        existing_conn.host = '192.168.1.100'
        existing_conn.login = 'airflow'
        existing_conn.password = 'airflow'
        existing_conn.port = 22
        session.commit()
        print(f"✅ Connection '{conn_id}' updated successfully")
    else:
        new_conn = Connection(
            conn_id=conn_id,
            conn_type='ssh',
            host='192.168.1.100',
            login='airflow',
            password='airflow',
            port=22
        )
        session.add(new_conn)
        session.commit()
        print(f"✅ Connection '{conn_id}' added successfully")
    
    session.close()

if __name__ == '__main__':
    add_ssh_connection()

