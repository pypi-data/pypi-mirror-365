from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase





import os

def get_authors(authors_str):
    """
    Generate a string representation of authors from a BibTeX-style string.
    If there is only one author, returns "FirstInitial. MiddleInitial. LastName, ".
    If there are multiple authors, returns "FirstAuthor _et al_.".

    Parameters:
        authors_str (str): A string of authors in BibTeX format (e.g., "Last, First Middle and Last, First").

    Returns:
        str: Formatted author string.
    """
    # Split the authors string into individual authors
    author_list = [author.strip() for author in authors_str.split(" and ")]

    # List to hold formatted author names
    formatted_names = []

    for author in author_list:
        # Split into "Last, First Middle" or "First Middle Last" format
        if ", " in author:
            last_name, first_name_middle = author.split(", ", 1)
            name_parts = first_name_middle.split()
        else:
            name_parts = author.split()
            last_name = name_parts[-1]

        # Extract first and middle names
        first_name = name_parts[0]
        middle_name = name_parts[1] if len(name_parts) > 1 else ""

        # Construct the formatted name
        middle_initial = f"{middle_name[0]}." if middle_name else ""
        formatted_name = f"{first_name[0]}. {middle_initial}{last_name}".strip()
        formatted_names.append(formatted_name)

    # Generate the final author string based on the number of authors
    if len(formatted_names) == 1:
        authors_string = f"{formatted_names[0]}, "
    elif len(formatted_names) > 1:
        authors_string = f"{formatted_names[0]} _et al_."
    else:
        authors_string = "No authors available."

    return authors_string


def render_software(bib_data):

     authors = get_authors(bib_data.persons['author'])
     year      = bib_data.fields['year']
     url       = bib_data.fields['url']
     text = authors + ' ' + '[' + url + '](' + url + '), ' + year 

     return text

def render_book(bib_data):

     authors = get_authors(bib_data.persons['author'])
     year      = bib_data.fields['year']
     url       = bib_data.fields['url']
     publisher       = bib_data.fields['publisher']
     text = authors + ' ' + '[' + publisher + '](' + url + '), ' + year 

     return text


def render_article(bib_data):

     authors = get_authors(bib_data['author'])
     journal = bib_data['journal']
     year = bib_data['year']
     pages = bib_data['pages']
     volume = bib_data['volume']
     url = bib_data['url']

     # Construct the formatted text
     text = (
        f"{authors} [{journal}]({url}) {volume}, {pages} ({year})"
     )

     return text



def format(entry_key,bibfile=None):

    #If not provided we default to the user-wide one
    if not bibfile:
       bibfile = os.path.expanduser("~/.plix/biblio.bib")

    with open(bibfile, encoding="utf-8") as f:

     parser = BibTexParser()
     library = parser.parse_file(f)   


    entries = library.entries


    bib_data = next((e for e in entries if e["ID"] == entry_key), None)


    
    if bib_data['ENTRYTYPE'] == 'software':
        return render_software(bib_data)
    elif bib_data['ENTRYTYPE']== 'book':
        return render_book(bib_data)
    elif bib_data['ENTRYTYPE'] == 'article':
        return render_article(bib_data)
    
    return "Unsupported entry type or entry not found."
    


