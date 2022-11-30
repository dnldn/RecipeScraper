# RecipeScraper
A trio of scripts for extracting recipes from cooking websites and writing them to formatted text files. Uses the recipe_scrapers, requests, and BeautifulSoup libraries.

1) URLs are initially scraped with crawl.py- all links that are outputted as "Internal Link" can be copied to a list.
2) This list is run through filter.py to determine whether it is a recipe or not, based on schema.org metadata.
3) Recipe URLs are then run through format.py, which will parse them to readable format. Examples below:

https://www.seriouseats.com/chorizo-stuffed-chicken-breasts-queso-sauce-recipe >
https://github.com/dnldn/RecipeScraper/blob/main/Examples/Chorizo-Stuffed_Chicken_Breasts_With_Queso_Sauce_Recipe.txt

https://www.seriouseats.com/goi-buoi-pomelo-salad-recipe >
https://github.com/dnldn/RecipeScraper/blob/main/Examples/Goi_Buoi_(Vietnamese_Pomelo_Salad)_Recipe.txt

https://www.seriouseats.com/zucchini-pineapple-bread-recipe >
https://github.com/dnldn/RecipeScraper/blob/main/Examples/Zucchini_Pineapple_Bread_Recipe.txt
