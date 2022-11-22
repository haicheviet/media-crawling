
### How to Run

- Fill your Facebook credentials into [`credentials.yaml`](credentials.yaml)
- Edit the [`input.txt`](input.txt) file and add profile, groups and individual group posts links as you want in the following format with each link on a new line:

Make sure the link only contains the username or id number at the end and not any other stuff. Make sure its in the format mentioned above.

Run the `ultimate-facebook-scraper` command ! 🚀

```python
python scraper/scraper.py
```

> Note: There are two modes to download Friends Profile Pics and the user's Photos: Large Size and Small Size. By default they are set to Small Sized Pics because its really quick while Large Size Mode takes time depending on the number of pictures to download.

You can personalize your scrapping needs using the command line arguments:

```python
python scraper/scraper.py \
    --uploaded_photos True \
    --friends_photos True \
    --friends_small_size True \
    --photos_small_size True \
    --total_scrolls 2500 \
    --scroll_time 8
```

Note that those are the default values so no need to write them down if you're just testing or are okay with them.


---
