# isort: skip_file
import sys
sys.path.insert(0, '/opt/airflow/scripts')
from datetime import datetime, timedelta
from plugin.main_pipeline import run_location_transform
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow import DAG
# =============================================

# Giờ đây Airflow sẽ tìm thấy thư mục 'plugin' ngay lập tức

default_args = {
    'owner': 'data_engineer',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

default_args = {
    'owner': 'data_engineer',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'end_to_end_etl_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',       # Chạy định kỳ vào 2 giờ sáng mỗi ngày
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['production', 'main_etl'],
) as dag:

    def execution_wrapper(**kwargs):
        # Đọc kết nối bảo mật từ giao diện Airflow
        mysql_conn = BaseHook.get_connection('my_mysql_raw')

        print(mysql_conn.host)
        print(mysql_conn.port)
        print(mysql_conn.login)
        print(mysql_conn.password)
        print(mysql_conn.schema)
        postgres_conn = BaseHook.get_connection('my_postgres_dw')

        print(postgres_conn.host)
        print(postgres_conn.port)
        print(postgres_conn.login)
        print(postgres_conn.password)
        print(postgres_conn.schema)

        mysql_str = f"mysql+pymysql://{mysql_conn.login}:{mysql_conn.password}@{mysql_conn.host}:{mysql_conn.port}/{mysql_conn.schema}"

        print(mysql_str)
        postgres_str = f"postgresql+psycopg2://{postgres_conn.login}:{postgres_conn.password}@{postgres_conn.host}:{postgres_conn.port}/{postgres_conn.schema}"
        print(postgres_str)

        # Gọi hàm tổng để chạy toàn bộ quy trình
        run_location_transform(mysql_str, postgres_str, **kwargs)

    run_pipeline_task = PythonOperator(
        task_id='execute_all_etl_steps',
        python_callable=execution_wrapper,
        provide_context=True,
    )

    run_pipeline_task
