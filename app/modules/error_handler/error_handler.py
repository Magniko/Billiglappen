import logging

def scraping_error(e, e_info):
    errors = (
        "Scraping Error. XPath does not exist in the HTML document.",
        "Numerical Error. The XPath points to a string, not a number.",
        "Timeout Error. The scraping thread timed out in an attempt to load or scrape the page. Page could be down.",
        "HTTP Error. Could not read the page.",
        ""
    )
    error_str = ""

    if len(e_info) == 2:
        error_str = "Error message %d at %s for XPath in %s.\n\t%s" % (e, e_info[0], e_info[1], errors[e])
    
    elif len(e_info) == 1:
        error_str = "Error message %d at %s. \n\t%s" % (e, e_info[0], errors[e]) 

    else:
        error_str = "Error."

    logging.error("%s", error_str)
    send_email(error_str)
    return -1


def price_change(column, price, id_, type, diff):
    warning_str = "Price change for %s of price %d from %s on table %s significant at %f. Please check it out." % (column, price, id_, table, diff)
    logging.warning(warning_str)
    send_email(warning_str)

    return -2



def send_email(message):
    pass
