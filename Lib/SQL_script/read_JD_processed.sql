INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';

SELECT 
    job_name, 
    company_name, 
    max(one_sentence_description) as one_sentence_description, 
    max(keywords) as keywords, 
    max(job_details_content) as job_details_content
FROM read_parquet('s3://jobdatabucket/silver/JD_Processed/dt='|| strftime(current_date, '%Y%m%d') || '/JD_Processed.parquet')
GROUP BY job_name, company_name
