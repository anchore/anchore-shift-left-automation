import os
import subprocess
import json
import requests

def run_command(cmd):
    # Run the command and capture the output
    output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    # Return the output
    return output


def pull_existing_issues(url, password, username, project_key):
    search_url = f"{url}/rest/api/3/search?jql=project={project_key}&maxResults=1000"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request(
        "GET",
        search_url,
        headers=headers,
        auth=(username, password)
    )

    result = json.loads(response.text)

    # print(json.dumps(result["issues"][0], indent=4))
    open_issues = []
    for issue in result["issues"]:
        if issue["fields"]["status"]["name"].lower() != "done":
            open_issues.append(issue)

    return open_issues

def get_issue_type(url, password, username, project_key):
    search_url = f"{url}/rest/api/2/issue/createmeta/{project_key}/issuetypes"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request(
        "GET",
        search_url,
        headers=headers,
        auth=(username, password)
    )

    result = json.loads(response.text)

    for issue_type in result["issueTypes"]:
        if issue_type["name"] == "Task":
            return issue_type["id"]

def main():
    # Define the Jira server URL and credentials
    jira_server = os.environ["JIRA_URL"]
    jira_username = os.environ["JIRA_API_USER"]
    jira_password = os.environ["JIRA_API_AUTH_TOKEN"]
    project_key = os.environ['JIRA_PROJECT_KEY']

    existing_issues = pull_existing_issues(jira_server, jira_password, jira_username, project_key)

    issue_type = get_issue_type(jira_server, jira_password, jira_username, project_key)
    print(issue_type)

    # get list of k8s-inventory images

    inventory_list = json.loads(run_command("anchorectl inventory list -o json"))

    # iterate through policy findings

    for inv_image in inventory_list:
        try:
            run_command(f"anchorectl image add --wait {inv_image['imageTag']}")
        except:
            pass
 
        actl_output = json.loads(run_command(
            f"anchorectl image check {inv_image['imageTag']} -o json --detail | jq '.evaluations[].details.findings'"))

        for finding in actl_output:
            if finding["action"] == "stop" and finding['triggerId'] not in str(existing_issues):
                url = f"{jira_server}/rest/api/3/issue"

                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }

                summary = finding['message'][:235] + (finding['message'][235:] and '..')

                payload = json.dumps({
                    "fields": {
                        "description": {
                            "content": [
                                {
                                    "content": [
                                        {
                                            "text": f"Gate: {finding['gate']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                },
                                {
                                    "content": [
                                        {
                                            "text": f"Policy ID: {finding['policyId']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                },
                                {
                                    "content": [
                                        {
                                            "text": f"Image Tag: {inv_image['imageTag']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                },
                                {
                                    "content": [
                                        {
                                            "text": f"Trigger Name: {finding['trigger']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                },
                                {
                                    "content": [
                                        {
                                            "text": f"Trigger ID: {finding['triggerId']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                },
                                {
                                    "content": [
                                        {
                                            "text": f"Message: {finding['message']}",
                                            "type": "text"
                                        }
                                    ],
                                    "type": "paragraph"
                                }
                            ],
                            "type": "doc",
                            "version": 1
                        },
                        "issuetype": {"id": issue_type},
                        "project": {"key": f"{project_key}"},
                        "summary": f"[ANCHORE] {summary}"
                    },
                    "update": {}
                })

                response = requests.request(
                    "POST",
                    url,
                    data=payload,
                    headers=headers,
                    auth=(jira_username, jira_password)
                )

                print(json.dumps(json.loads(response.text),
                    sort_keys=True, indent=4, separators=(",", ": ")))


if __name__ == "__main__":
    main()
