#Copyright (c) 2011 Andrew Krieger
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import urllib
import re
import getpass

def get_login_url():
    """Returns login url.

    If we're already logged in to ResNet, this just returns None
    Otherwise it returns the URL we need to log in to,
    eg "tnc1cas02.resnet.ohio-state.edu/auth/perfigo_weblogin.jsp"
    """


    #See if we're logged in already
    #If we are, this will go through to xkcd, which returns a 404
    #If we aren't this will let us find the login url
    conn = urllib.urlopen("http://www.xkcd.com/404")
    code = conn.getcode()
    data = conn.read()
    conn.close()

    if code != 404:
        #We are not logged in.  Find the login url in the response text
        #Just grab the first thing that looks like a URL.
        #Assume it ends with a single quote, double quote, or space
        #As of April 2011, this finds a
        #<META http-equiv='refresh' content='url'> tag that works perfectly
        url = re.search("https://[^ '\"]+", data)
        if url is None:
            #No result found - time to die
            #This probably means OSU changes the ResNet response page
            raise Exception("Could not find login url")
        
        #Return the URL
        return url.group(0)

    else:
        #A good response means we're already signed in
        return None

def get_captive_form(url):
    """Downloads the login form from ResNet.  Returns (loginurl, params).

    The url passed to this function should be the return value of get_login_url.

    The loginurl returned is the url to submit the login response to.
    The params should be POST'ed with the login response.  They are a collection of random name/value pairs passed in hidden inputs.  Better just to pass them along; I think they're important.
    """

    #Connect to the login form
    conn = urllib.urlopen(url)
    code = conn.getcode()
    data = conn.read()
    conn.close()

    if code != 200:
        raise Exception("Failed to retrieve login form")

    #Find the form's path
    loginurl =  re.search('<form method="post" name="loginform" action="([^"]+)"', data)
    if loginurl is None:
        raise Exception("Could not find form path")
    loginurl = loginurl.group(1)

    #The loginurl we found is relative; paste it to the current url
    #after stripping the file name from url
    url = re.search("(.*/)[^/]+", url).group(1)
    loginurl = url + loginurl

    #The re searches for hidden inputs.
    #Be careful, it's not pretty.
    hidden_inputs = re.findall(r"""<input\s+type\s*=\s*(["'])hidden\1\s+name\s*=\s*(["'])([^"']+)\2\s+value\s*=\s*(["'])([^"']+)\4\s*/>""", data)

    #Now iterate over the hidden inputs, and add them to the params list
    #a, b, and d are random quotes that we don't care about now
    #but that we needed to properly match the re
    params = {}
    for a,b, name, d, value in hidden_inputs:
        params[name] = value

    #MODIFY THIS PART

    #Put in your name.number inside the quotes
    params["username"] = "name.1"


    params["password"] = getpass.getpass("OSU Login Password: ")

    #If you want, you can comment the above line and uncomment the code below
    #Then put your password in plaintext in the quotes, and you won't have to enter it
    #Of course, then anyone could just read your password if they look in this file

    #params["password"] = "your password in plaintext here"

    return (loginurl, params)

def do_login(loginurl, params):
    conn = urllib.urlopen(loginurl, urllib.urlencode(params))
    code = conn.getcode()
    data = conn.read()
    conn.close()

    if not re.search("success", data, re.I):
        raise Warning("Could not confirm success")



if __name__ == "__main__":
    url = get_login_url()
    if url is None:
        print "Already logged in to ResNet."
    else:
        (loginurl, params) = get_captive_form(url)
        do_login(loginurl, params)

