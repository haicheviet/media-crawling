
scrapy crawl comments \
    -a email="$FACEBOOK_EMAIL" \
    -a password="$FACEBOOK_PASSWORD" \
    -a post_id="3020469904855099" \
    -a post="https://m.facebook.com/story.php?story_fbid=3020469904855099&id=1871020459800055&fs=0&focus_composer=0" \
    -a max="100" \
    -o "./test_commend.csv"
