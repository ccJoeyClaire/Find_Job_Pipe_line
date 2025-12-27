-- MinIO 连接配置（dbcode 插件需要）
INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';

SELECT company_name, company_url, company_box_content
FROM read_json('s3://jobdatabucket/raw/raw_json/dt=2025-12-19/*.json')
GROUP BY company_name, company_url, company_box_content;



