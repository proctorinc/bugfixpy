#!/usr/bin/env python3

# Author Matt Proctor
# Date: 05.09.2022
# Email: mproctor@securecodewarrior.com

import subprocess
import webbrowser
from utils import (
    cherrypick,
    isValidCHLRQ,
    isValidCHLC,
    getCHLRQ,
    getCHLC,
    setupCredentials,
    cloneRepository,
    getBranches,
    isFullApp,
    parseArguments,
    getRepositoryURL,
    fixAndCommitBranch,
    formatMessages,
    commitAddedOrRemovedLines,
    transitionJiraTickets,
)
from text import (
    Colors,
)
from api import (
    apiIsValidCredentials,
)
from constants import (
    API_EMAIL,
    API_KEY,
    FA_SECURE_BRANCH
)

# Matt's current Todo List:###########
#
# TODO: make into portable application
#
######################################

# Main function runs bug-fix program
def main():

    # Parse commandline arguments
    args = parseArguments()

    # Default user is not done fixing branches
    done_fixing = False

    # Set default cherrypick has not occurred
    did_cherrypick = False

    # Hold fix messages for all branches in list
    fix_messages = []

    # Track whether chunks need to be fixed or not
    fix_chunks_required = False

    # define variables from arguments
    repo_name = args.repository
    test_mode = args.test
    setup_mode = args.setup
    chlrq = args.chlrq
    chlc = args.chlc
    no_pick = args.no_pick
    only_transition = args.transition
    api_enabled = args.api
    
    # If setup mode is on, run setup
    if setup_mode:
        setupCredentials()

    elif only_transition:

        # If parameter not entered, prompt user for CHRLQ
        if not chlrq:
            chlrq = getCHLRQ()

        # If parameter not entered, prompt user for CHLC
        if not chlc:
            chlc = getCHLC()

        # Ask user if bulk transition is required
        if input(f'Is bulk transition required? ({Colors.BOLD}{Colors.WHITE}Y{Colors.ENDC}/n): {Colors.WHITE}') != 'n':
            did_cherrypick = True

        fix_messages = input(f'{Colors.ENDC}Enter fix message: {Colors.WHITE}')

        print(Colors.ENDC)

        # Automatically transition jira tickets
        transitionJiraTickets(chlrq, f'CHLC-{chlc}', fix_messages, did_cherrypick)

        exit(0)

    # Check if environment variables do not exist
    elif (not test_mode) and api_enabled and (not API_EMAIL or not API_KEY):
        print(f'{Colors.FAIL}Credentials not setup. Run \'bug-fix.py --setup\' to set up environment variables{Colors.ENDC}')

        # Notify that no email is present
        if not API_EMAIL:
            print(f'{Colors.FAIL}No API email present{Colors.ENDC}')

        # Notify that no api key is present
        if not API_KEY:
            print(f'{Colors.FAIL}No API key present{Colors.ENDC}')

        exit(1)

    # Check if API credentials are valid, otherwise exit program
    if not test_mode and api_enabled and not apiIsValidCredentials():
        print(f'{Colors.FAIL}Invalid API credentials. Run with --setup to change credentials{Colors.ENDC}')
        exit(1)

    # Only get ticket numbers if API is enabled
    if api_enabled:

        # Check that CHLRQ is valid
        if chlrq and not isValidCHLRQ(chlrq):
            # Alert user chlrq is invalid
            print(f'{Colors.FAIL}CHLRQ-{chlrq} is not valid.{Colors.ENDC}')
            exit(1)

        # Check that CHLC is valid
        if chlc and not isValidCHLC(chlc):
            # Alert user chlrq is invalid
            print(f'{Colors.FAIL}CHLRQ-{chlc} is not valid.{Colors.ENDC}')
            exit(1)

    # Check if push is disabled
    if test_mode:
        print(f'{Colors.HEADER}######## TEST MODE - GIT PUSH & API CALLS ARE DISABLED{Colors.ENDC}')

    if no_pick:
        print(f'{Colors.HEADER}######## Cherry-pick disabled - will not cherry-pick all branches{Colors.ENDC}')

    if api_enabled:
        print(f'{Colors.HEADER}######## API Auto transitioning Jira tickets enabled{Colors.ENDC}')
    else:
        print(f'{Colors.HEADER}######## API disabled{Colors.ENDC}')

    # Get all repository information
    repository = cloneRepository(repo_name)
    branches = getBranches(repository)
    is_full_app = isFullApp(repository)
    repository_url = getRepositoryURL(repo_name)

    # Print Details about the repository
    print(f'Repo:{Colors.OKCYAN} {repo_name}{Colors.ENDC}')
    print(f'Branches:{Colors.OKCYAN} {len(branches)}{Colors.ENDC}')

    if is_full_app:
        print(f'Type: {Colors.OKCYAN}Full App{Colors.ENDC}')
    else:
        print(f'Type: {Colors.OKCYAN}Minified App{Colors.ENDC}')

    if not api_enabled:
        print(f'{Colors.WARNING}\n1. Transition CHLRQ to Planned (choose this month)')
        print('2. Transition CHLRQ to In Progress')
        print(f'3. Locate the branch to make the fix on (if secure, choose secure){Colors.ENDC}')

    # Continue to fix branches until user is done
    while not done_fixing:

        # Fix the branch and retrieve the name and fix explanation
        fix_message, fixed_branch = fixAndCommitBranch(repository, repository_url, branches, is_full_app)

        # Remove initial_branch from branches to avoid cherry-picking it
        branches.remove(fixed_branch)

        # Add message to list of messages
        fix_messages.append(fix_message)

        # Keep track of chunks needing to be fixed
        if commitAddedOrRemovedLines(repository):
            fix_chunks_required = True

        # If full app and fix was on the secure branch, cherry-pick branches
        if is_full_app and fixed_branch == FA_SECURE_BRANCH:

            # Get the commit ID
            commit_id = repository.rev_parse('HEAD')

            # If cherry pick is not disabled
            if not no_pick:

                # Run cherry-pick method
                cherrypick(repository_url, branches, commit_id)

            # Confirm that cherrypick occurred
            did_cherrypick = True

        # Prompt user to fix another branch
        fix_branch = input(f'\nFix another branch? (y/{Colors.BOLD}{Colors.WHITE}N{Colors.ENDC}){Colors.ENDC}: {Colors.WHITE}')

        print(Colors.ENDC, end='')

        # If not yes, user is done fixing
        if fix_branch != 'y':
            done_fixing = True

    # If test mode, don't push to repository
    if test_mode:
        input(f'{Colors.HEADER}\nPush Disabled. Press [ENTER] to continue{Colors.ENDC}')
    
    if api_enabled:
        input(f'{Colors.UNDERLINE}{Colors.OKGREEN}{Colors.BOLD}\nPress [ENTER] to push to repo{Colors.ENDC}')

        # Push commit to the repository
        subprocess.check_output(f'git -C {repository_url} push --all', shell=True)

        # If parameter not entered, prompt user for CHRLQ
        if not chlrq:
            chlrq = getCHLRQ()

        # If parameter not entered, prompt user for CHLC
        if not chlc:
            chlc = getCHLC()

        # Automatically transition jira tickets
        transitionJiraTickets(chlrq, chlc, formatMessages(fix_messages), did_cherrypick)
    else:
        print(f'{Colors.WARNING}\n1. Close CHLRQ (add the commit in as a comment){Colors.WHITE}')

        # Print fix messages
        for message in fix_messages:
            print(f'\t{message}')

        print(f'{Colors.ENDC}{Colors.WARNING}2. Link CHLRQ to challenge CHLC (choose \'relates to\'){Colors.ENDC}')

        chlc = input('Enter challenge CHLC number [Ex: 1234]: ')

        webbrowser.open(f'https://securecodewarrior.atlassian.net/browse/CHLC-{chlc}?jql=project%20%3D%20%27CHLC%27%20and%20issuetype%3D%20challenge%20and%20issue%20in%20linkedIssues(%27CHLC-{chlc}%27)%20ORDER%20BY%20created%20DESC')

        print(f'\n{Colors.WARNING}Follow these steps in the open tab')
        print('1. Bulk transition all -> Select all -> Transition -> FEEDBACK OPEN')
        print('2. Bulk transition all -> Select all -> Transition -> FEEDBACK REVIEW')
        print(f'3. Edit -> Change assignee to Thomas and add CHLRQ number in comment [ex: CHLRQ-1234]{Colors.ENDC}')

    print(f'{Colors.WARNING}\nCOMPLETE THE FOLLOWING TASKS:')

    print(f'{Colors.HEADER}\n####################################')
    print('# 1. Update CMS branches to latest #')

    if fix_chunks_required:
        print('#                                  #')
        print('# 2. Commit added or removed lines #')
        print('#    Make sure chunks are correct  #')
    
    print('####################################')

    print(f'{Colors.OKGREEN}{Colors.BOLD}{Colors.UNDERLINE}\nBug Fix Complete.{Colors.ENDC}')

if __name__ == '__main__':
   main()