-- MinIO 连接配置（dbcode 插件需要）
INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';

with company_info as (
    SELECT company_name, company_url, company_box_content, company_score
    FROM read_parquet('s3://jobdatabucket/bronze/company_info/dt=20251225/company_info_with_score.parquet')
)
SELECT jd.*, co.company_url, co.company_box_content, co.company_score
FROM read_json('s3://jobdatabucket/raw/raw_json/dt=2025-12-19/*.json') as jd
JOIN company_info as co
ON jd.company_name = co.company_name
WHERE co.company_score >= 0

