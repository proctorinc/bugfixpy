import sys

from bugfixpy.git.fix_result import FixResult
from bugfixpy.constants import colors, instructions
from bugfixpy.git.repository import Repository
from bugfixpy.scraper.scraper_data import ScraperData
from bugfixpy.scripts import transition
from bugfixpy.scripts.git import make_changes_in_repository
from bugfixpy.formatter import Text
from bugfixpy.utils import prompt_user
from bugfixpy.jira.issue import (
    ChallengeRequestIssue,
)

from . import utils


def run(test_mode: bool) -> None:
    utils.print_mode_headers(test_mode)
    challenge_data = utils.scrape_challenge_data_from_cms()
    repository = clone_the_challenge_repository(
        challenge_data.application.repository_name
    )
    challenge_request_issue = prompt_user.get_challenge_request_issue()
    fix_results = make_changes_in_repository(repository, challenge_request_issue)
    push_fix_to_github_if_not_in_test_mode(repository, test_mode)
    transition_challenge_issues_with_results(
        fix_results, challenge_data, challenge_request_issue
    )
    utils.print_end_instructions_based_off_of_results(fix_results)


def clone_the_challenge_repository(repository_name) -> Repository:
    try:
        print("Cloning Repository...", end="")
        repository = Repository(repository_name)

        utils.print_repository_details(repository)
    except ValueError:
        Text("Error getting repository", colors.FAIL).display()
        sys.exit(1)

    return repository


def push_fix_to_github_if_not_in_test_mode(repository, test_mode) -> None:
    try:
        if test_mode:
            print(f"{colors.HEADER}Test mode enabled. Push skipped{colors.ENDC}")
        else:
            input(instructions.PROMPT_FOR_ENTER_PUSH_ENABLED)
            repository.push_fix_to_github()
    except KeyboardInterrupt:
        print(f"\n{colors.FAIL}Skipped push to repository{colors.ENDC}")


def transition_challenge_issues_with_results(
    fix_result: FixResult,
    challenge_data: ScraperData,
    challenge_request_issue: ChallengeRequestIssue,
) -> None:
    try:
        transition.transition_jira_issues(
            fix_result,
            challenge_data,
            challenge_request_issue,
        )

    except Exception as err:
        print(err)
        sys.exit(1)