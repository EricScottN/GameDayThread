# GameDayThread
Generate GDT on r/hockey and update
```
usage: main.py [-h] [-po POST_OVERRIDE] [-s {hockey,hockeygtt}] [-t TEAM] [-tl TITLE]

optional arguments:
  -h, --help            show this help message and exit
  -po POST_OVERRIDE, --post_override POST_OVERRIDE
                        Forces script to create post if team is found
  -s {hockey,hockeygtt}, --subreddit {hockey,hockeygtt}
                        Override subreddit - defaults to SUBREDDIT in .env file
  -t TEAM, --team TEAM  Override team selection - defaults to MY_TEAM in .env file
  -tl TITLE, --title TITLE
                        Append a message to gdt reddit post title

```
