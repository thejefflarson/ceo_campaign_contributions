import simplejson, urllib, sys

class ResultError(Exception):
    pass

def load_json(order, NYT_BASE, **kwargs):
    url = NYT_BASE + "/".join( kwargs[stmt] for stmt in order if kwargs.has_key(stmt)) + "." + kwargs['response_format']
    url += "?api-key=" + kwargs['app_id']
    if kwargs.has_key('search'):
        url += "&" + urllib.urlencode(kwargs['search'])
    try:
        try:
            result = simplejson.load(urllib.urlopen(url))
        except ValueError,e:
            sys.stderr.write('error: %s url: %s resp: %s\n' %(e,url, urllib.urlopen(url).read()))
            return 'error: %s url: %s\n' %(e,url)
        if result['status'] == "ERROR":
            # An error occurred; raise an exception
            raise ResultError
        return result['results']
    except ResultError:
        return 'errors %s' %(url)
