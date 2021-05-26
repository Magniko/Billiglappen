import os
import json
import logging
import urllib.request
from urllib.error import HTTPError

#REPORT = os.environ["REPORT"]
ERROR = os.environ["ERROR_WEBHOOK"]
WARNING = os.environ["WARNING_WEBHOOK"]


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
        error_str = ("* *ERROR* *: Error message %d at %s for XPath in %s." % (e, e_info[0], e_info[1]), "%s" % (errors[e]) )
    
    elif len(e_info) == 1:
        error_str = ("* *ERROR* *: Error message %d at %s." % (e, e_info[0]), "%s" % (errors[e]) )

    else:
        error_str = ("* *ERROR* *: Error.", "undefined error")


    logging.error("%s", '\n\t'.join(error_str))
    send_slack(ERROR, error_str)
    return -1


def price_change(column, new_price, current_price, id_, table, diff):
    warning_str = ("* *WARNING* *: Price change for %s of %s in %s."  % (column, id_, table),  "Price went from %s to %s or %f%%." % (current_price, new_price, (diff*100)))
    logging.warning("%s", '\n\t'.join(warning_str))
    send_slack(WARNING, warning_str)

    return -2

    
"""def scraping_report(time, errors, warnings, successes):
    report_str = ("* *REPORT* *: Scraping session completed in %f seconds." % (time), "Errors: %d\nWarnings: %d\nSuccesses: %d" % (errors, warnings, successes))
    logging.debug("%s", '\n\t'.join(report_str))
    send_slack(REPORT, report_str)

    return -2"""


"""def send_email(message):
    port = 465  # For SSL
    smtp_server = "mail.billiglappen.no"
    sender_email = "debug@billiglappen.no"
    receiver_email = "admin@billiglappen.no"

    password = os.environ["DEBUG_PASS"]
    #message = f"Subject: {message[0]}\n\n{message[1]}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)"""




def send_slack(type_url, message):

    slack_data = {
                                "blocks": [ {
                                            "type": "section",
                                            "text": {
                                                    "type": "mrkdwn",
                                                    "text": f"{message[0]}\n*{message[1]}*"
                                            }
                                }]
                }
            
            
                data = json.dumps(slack_data).encode()
            
                req = urllib.request.Request(type_url, data=data, headers={'Content-Type': 'application/json'})
                try:
                    r = urllib.request.urlopen(req)
            
                except HTTPError as err:
                    print(err.msg)
                    raise ValueError(
                        "Request to slack returned an error %s, the response is:\n%s"
                        % (err.status, err.info)
                )
