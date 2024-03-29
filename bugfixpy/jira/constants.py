import keyring
from requests.auth import HTTPBasicAuth

# Email to access Jira API
API_EMAIL = keyring.get_password("system", "JIRA_API_EMAIL")

# Jira API key
API_KEY = keyring.get_password("system", "JIRA_API_KEY")

# Create authentication object for API calls
AUTH = HTTPBasicAuth(API_EMAIL, API_KEY)

# Account id for the person to link for approval in jira
CONTENT_VERIFIER_ID = "5e546930a17f930c9b959d05"

# API defined headers
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Jira id for transitioning to "planned" in workflow
TRANSITION_PLANNED = 281

# Jira id for transitioning to "in progress" in workflow
TRANSITION_IN_PROGRESS = 291

# Jira id for transitioning to "feedback open" in workflow
TRANSITION_FEEDBACK_OPEN = 511

# Jira id for transitioning to "feedback review" in workflow
TRANSITION_FEEDBACK_REVIEW = 521

# SCW base URL for Jira browsing
SCW_BROWSE_URL = "https://securecodewarrior.atlassian.net/browse/"

# SCW base URL for Jira API
SCW_API_URL = "https://securecodewarrior.atlassian.net/rest/api/latest"

# API response "key" entry
RESPONSE_KEY = "key"

# CHLRQ string
CHLRQ = "CHLRQ"

# CHLC string
CHLC = "CHLC"

# Bulk transition JQL url
BULK_TRANSITION_JQL_URL = "https://securecodewarrior.atlassian.net/browse/CHLC-{chlc}?jql=project%20%3D%20%27CHLC%27%20and%20issuetype%3D%20challenge%20and%20issue%20in%20linkedIssues(%27CHLC-{chlc}%27)%20ORDER%20BY%20created%20DESC"

LINKED_ISSUES_ENDPOINT = "issueLink"

LINKED_ISSUES_ENDPOINT = "project/CHLRQ/versions"

TRANSITION_TO_CLOSED_ID = "191"
