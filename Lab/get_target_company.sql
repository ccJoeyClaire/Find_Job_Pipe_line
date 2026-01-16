INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';



set time zone 'Asia/Shanghai';


select *
from read_parquet('s3://jobdatabucket/gold/target_company/dt=*/target_company.parquet')