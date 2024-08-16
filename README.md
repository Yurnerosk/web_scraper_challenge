# !!! WEB SCRAPER CHALLENGE !!!
## Browser Automation with Selenium and Chrome, designed for Robocorp Control Room 

Hello, welcome to my web scraper repository!

This project has 3 parts:

- configurations_class.py : Responsible for importing Robocorp Control Room commands;
- excel_class.py : Responsible for saving the excel file;
- web_scraper.py : Responsible for general navigation and data gathering.

## Challenge

This challenge consists of using the website [LA Times](https://www.latimes.com/) to scrape some news. The process
has to follow certain instructions:

- Open link;
- Enter a "search_phrase";
- On the result page:
    - select the desired topics from "sections"
    - select newest news
    - if possible, filter by N last months. If N=0 then N=1.
- Get the values: title, date, and description;
- See if there is money involved, count search phrase in title and description;
- Store info in Excel file;
- Gather the pictures and their names.

**Note:** In this website, there is no such filter for dates, so a loop was created in order to mimic 
the function.

Needless to say that this was a interesting exercise and brought a lot of learning materials.

## Robocorp Input example

This project handles as many sections you want(as long it exists in database).

```
{
  "search_phrase": "climate",
  "sections": [
    "science & medicine", "books"
  ],
  "months_number": 1
}

```

## Dependencies
- RPA Framework
- Robocorp
- Selenium

All of the required dependencies are listed in [conda.YAML](https://github.com/Yurnerosk/web_scraper_challenge/blob/main/conda.yaml).
