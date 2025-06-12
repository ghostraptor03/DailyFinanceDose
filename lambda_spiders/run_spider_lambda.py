import os
import json
import boto3
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def lambda_handler(event, context):
    spider_name = event.get("spider_name")
    s3_bucket = event.get("s3_bucket")
    s3_key = event.get("s3_key", f"{spider_name}_output.json")

    # Output file in Lambda's /tmp directory
    output_file = f"/tmp/{spider_name}_output.json"
    settings = get_project_settings()
    settings.set('FEEDS', {
        output_file: {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 2,
        }
    })

    # Import the spider dynamically
    import importlib
    spider_module = importlib.import_module(f"spiders.{spider_name}_spider")
    spider_class = getattr(spider_module, [c for c in dir(spider_module) if c.endswith('Spider')][0])

    process = CrawlerProcess(settings)
    process.crawl(spider_class)
    process.start()

    # Upload to S3
    s3 = boto3.client('s3')
    with open(output_file, "rb") as f:
        s3.upload_fileobj(f, s3_bucket, s3_key)

    return {
        "status": "success",
        "s3_bucket": s3_bucket,
        "s3_key": s3_key
    }