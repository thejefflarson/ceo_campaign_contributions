import simplejson, urllib, pprint
NYT_BASE = "http://api.nytimes.com/svc/elections/us/"
from beckett.finance.utils.app_id import get_app_id


class ResultError(Exception):
    pass

def get_finance_data_json(**kwargs):
    """
    Args, see http://developer.nytimes.com/docs/campaign_finance_api
        resource_type: "candidates","states", "zips", "contributions", ""
        query_file: "donorsearch", "candidate name", "candidate ID", "location", "totals", zip_code, state_abbr 
                    (last two only for type states or zips)
        ------ only for use with contributions ------
        fname: "first name of donor"
        lname: "last name of donor"
        zip: "zip code to search in"
    Just for candidates, donors TK
    returns: python dict
    """
    kwargs.update({
        'app_id': get_app_id(),
        'version': 'v2',
        'response_format':'json',
        'campaign_type':'president', # move to args when useful
        'year':'2008', # ditto
        'data_to_query':'finances', #double ditto
    })
    order = ['version','campaign_type','year','data_to_query', 'resource_type', 'query_file']
    url = NYT_BASE + "/".join(kwargs[stmt] for stmt in order) + "." + kwargs['response_format']
    url += "?api-key=" + kwargs['app_id']
    if kwargs.has_key('search'):
        url += "&" + urllib.urlencode(kwargs['search'])
    try: 
        result = simplejson.load(urllib.urlopen(url))
        if result['status'] == "ERROR":
            # An error occurred; raise an exception
            raise ResultError
        return result['results']
    except ResultError:
        return 'errors'

if __name__=="__main__":
    test = {
        'search':{
                  'fname': 'tim',
                  'lname': 'barton',
                },
        'resource_type': "contributions",
        'query_file': "donorsearch",
    }
