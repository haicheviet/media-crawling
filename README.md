# Crawler
- To deploy app and crawl news install as below
+ pip install poetry
+ poetry install
- To run app

poetry run uvicorn app.main:app --reload

- To crawl new, cd to news_crawl and read README
- To crawl fb, cd to fb_crawl and read README
- To init typesense, docker install typesense
+ `docker run -p 8108:8108 -v/tmp/typesense-data:/data typesense/typesense:0.19.0 \
  --data-dir /data --api-key=$TYPESENSE_KEY `
+ Schedule crontab migrate_news.py and migrate_fb.py to update data to typesense
