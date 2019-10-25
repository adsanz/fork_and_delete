#!/usr/bin/python3
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


# How to get client_id and client_secret https://confluence.atlassian.com/bitbucket/oauth-on-bitbucket-cloud-238027431.html
class ClientDetails:
    client_id = "" 
    client_secret = ""
    redirect_uri = "https://localhost.com"
    auth_uri = "https://bitbucket.org/site/oauth2/authorize"
    token_uri = "https://bitbucket.org/site/oauth2/access_token"
    server_base_uri = "https://api.bitbucket.org/"
    project_keys= []
    project_keys_migrate = []
    team_name=""
    team_name_migrate = ""


clt = ClientDetails()
# Using client credential grant workflow -> https://developer.atlassian.com/bitbucket/api/2/reference/meta/authentication
bitbucket_session = OAuth2Session(clt.client_id,client=BackendApplicationClient(clt.client_id))
bitbucket_session.fetch_token(
    clt.token_uri,
    username=clt.client_id,
    password=clt.client_secret,
)

# a list of repos that will be not processed
repos_to_avoid = []



request = bitbucket_session.get(clt.server_base_uri + "2.0/repositories/grupopromotive").json() 
while True:
    for items in request["values"]:
        if items["project"]["key"] in clt.project_keys:
            if items["slug"] not in repos_to_avoid:
                fork_repo_req = bitbucket_session.post(clt.server_base_uri + "2.0/repositories/{}/{}/forks".format(clt.team_name,items["slug"]), json={"name":"{}".format(items["slug"]),"project":{"key":"SD"},"owner":{"username":"{}".format(clt.team_name_migrate)}})
                if fork_repo_req.status_code != 201:
                    print("Could not fork repo -> {} got status code -> {}".format(items["slug"]),fork_repo_req.status_code))
                    pass
                else:
                    print("Forked repo -> {} status code -> {} ".format(items["slug"],fork_repo_req.status_code))
                    og_repo_del = bitbucket_session.delete(clt.server_base_uri + "2.0/repositories/{}/{}/".format(clt.team_name,items["slug"]))
                    print("Deleted forked repo -> {} status code -> {}".format(items["slug"],og_repo_del.status_code))
            else:
                repo_del_not_forked = bitbucket_session.delete(clt.server_base_uri + "2.0/repositories/{}/{}/".format(clt.team_name,items["slug"]))
                print("Deleted repo not forked -> {} status code -> {}".format(items["slug"],repo_del_not_forked.status_code))
    try:
        request = bitbucket_session.get(request["next"]).json()
    except KeyError:
        break
print("Done")


