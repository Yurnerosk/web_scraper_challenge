# !!! WEB SCRAPER CHALLENGE !!!
## Browser Automation with Selenium and Chrome, designed for Robocorp Control Room 

Hello, welcome to my web scraper repository!

This project has 3 parts:

- configurations_class.py : Responsible for importing Robocorp Control Room commands;
- excel_class.py : Responsible for saving the excel file;
- web_scraper_r_p_a.py : Responsible for general navigation and data gathering.

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

Available sections:

"world & nation", "politics", "business", "opinion", "entertainment & arts", "archives", "travel & experiences", "science & medicine", "climate & environment", "books", "food", "movies", "sports", "television", "autos", "music", "greenspace", "letters to the editor"


```
{
  "search_phrase": "climate",
  "sections": [
    "world & nation"
  ],
  "months_number": 1
}

```

## Dependencies
- RPA Framework
- Robocorp
- Selenium

All of the required dependencies are listed in [conda.YAML](https://github.com/Yurnerosk/web_scraper_challenge/blob/main/conda.yaml).

## Pending solutions:
There are some points i need to refine in this code, from the interview feedback. The points are:

- The code needs modularization. It seems that it's unidimention, and can be fixed by using Abstract Methods (something about "separation of concerns").
- I've used absolute Xpaths to some selectors, so the code might be fragile (Did I really use absolute or relative?)
- This code violates the Single Responsability Principle, so ir conbines unrelated methods so it refactors inheritance.

Contributions welcome!! :D

I also don't know how to use git yet, so I hope I can make this easier for everybody.
