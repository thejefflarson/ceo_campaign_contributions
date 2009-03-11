import simplejson, urllib2, sys

class ResultError(Exception):
    pass

def load_json(order, NYT_BASE, **kwargs):
    url = NYT_BASE + "/".join( kwargs[stmt] for stmt in order if kwargs.has_key(stmt)) + "." + kwargs['response_format']
    url += "?api-key=" + kwargs['app_id']
    if kwargs.has_key('search'):
        url += "&" + urllib2.urlencode(kwargs['search'])
    try:
        try:
            response = urllib2.urlopen(url) 
            result = simplejson.load(response)
#            sys.stdout.write('trying %s\n' % (url))
        except ValueError,e:
            sys.stderr.write('error: %s url: %s resp: %s\n' %(e,url, response.read()))
            return 'error: %s url: %s\n' %(e,url)
        if result['status'] == "ERROR":
            # An error occurred; raise an exception
            raise ResultError
        return result['results']
    except ResultError:
        return 'errors %s' %(url)
