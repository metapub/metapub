#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Code lifted from somewhere on the internet...

import argparse
import csv
import json
from math import inf
import os
import random
import sys
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request

from Levenshtein import ratio, matching_blocks, editops

MATCH_DEFAULT = 0.9
ASK_DEFAULT = 0.8
COLORS_DEFAULT = True

TITLE_HEADER_WL = ["article title", "title"]

ARG_HELP_STRINGS = {
    "title_file": "",
    "match_threshold": "a float value determining the minimum Levenshtein ratio to accept a title match (default: " + str(MATCH_DEFAULT) + ")",
    "ask_threshold": "a float value determining the minimum Levenshtein ratio to accept a title match (default: " + str(ASK_DEFAULT) + ")",
    "ansi_colors": "Use colorised text for easier visual match recognition (default: " + str(COLORS_DEFAULT) + ")",
    "start": "Start from this line number",
    "end": "End at this line number"
}

L_JUST = 40
BREAK = "".join(["-" for i in range(80)])
CMP_COLORS = ["blue", "green", "yellow", "red"]
EMPTY_RESULT = {
    "crossref_title": "",
    "similarity": 0,
    "doi": ""
}
MAX_RETRIES_ON_ERROR = 3

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title_file", help=ARG_HELP_STRINGS["title_file"])
    parser.add_argument("-m", "--match_threshold", type=float, default=0.9, help=ARG_HELP_STRINGS["match_threshold"])
    parser.add_argument("-a", "--ask_threshold", type=float, default=0.8, help=ARG_HELP_STRINGS["ask_threshold"])
    parser.add_argument("-c", "--colors", type=bool, default=COLORS_DEFAULT, help=ARG_HELP_STRINGS["ansi_colors"])
    parser.add_argument("--start", type=int, default=0, help=ARG_HELP_STRINGS["start"])
    parser.add_argument("--end", type=int, default=inf, help=ARG_HELP_STRINGS["end"])
    args = parser.parse_args()
    
    header = None
    additional_fields = ["doi", "similarity"]
    
    with open(args.title_file, "r") as f:
        reader = csv.DictReader(f)
        title_field = None
        for field in reader.fieldnames:
            if field.lower() in TITLE_HEADER_WL:
                print(colorise("Using column '" + field + "' as title column", "green"))
                title_field = field
                break
        else:
            print(colorise("ERROR: Could not find a column name which might denote a title column", "red"))
            sys.exit()
        header = reader.fieldnames
        for field in additional_fields:
            if field not in header:
                header.append(field)
        modified_lines = []
        ask_count = 0
        for line in reader:
            line["ask"] = False
            if reader.line_num < args.start or reader.line_num > args.end:
                continue
            print(BREAK)
            title = line[title_field]
            head = "line " + str(reader.line_num) + ", query title:"
            print(colorise(head.ljust(L_JUST) + "'" + title + "'", "blue"))
            ret = crossref_query_title(title)
            retries = 0
            while not ret['success'] and retries < MAX_RETRIES_ON_ERROR:
                retries += 1
                msg = "Error while querying CrossRef API ({}), retrying ({})...".format(ret["exception"], retries)
                print(colorise(msg, "red"))
                ret = crossref_query_title(title)
            result = ret["result"]
            msg_tail = "'{}' [{}]"
            msg_tail = msg_tail.format(result["crossref_title"], result["doi"])
            if result["similarity"] == 1.0:
                msg_head = "Perfect match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "cyan"))
                line.update(result)
                line["ask"] = False
            elif result["similarity"] >= args.match_threshold:
                msg_head = "Good match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "green"))
                line.update(result)
                line["ask"] = False
            elif result["similarity"] >= args.ask_threshold:
                msg_head = "Possible match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "yellow"))
                line.update(result)
                line["line_num"] = reader.line_num
                line["ask"] = True
                ask_count += 1
            else:
                msg_head = "No match found, most similar was ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "red"))
                line.update(EMPTY_RESULT)
                line["ask"] = False
            modified_lines.append(line)
        if ask_count > 0:
            print(BREAK)
            ask_msg = "{} matches found with a similarity between {} and {} will need manual confirmation:"
            ask_msg = ask_msg.format(ask_count, args.ask_threshold, args.match_threshold)
            print(colorise(ask_msg, "green"))
        for line in modified_lines:
            if line["ask"]:
                print(BREAK)
                query_t = line[title_field]
                xref_t = line["crossref_title"]
                # display matching segments in identical colors for easier recognition
                diff = matching_blocks(editops(query_t.lower(), xref_t.lower()), query_t, xref_t)
                query_print = query_t
                xref_print = xref_t
                # ANSI codes increase string length, so we need an offset to compensate
                offset = 0
                for i in range(len(diff)):
                    a, b, c = diff[i]
                    a += offset
                    b += offset
                    offset += 9
                    color = CMP_COLORS[i % len(CMP_COLORS)]
                    query_print = colorise_text_segment(query_print, a, a + c , color)
                    xref_print = colorise_text_segment(xref_print, b, b + c , color)
                query_head = colorise("line {}, query title:".format(line["line_num"]), "blue")
                xref_head = colorise("Possible match ({}):".format(round(line["similarity"], 2)), "yellow")
                print(query_head.ljust(L_JUST) + query_print)
                print(xref_head.ljust(L_JUST) + xref_print)
                answer = input("Do you want to accept the DOI for the match title? (y/n):")
                while answer not in ["y", "n"]:
                    answer = input("Please type 'y' or 'n':")
                if answer == "n":
                    line.update(EMPTY_RESULT)
                
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "import_dois_out.csv"), "w") as out:
            dialect = csv.excel
            dialect.quoting = csv.QUOTE_ALL
            writer = csv.DictWriter(out, header, extrasaction='ignore', dialect=dialect)
            writer.writeheader()
            writer.writerows(modified_lines)

def crossref_query_title(title):
    api_url = "https://api.crossref.org/works?"
    params = {"rows": "5", "query.title": title}
    url = api_url + urlencode(params, quote_via=quote_plus)
    print(url)
    request = Request(url)
    request.add_header("User-Agent", "OpenAPC DOI Importer (https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py; mailto:openapc@uni-bielefeld.de)")
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content)
        items = data["message"]["items"]
        most_similar = EMPTY_RESULT
        for item in items:
            title = item["title"].pop()
            result = {
                "crossref_title": title,
                "similarity": ratio(title.lower(), params["query.title"].lower()),
                "doi": item["DOI"]
            }
            if most_similar["similarity"] < result["similarity"]:
                most_similar = result
        return {"success": True, "result": most_similar}
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}
    
def colorise(text, color):
    return colorise_text_segment(text, 0, len(text), color)
    
def colorise_text_segment(text, start, end, color):
    ANSI_COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m"
    }
    if color not in ANSI_COLORS.keys():
        raise ValueError("Argument 'color' must be one of [" + ", ".join(ANSI_COLORS.keys()) + "]")
    s = ANSI_COLORS[color]
    e = "\033[0m"
    return text[:start] + s + text[start:end] + e + text[end:]
    
if __name__ == '__main__':
    main()
