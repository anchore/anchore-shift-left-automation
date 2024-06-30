# anchore-shift-left-automation
This repository has examples for a shift-left implementation of Anchore with GitLab and Jira for an automated workflow

# How to run the generate_policy_tickets_jira.py script
Jira Ticket Generator
The script in its current state will generate Jira tickets from STOP actions in Anchore policy results for a single SBOM in Anchore.

## Usage

### ENV variables

The following environment variables need to be set alongside a functional `anchorectl` connection in order for the script to function:

```
JIRA_API_USER="tests@test.com"
JIRA_API_AUTH_TOKEN="TOKEN12345678910"
JIRA_URL="https://your-domain.atlassian.net"
JIRA_PROJECT_KEY="SAT"
IMAGE="image-repo:tag"
```

### Running the script

The script can be run after setting the environment variables by running `python3 generate_tickets.py`
