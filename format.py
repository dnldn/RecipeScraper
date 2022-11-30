import requests
import math
import re
import string
import os
from random import randint
from time import sleep
from recipe_scrapers import scrape_html

class sc:

    # Initializing scraper class.
    def __init__(self, title, url, image, yields, time, ingredients, instructions, nutrients, nutrient_flag):
        self.title = title
        self.filename = self.format_title(title)
        self.url = url
        self.image = image
        self.yields = yields
        self.time = time
        self.ingredients = ingredients
        self.instructions = instructions
        self.nutrients = nutrients
        self.nutrient_flag = nutrient_flag

    # Standardizing preparation/cook time to read out as hours and minutes- as opposed to only minutes.
    def convertTime(self):
        if self.time > 60:
            hours = math.floor(self.time / 60)
            minutes = self.time % 60
            if hours == 1 and minutes == 0:
                return "Prep time: " + str(hours) + " hour"
            elif hours == 1 and minutes != 0:
                return "Prep time: " + str(hours) + " hour and " + str(minutes) + " minutes"
            elif hours > 1 and minutes == 0:
                return "Prep time: " + str(hours) + " hours"
            else:
                return "Prep time: " + str(hours) + " hours and " + str(minutes) + " minutes"
        else:
            return str(self.time) + " minutes"

    # Cleaning output from data extraction of ingredients.
    def clean_ingredients(self, t):
        str = ''
        pattern1 = '\', '
        pattern2 = '\[|\]'

        # Return ingredient list, separating by line break instead of brackets.
        for i in t:
            i = re.sub(pattern1, '\n', i)
            i = re.sub(pattern2, '', i)
            str = str + i + '\n'
        return "Ingredients:\n" + str

    # Cleaning output from data extraction of nutrients.
    def clean_nutrients(self, d):
        nutrients = str(d)
        if nutrients:
            p_cal = "(?<=\'calories\': \')\d+ "
            p_carb = "(?<=\'carbohydrateContent\': \')\d+ g"
            p_fiber = "(?<=\'fiberContent\': \')\d+ g"
            p_pro = "(?<=\'proteinContent\': \')\d+ g"
            p_sug = "(?<=\'sugarContent\': \')\d+ g"
            p_sod = "(?<=\'sodiumContent\': \')\d+ mg"
            p_serve = "(?<=\'servingSize\': \')([a-zA-Z\s]*)\d+"
            p_fat = "(?<=\'fatContent\': \')\d+ g"
            p_sfat = "(?<=\'saturatedFatContent\': \')\d+ g"
            p_ufat = "(?<=\'unsaturatedFatContent\': \')\d+ g"

            # Local function to catch errors - not every recipe has metadata for every column. This stops function from stalling.
            def catchEmpty(pattern, string):
                try:
                    sub = re.search(pattern, string).group()
                    return sub
                except AttributeError:
                    pass
                    return "na"

            # Extract nutrition info for each of the following:
            # Calories, protein, carbohydrates, total fat, saturated fat, unsaturated fat, sodium, sugar, fiber, and servings.
            l_cal = catchEmpty(p_cal, nutrients)
            l_pro = catchEmpty(p_pro, nutrients)
            l_carb = catchEmpty(p_carb, nutrients)
            l_fat = catchEmpty(p_fat, nutrients)
            l_sfat = catchEmpty(p_sfat, nutrients)
            l_ufat = catchEmpty(p_ufat, nutrients)
            l_sod = catchEmpty(p_sod, nutrients)
            l_sug = catchEmpty(p_sug, nutrients)
            l_fiber = catchEmpty(p_fiber, nutrients)
            l_serve = catchEmpty(p_serve, nutrients)

            # Formatting output of data.
            total_header = str("%-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %s" %("calories", "protein", "carbs", "fat", "satfat", "unfat", "sodium", "sugar", "fiber", "servings"))
            total_nutrients = str("%-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %s" %(l_cal, l_pro, l_carb, l_fat, l_sfat, l_ufat, l_sod, l_sug, l_fiber, l_serve))

            # Get number of servings for calculating nutrients - always using smaller number if more than one number exists.
            try:
                coeff = int(re.search("\d+", l_serve).group())
            except AttributeError:
                coeff = 0
                pass

            # Calculate nutrition macros per serving. Note - metadata fields are not filled out correctly on all recipes, especially older ones, so this may divide
            # the serving nutrition info by the number of servings, instead of the nutrition info of the entire dish.
            def perServing(x, y):
                sub_string = re.search("\d+", x)
                sub_num = int(sub_string.group())
                return str(math.floor(sub_num / y))

            # Calculate only if number of servings is listed.
            if coeff != 0:
                s_cal = perServing(l_cal, coeff)
                s_pro = perServing(l_pro, coeff)
                s_carb = perServing(l_carb, coeff)
                s_fat = perServing(l_fat, coeff)
                s_sfat = perServing(l_sfat, coeff)
                s_ufat = perServing(l_ufat, coeff)
                s_sod = perServing(l_sod, coeff)
                s_sug = perServing(l_sug, coeff)
                s_fiber = perServing(l_fiber, coeff)

                # Format output into table.
                serving_header = str("%-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %s" % ("calories", "protein", "carbs", "fat", "satfat", "unfat", "sodium", "sugar", "fiber"))
                serving_nutrients = str("%-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %s" %(s_cal, s_pro, s_carb, s_fat, s_sfat, s_ufat, s_sod, s_sug, s_fiber))

            # If the number of servings is not listed, return no serving size available.
            else:
                serving_header = ""
                serving_nutrients = "No serving size available."
            total_string = "Total nutrients:\n" + total_header + "\n" + total_nutrients

            # Return nutrition info.
            if serving_header == "":
                serving_string = serving_nutrients
            else:
                serving_string = "Serving size:\n" + serving_header + "\n" + serving_nutrients
            return total_string, serving_string

    # Formatting instructions - numbering steps and adding line breaks.
    def clean_instructions(self, t):
        sbstr = re.split('\n', self.instructions)
        instructions = ''
        count = 1
        for i in sbstr:
            instructions = instructions + str(count) + ") " + i + "\n"
            count = count + 1
        return instructions

    # Formatting the title - replacing characters that may make file IO difficult.
    def format_title(self, s):
        legal_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        title = ''.join(c for c in s if c in legal_chars)
        title = title.replace(' ', '_')
        title = title.replace('\'', '')
        return title

    # String constructor - joining all previous operations to create recipe output.
    def __str__(self):
        self.time = self.convertTime()
        ingredients = self.clean_ingredients(self.ingredients)
        instructions = self.clean_instructions(self.instructions)
        if self.nutrient_flag == 0:
            self.nutrients = "No nutrition value provided."
            str = f"{self.title}\n{self.url}\n{self.time}\n{self.yields}\n\n" + ingredients + "\n" + instructions + "\n\n" + self.nutrients
        else:
            nutrients, serving_nutrients = self.clean_nutrients(self.nutrients)
            str = f"{self.title}\n{self.url}\n{self.time}\n{self.yields}\n\n" + ingredients + "\n" + instructions + "\n\n" + nutrients + "\n" + serving_nutrients
        return str

# Web scrape a given URL using requests and recipe_scraper libraries.
def recipe_scrape(url):
    html = requests.get(url).content
    scraper = scrape_html(html=html, org_url=url)
    if scraper:
        nutrient_flag = 1
        if str(scraper.nutrients()) == "{}":
            nutrient_flag = 0

        #Initialize object.
        s = sc(
            scraper.title(),
            url,
            scraper.image(),
            scraper.yields(),
            scraper.total_time(),
            scraper.ingredients(),
            scraper.instructions(),  # or alternatively for results as a Python list: scraper.instructions_list()
            scraper.nutrients(),  # if available
            nutrient_flag
        )
        return s, s.filename
    else:
        return "Not a valid url.", ""



# This array should be populated with a list of valid URLs containing schema.org recipe metadata.
# Get this by running crawl.py first, then filter.py.
urls = []

# Main function.
if __name__ == '__main__':

    # Set desired output directory for recipes here.
    directory = "/home/recipes/"
    os.chdir(directory)

    # Attempt scrape on each site in urls array.
    for site in urls:
        try:
            recipe, filename = recipe_scrape(site)
            s = str(recipe)
            print(s)
            with open(filename, mode="w", encoding="utf-8") as file:
                file.write(s)

            # Random delay between 1 and 5 seconds before continuing loop - anything less than this may cause server timeouts or worse from the targeted website.
            sleep(randint(1, 5))
        except:
            print("An error occurred.")
