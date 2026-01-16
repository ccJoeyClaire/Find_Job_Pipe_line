select
    *,
    concat(
        content_embeddings, 
        job_name_embeddings, 
        one_sentence_embeddings, 
        keywords_embeddings
    ) as all_embeddings,
    concat(
        job_name_embeddings, 
        one_sentence_embeddings, 
        keywords_embeddings
    ) as key_embeddings
from read_parquet('s3://jobdatabucket/features_engineering/raw_data_embeddings/dt=2025-12-30/raw_data_embeddings.parquet')