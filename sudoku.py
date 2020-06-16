"""
sudoku.py -- scrape common web sources for Sudokus
"""

import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

sudokuexchange_head = "https://sudokuexchange.com/play/?s="


def get_nytimes():
    """Scrape all three NY Times puzzles"""

    url = "https://www.nytimes.com/puzzles/sudoku/easy"
    text = requests.get(url).text
    soup = BeautifulSoup(text, features="html.parser")

    # find the script that starts with `window.gameData =`
    # usually the first but who knows
    for script in soup.find_all("script", type="text/javascript"):
        if not script.contents:
            continue

        contents = script.contents[0]
        start_str = "window.gameData = "
        if contents.startswith(start_str):
            contents = contents.replace(start_str, "")
            puzzle_info = json.loads(contents)

            break

    # now we have puzzle_info as a dict with keys easy, medium, hard
    # and some levels of nesting; get the puzzle information and
    # create the SudokuExchange link
    puzzles = {}
    for difficulty in ("easy", "medium", "hard"):
        digits = puzzle_info[difficulty]["puzzle_data"]["puzzle"]
        digits_str = "".join(str(x) for x in digits)
        puzzles[difficulty] = f"{sudokuexchange_head}{digits_str}"

    return puzzles


def get_dailysudoku():
    """Get puzzle from dailysudoku.com"""

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    url = f"http://www.dailysudoku.com/cgi-bin/sudoku/get_board.pl?year={year}&month={month}&day={day}"
    data = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0"
        },
    ).json()

    numbers = data["numbers"].replace(".", "0")
    return f"{sudokuexchange_head}{numbers}"

def get_tribune():
    """Get puzzle from Tribune Content Agency"""

    # not sure how often this expires
    api_key = ("b366a2d09d81e980a1e3c3eac8ddbe524a3d9a79d88d6e4e92495f8a10e3246a",)
    today = datetime.now().strftime(r"%m/%d/%Y")
    form_data = {
        "apiKey": api_key,
        "productId": "sudoku",
        "publicationDate": today,
        "ldt": today,
    }

    headers = {"Accept": "application/json, text/javascript, */*; q=0.01"}

    data = requests.post(
        "https://puzzles.tribunecontentagency.com/puzzles/pzzResource/puzzle.do",
        data=form_data,
        headers=headers,
    ).json()

    # this just handles the structure of the JSON they return
    numbers = []
    for cell in data["puzzleDetails"]["gCells"]:
        # check if cell was filled out or not
        if cell["qcell"]:
            numbers.append(cell["cellVal"])
        else:
            numbers.append("0")

    cell_string = "".join(numbers)
    return f"{sudokuexchange_head}{cell_string}"



if __name__ == "__main__":
    nytimes_links = get_nytimes()
    for difficulty, link in nytimes_links.items():
        print(f"NY Times {difficulty} -- {link}")

    dailysudoku_link = get_dailysudoku()
    print(f"dailysudoku.com -- {dailysudoku_link}")

    tribune_link = get_tribune()
    print(f"Chicago Tribune -- {tribune_link}")