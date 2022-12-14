BACKEND = "frontera.contrib.backends.sqlalchemy.Distributed"
SQLALCHEMYBACKEND_ENGINE = "sqlite:///news.db"
MAX_REQUESTS = 2000
MAX_NEXT_REQUESTS = 10
DELAY_ON_EMPTY = 0.0
SPIDER_FEED_PARTITIONS = 1
SPIDER_LOG_PARTITIONS = 1
HTTPCACHE_ENABLED = (
    False  # Turns off disk cache, which has low hit ratio during broad crawls
)
REDIRECT_ENABLED = True
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 120
RETRY_ENABLED = (
    False  # Retries can be handled by Frontera itself, depending on crawling strategy
)
DOWNLOAD_MAXSIZE = (
    10 * 1024 * 1024
)  # Maximum document size, causes OOM kills if not set
LOGSTATS_INTERVAL = 10

# auto throttling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_DEBUG = False
AUTOTHROTTLE_MAX_DELAY = 3.0
AUTOTHROTTLE_START_DELAY = (
    0.25  # Any small enough value, it will be adjusted during operation by averaging
)
# with response latencies.
RANDOMIZE_DOWNLOAD_DELAY = False

# concurrency
CONCURRENT_REQUESTS = (
    100  # Depends on many factors, and should be determined experimentally
)
DOWNLOAD_DELAY = 0.0
