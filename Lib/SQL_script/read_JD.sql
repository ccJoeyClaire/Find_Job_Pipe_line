-- MinIO 连接配置（dbcode 插件需要）
INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';

set time zone 'Asia/Shanghai';

-- ' || strftime(current_date, '%Y%m%d') || '

SELECT * 
FROM read_json_auto('s3://jobdatabucket/bronze/raw_json/dt=20260225/*.json') as jd
