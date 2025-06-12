FROM public.ecr.aws/lambda/python:3.11

# System dependencies for Scrapy
RUN yum install -y gcc libxml2-devel libxslt-devel

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your code
COPY . .

# Lambda entrypoint
CMD ["run_spider_lambda.lambda_handler"]