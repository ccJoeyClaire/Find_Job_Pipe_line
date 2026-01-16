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
    FROM read_parquet('s3://jobdatabucket/gold/target_company/dt=*/target_company.parquet')
),
jd_processed as (
    SELECT *
    FROM read_parquet('s3://jobdatabucket/silver/JD_Processed/dt='|| strftime(current_date, '%Y%m%d') || '/JD_Processed.parquet')
)
SELECT jd.*, co.company_url, co.company_box_content, co.company_score
FROM read_json('s3://jobdatabucket/bronze/raw_json/dt='|| strftime(current_date, '%Y%m%d') || '/*.json') as jd
JOIN company_info as co
ON jd.company_name = co.company_name
JOIN jd_processed as jd_p
ON jd.job_name = jd_p.job_name
AND jd.company_name = jd_p.company_name
WHERE co.company_score >= 0 AND jd_p.edu_requirement <> 'Master_above_or_elite_school' AND jd_p.work_exp_requirement <> '3+_years'

