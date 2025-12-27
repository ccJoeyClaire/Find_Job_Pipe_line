--MinIO 连接配置（dbcode 插件需要）
-- INSTALL httpfs;
-- LOAD httpfs;
-- SET s3_endpoint='localhost:9000';
-- SET s3_access_key_id='minioadmin';
-- SET s3_secret_access_key='minioadmin';
-- SET s3_use_ssl=false;
-- SET s3_url_style='path';

-- 查询数据
select * 
from read_parquet('s3://jobdatabucket/bronze/company_info/dt=20251225/company_info_with_score.parquet')
