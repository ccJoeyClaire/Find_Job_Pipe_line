-- MinIO 连接配置（dbcode 插件需要）
INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';

set time zone 'Asia/Shanghai';

-- 使用当前日期格式化后的字符串（格式：YYYYMMDD）
-- 注意：如果需要在 Python 中动态替换日期，可以使用字符串格式化
-- 使用 union_by_name=True 来处理不同 schema 的 parquet 文件（有些文件可能没有 company_score 列）
-- ' || strftime(current_date, '%Y%m%d') || '
SELECT 
    jd.company_name, 
    jd.company_url, 
    jd.company_box_content
FROM read_json_auto('s3://jobdatabucket/bronze/raw_json/dt=20260225/*.json') as jd
-- left join read_parquet('s3://jobdatabucket/silver/company_info/dt=*/company_info_with_score.parquet', union_by_name=True) as co
-- on jd.company_name = co.company_name
-- where co.company_score IS NULL
-- GROUP BY jd.company_name, jd.company_url, jd.company_box_content;



