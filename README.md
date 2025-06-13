# Lambda Spiders: Serverless Scrapy on AWS Lambda

This project enables you to run Scrapy spiders as AWS Lambda container functions and save results to S3, making your news aggregation pipeline scalable, serverless, and cost-effective.

---

## **How It Works**

- Each spider is a Python file in the `spiders/` directory.
- The Lambda handler (`run_spider_lambda.py`) receives an event specifying which spider to run and where to store the output in S3.
- The handler dynamically loads the spider, runs it, and writes the output to `/tmp/` (the only writable directory in Lambda).
- After the crawl, the output JSON is uploaded to your specified S3 bucket and key.
- You can trigger the Lambda for each spider individually, in parallel, or on a schedule (e.g., daily).

---

## **Project Structure**

```
lambda_spiders/
├── Dockerfile                # Lambda container build config
├── requirements.txt          # Python dependencies
├── run_spider_lambda.py      # Lambda entrypoint and spider runner
├── items.py                  # Scrapy Item definitions (used by all spiders)
└── spiders/                  # Your Scrapy spiders (one per file)
    ├── cnbc_spider.py
    ├── reuters_spider.py
    ├── yahoo_finance_spider.py
    ├── marketwatch_spider.py
    └── ... (other spiders)
```

---

## **How to Deploy and Use**

### **1. Build the Docker Image**

```sh
docker build -t lambda-spiders .
```

### **2. Push to AWS ECR**

- [Follow AWS docs to create an ECR repo and push your image.](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- Example:
  ```sh
  aws ecr create-repository --repository-name lambda-spiders
  docker tag lambda-spiders:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/lambda-spiders:latest
  aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<region>.amazonaws.com
  docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/lambda-spiders:latest
  ```

### **3. Create a Lambda Function from the Container**

- In the AWS Lambda console, create a new function **from container image**.
- Set the handler to `run_spider_lambda.lambda_handler`.
- Set timeout to 15 minutes (max for Lambda).
- Set memory to 1024MB+ for Scrapy.
- Attach an IAM role with permission to write to your S3 bucket.

### **4. Trigger the Lambda**

- You can trigger the Lambda with a payload like:
  ```json
  {
    "spider_name": "cnbc",
    "s3_bucket": "your-bucket-name",
    "s3_key": "cnbc/2025-06-08.json"
  }
  ```
- Do this for each spider you want to run.

### **5. Automate (Optional)**

- Use AWS EventBridge (CloudWatch Events) to schedule each Lambda daily.
- Or use Step Functions to run them in sequence/parallel.

---

## **How to Add a New Spider**

1. Create a new file in `spiders/` (e.g., `barrons_spider.py`).
2. Define your Scrapy spider class in that file.
3. Make sure it uses `from items import NewsArticleItem` for the item definition.
4. Deploy your updated container image to AWS.

---

## **Best Practices & Notes**

- **Output:** All spider output is written to `/tmp/` and uploaded to S3 as JSON.
- **Dependencies:** All Python dependencies must be in `requirements.txt`.
- **Secrets:** Never hardcode AWS credentials. Use IAM roles for Lambda.
- **ScraperAPI:** If you use ScraperAPI or similar, store the key in an environment variable or AWS Secrets Manager.
- **Lambda Limits:** Lambda has a 15-minute timeout and 512MB `/tmp` space. For very large crawls, consider splitting jobs or using ECS/Fargate.
- **Logs:** Lambda logs go to CloudWatch by default.

---

## **Troubleshooting**

- If your spider fails to import `NewsArticleItem`, check your import paths and ensure `items.py` is in the root of your Lambda package.
- If you get permission errors uploading to S3, check your Lambda IAM role.
- If you hit Lambda timeouts, reduce the number of pages crawled or increase efficiency.

---

## **Contact**

For questions or improvements, open an issue or pull request!