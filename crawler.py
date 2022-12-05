import json
from requests import Session
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
#from selenium import webdriver

#TODO Make Inputs
homepage_url = 'https://curated.investnext.com'
username = 'litanyahav'
password = 'Litan2020!'

#TODO Delete This Function
def get_investment_name(content):
    """
    Input: Parsed BeautifulSoup object from individual investment website
            currently accept the website 'https://curated.investnext.com/portal/investments/34024/3114/'

    Output: string, the name of the individual investment
    """
    class_a = content.find(string='Class A')
    parent = class_a.find_parent().find_parent()
    for child in parent.children:
        name = child.text
        break
    return name.strip()

#TODO Delete this function
def get_investment_name(content):
    """
    Input: Parsed BeautifulSoup object from individual investment website
            currently accept the website 'https://curated.investnext.com/portal/investments/34024/3114/'

    Output: string, the name of the individual investment
    """
    print(content.find(attrs={"comp-id": "42"}))
    table = content.find({'comp-id': '42'}).find_children()
    class_a = content.find(string='Class A')
    parent = class_a.find_parent().find_parent()
    for child in parent.children:
        name = child.text
        break
    return name.strip()



def get_document_info(session):
    """
    Input: Request session logged into https://curated.investnext.com

    Output: response formatted as {"investments": dictionary<list<dictionary>>, "error_log": list} where
                investments represents a dictionary mapping investments to a list of their related documents where each document is represented as a dictionary:
                    {"id": int, "filename": str, "file_type": str, "upload_timestamp": string, "download_link": string}
                error_log represents a list of strings describing

    """
    #Constants
    documents_api = "https://curated.investnext.com/portal/api/documents"

    #Outputs
    error_log = []
    investments  = {}
    response = {"investments": investments, "error_log": error_log}

    #Traverse API
    response_json = session.get(documents_api).json()
    documentsOnPage = response_json.get("documents", None)
    if documentsOnPage == None:
        error_log.append("List of documents not found")
    else:
        id = 0
        for document in documentsOnPage:
            #Get investment document relates to
            investment = document.get("company", None)
            if investment != None:
                investment = investment.get("name", None)
            if investment == None:
                continue
            investment_documents = investments.get(investment, [])
            investments[investment] = investment_documents

            #Gather document data
            id += 1
            documentInfo = {"id":id}

            name = document.get("name", None)
            if name == None:
                error_log.append(f"Document {id} missing name")
            documentInfo["name"] = name

            file_type = document.get("file_type", None)
            if file_type == None:
                error_log.append(f"Document {id} missing file_type")
            documentInfo["file_type"] = file_type

            timestamp = document.get("timestamp", None)
            if name == None:
                error_log.append(f"Document {id} missing timestamp")
            documentInfo["timestamp"] = datetime.fromisoformat(timestamp[:-1])

            download_link = document.get("url", None)
            if name == None:
                error_log.append(f"Document {id} missing download_link")
            documentInfo["download_link"] = download_link

            investment_documents.append(documentInfo)

    return response


"""
Downloads all documents for each investment in 'document_info' using the folder structure below:

Folder Structure: ./Documents/<investment_name>/<document_name>

Input:
    session: Crawler Session that is logged into InvestNext
    document_info: dictionary representation of document info or the output of get_document_info

Output: void
"""
#TODO Make this safer
def download_documents(session, document_info):
    #Creates Document directory
    working_dir = os.getcwd()
    new_folder = "Documents"
    path = os.path.join(working_dir, new_folder)
    os.makedirs(path, exist_ok=True)
    os.chdir(path)

    documents_per_investment = document_info['investments']

    #Creates folder for each investment
    for investment_name, document_list in documents_per_investment.items():
        os.makedirs(investment_name, exist_ok=True)

        #Downloads all documents for each  investment
        for document in document_list:
            if document['download_link'] == None:
                continue
            else:
                document_data = session.get(document["download_link"], allow_redirects = True, stream = True)
                with open(f'./{investment_name}/{document["name"]}.{document["file_type"]}', 'wb') as file:
                    for data in document_data:
                        file.write(data)


#TODO Spec
def get_main_investment_info(session, content):
    """
    Input: Parsed BeautifulSoup object from individual investment website
            currently accept the website 'https://curated.investnext.com/portal/investments/'

    Output: dictionary that represents each variable and the corresponding value.
    """
    #Retrieve the api url from the main page
    account_number = content.find('option', string='All Accounts').find_next_sibling('option').attrs['value']
    main_page_api = 'https://curated.investnext.com/portal/api/investments?account='+str(account_number)

    #Outputs
    error_log = []
    information_dict = {}

    response = {'error_log': error_log, 'information': information_dict}

    #Traverse API and retrieve investment information
    main_page_json = session.get(main_page_api).json()
    investments = main_page_json.get('data', None)
    if investments ==  None:
        error_log.append('Investments not found')
    else:
        id = 0
        investments_info = []
        urls = []
        investment_error_log = []
        for investment in investments:
            id += 1
            investment_info = {'id': id, 'investment_error_log': investment_error_log}

            account = investment.get('account', None)
            if account == None:
                investment_error_log.append(f'Investment {id} missing account')
            investment_info['account'] = account

            project = investment.get('project', None)
            if project == None:
                investment_error_log.append(f'Investment {id} missing project')
            investment_info['project'] = project

            unit_class = investment.get('unit_class', None)
            if unit_class == None:
                investment_error_log.append(f'Investment {id} missing unit_class')
            investment_info['unit_class'] = unit_class

            url = investment.get('url', None)
            if url == None:
                investment_error_log.append(f'Investment {id} missing url')
            investment_info['url'] = url

            investments_info.append(investment_info)
        information_dict['investments'] = investments_info

    contribution_api = 'https://curated.investnext.com/portal/api/data/contributions?account=' + str(account_number)

    contribution_json = session.get(contribution_api).json()
    contribution = contribution_json.get('data', None)
    if contribution == None:
        error_log.append('Missing contribution')
    else:
        capital_balance = contribution_json.get('total', None)
        if capital_balance == None:
            error_log.append('Missing capital balance')
        information_dict['capital balance'] = capital_balance

    distribution_api = 'https://curated.investnext.com/portal/api/data/distributions?account=' + str(account_number)

    distribution_json = session.get(distribution_api).json()
    distribution = distribution_json.get('data', None)
    if distribution == None:
        error_log.append('Missing distribution')
    else:
        distributions = distribution_json.get('total', None)
        if capital_balance == None:
            error_log.append('Missing distributions')
        information_dict['distributions'] = distributions

    return response


def get_transaction_info(session, position, _class):
    """
    Input: Request session logged into https://curated.investnext.com

    Output: response formatted as a list of dictionaries of each individual transaction (determined by the position and class number parsed through the main investment page api),
    including activity type, amount, date, price, and units;
            error_log represents a list of strings

    """
    #Constants
    transactions_api = f"https://curated.investnext.com/portal/api/investments/transactions?position={position}&class={_class}"

    #Outputs
    error_log = []
    transactions = []
    response = {"transactions": transactions, "error_log": error_log}

    #Traverse API
    transactions_json = session.get(transactions_api).json()

    if len(transactions_json) == 0:
        error_log.append("List of transactions not found")
    else:
        id = 0
        for transaction in transactions_json:
            id += 1
            transaction_info = {"id":id}

            activity_type = transaction.get("activity_type", None)
            if activity_type == None:
                error_log.append(f"Transaction {id} missing activity_type")
            transaction_info["activity_type"] = activity_type

            amount = transaction.get("amount", None)
            if amount == None:
                error_log.append(f"Transaction {id} missing amount")
            transaction_info["amount"] = amount

            date = transaction.get("date", None)
            if date == None:
                error_log.append(f"Transaction {id} missing date")
            transaction_info["date"] = datetime.strptime(date, "%b %d %Y")

            price = transaction.get("price", None)
            transaction_info["price"] = price

            units = transaction.get("units", None)
            transaction_info["units"] = units

            transactions.append(transaction_info)

    return response


def main():
    with Session() as session:
        #Perform Login
        session.headers = {'Referer': homepage_url}
        loginPage = bs(session.get(homepage_url,timeout=10).content, "html.parser")
        middlewareToken = loginPage.find("input", {"name":"csrfmiddlewaretoken"})["value"]
        login_info = {'username':username, 'password':password, 'csrfmiddlewaretoken':middlewareToken, 'next': '','distinct_id': ''}
        response = session.post(homepage_url, data=login_info)

        #Retrieve Home Page
        homepage = bs(session.get(homepage_url,timeout=10).content, 'html.parser')
        #print(homepage)

        #Retrieve Main Investment Page
        investmentMain_path = homepage.find("a", string="View Investments")["href"]
        investmentMain_url = homepage_url + investmentMain_path
        investmentMainPage = bs(session.get(investmentMain_url,timeout=10).content, 'html.parser',)
        #print(investmentMainPage)

        #inialize output JSON
        output_data = {'investments' : []}

        #Gather main investment page data
        main_investment_page_response = get_main_investment_info(session, investmentMainPage)
        output_data["error_log"] = main_investment_page_response['error_log']
        main_page_information = main_investment_page_response['information']
        output_data['total_capital_balance'] = main_page_information['capital balance']
        output_data['total_distributions'] = main_page_information['distributions']

        #Gather Document Data and download documents
        document_info = get_document_info(session)
        download_documents(session, document_info)

        #Gather each investment data
        for investment in main_page_information['investments']:
            investment_info = {}
            investment_info['investment_id'] = investment['id']
            investment_info['account_name'] = investment['account']
            investment_info['project_name'] = investment['project']
            investment_info['investment_name'] = investment['unit_class']

            #Handle Error Logging
            investment_info['error_log'] = []
            for key in investment_info:
                if investment_info[key] is None:
                    investment_info['error_log'].append(key)

            #Gather investment transactions page data
            url = investment['url'] #/portal/investments/POSITION/CLASS/
            url_elements = url.split("/")
            position = url_elements[3]
            _class = url_elements[4]
            transaction_response = get_transaction_info(session, position, _class)
            investment_info['transactions'] = transaction_response['transactions']

            #Handle investment transactions error logging
            for transaction in investment_info['transactions']:
                transaction["error_log"] = []
                for key in transaction:
                    if transaction[key] is None:
                        transaction["error_log"].append(key)

            #Handle Document Gathering
            investment_info['documents'] = document_info['investments'].get(investment_info['project_name'],[])

            #Handle document error logging
            for document in investment_info['documents']:
                document["error_log"] = []
                for key in document:
                    if document[key] is None:
                        document["error_log"].append(key)

            #Add investment to output
            output_data["investments"].append(investment_info)

        return output_data

if __name__ == "__main__":
    print(main())
