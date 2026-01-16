INSTALL httpfs;
LOAD httpfs;
SET s3_endpoint='localhost:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin';
SET s3_use_ssl=false;
SET s3_url_style='path';




select 
    company_name, 
    company_url, 
    company_box_content,
    3 * Min(company_size) + 2 * Min(ownership) + 2 * Min(industry) + 3 * Min(mentions) + 1 * Min(culture) + 1 * Min(nationality) as company_score
from read_parquet('s3://jobdatabucket/silver/company_info/dt=*/company_info_with_score.parquet') 
where company_box_content IS NOT NULL
group by company_name, company_url, company_box_content
having company_score >= 0