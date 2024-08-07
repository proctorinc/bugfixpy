import json
import sys
import readline
from typing import Callable

from bugfixpy import git
from bugfixpy.exceptions import InvalidIssueIdError
from bugfixpy.git import Repository
from bugfixpy.utils import validate
from bugfixpy.utils.text import completer
from bugfixpy.jira import (
    ApplicationCreationIssue,
    ChallengeCreationIssue,
    ChallengeRequestIssue,
    constants,
)
from bugfixpy.utils.text import colors


def __get_valid_input(
    prompt: str, invalid_message: str, is_valid: Callable[[str], bool]
) -> str:
    value = input(prompt)
    print(colors.ENDC, end="")

    while not is_valid(value):
        print(f'{colors.FAIL}"{value}" {invalid_message}{colors.ENDC}')
        value = input(prompt)
        print(colors.ENDC, end="")

    return value


def get_challenge_request_issue() -> ChallengeRequestIssue:
    challenge_request = None

    while not challenge_request:
        challenge_id = input(
            f"{colors.ENDC}Enter {colors.OKCYAN}CHLRQ{colors.ENDC} ticket number: {colors.WHITE}"
        )

        try:
            challenge_request = ChallengeRequestIssue(challenge_id)

        except InvalidIssueIdError:
            print(
                f"{colors.OKCYAN}CHLRQ-{challenge_id}{colors.ENDC} is not valid. Enter 2-4 digits."
            )
    print(colors.ENDC)
    return challenge_request


def get_challenge_creation_issue() -> ChallengeCreationIssue:
    challenge_creation = None

    while not challenge_creation:
        challenge_id = input(
            f"{colors.ENDC}Enter {colors.OKCYAN}CHLC{colors.ENDC} ticket number: {colors.WHITE}"
        )

        try:
            challenge_creation = ChallengeCreationIssue(challenge_id)

        except InvalidIssueIdError:
            print(
                f"{colors.OKCYAN}CHLC-{challenge_id}{colors.ENDC} is not valid. Enter 2-4 digits."
            )
    return challenge_creation


def get_application_creation_issue() -> ApplicationCreationIssue:
    application_creation = None

    while not application_creation:
        challenge_id = input(
            f"{colors.ENDC}Enter {colors.OKCYAN}CHLC{colors.ENDC} ticket number: {colors.WHITE}"
        )

        try:
            application_creation = ApplicationCreationIssue(challenge_id)

        except InvalidIssueIdError:
            print(
                f"{colors.OKCYAN}CHLC-{challenge_id}{colors.ENDC} is not valid. Enter 2-4 digits."
            )
    return application_creation


def to_resolve_merge_conflict() -> None:
    print(
        f"\n{colors.ENDC}{colors.BOLD}Press {colors.OKGREEN}[ENTER] {colors.ENDC}{colors.BOLD}when changes have been made{colors.ENDC}",
        end="\r",
    )
    input("")
    print("\r\r", end="")


def to_press_enter_after_making_changes() -> None:
    print(
        f"\n{colors.ENDC}{colors.BOLD}Press {colors.OKGREEN}[ENTER] {colors.ENDC}{colors.BOLD}when changes have been made{colors.ENDC}",
        end="\r",
    )
    input("")
    print("\r\r", end="")


def if_they_want_to_continue() -> None:
    exit_program = input("Would you like to exit? (Y/n): ")

    if exit_program.upper() == "N":
        print("Continuing..")
    else:
        sys.exit(1)


def for_challenge_id() -> str:
    prompt = f"{colors.ENDC}Enter Challenge ID: {colors.WHITE}"
    invalid_message = "is not a valid Challenge ID"

    application_name = __get_valid_input(
        prompt, invalid_message, validate.is_valid_challenge_id
    )

    return application_name


def for_application_name_or_url() -> str:
    prompt = f"{colors.ENDC}Enter application name or CMS url: {colors.WHITE}"
    invalid_message = "is not a valid application name"

    challenge_id = __get_valid_input(
        prompt, invalid_message, validate.is_valid_application_name
    )

    return challenge_id


def for_branch_in_repository(repository: Repository) -> str:
    branches = repository.get_branches()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.get_list_completer(branches))

    branch = input(f"{colors.ENDC}Enter name of branch: {colors.WHITE}")

    print(colors.ENDC, end="")

    # Check that user input is a valid branch
    while branch not in branches:
        # Alert user branch name is invalid
        print(f'{colors.FAIL}"{branch}" is not a valid branch name{colors.ENDC}')

        # Check if user entered "secure" on a minified app. Suggest minified secure branch
        if (
            not repository.is_full_app
        ) and branch == git.constants.FULL_APP_SECURE_BRANCH:
            minified_secure_branches = repository.get_minified_secure_branch()
            print(
                f"\nThis app is {colors.OKCYAN}Minified{colors.ENDC}, enter the correct secure"
                f" branch: {colors.HEADER}"
            )
            for branch in minified_secure_branches:
                print(branch, end=" ")
            print(colors.ENDC)

        # Prompt user for branch again
        branch = input(f"{colors.ENDC}Enter name of branch: {colors.WHITE}")

        print(colors.ENDC, end="")

    # Disable tab completion
    readline.parse_and_bind("tab: repository-insert")

    return branch


def for_next_branch_or_to_continue(repository: Repository) -> str:
    branches = repository.get_branches()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.get_list_completer(branches))

    branch = input(
        f"\n{colors.ENDC}Enter name of branch to fix another {colors.WHITE}(continue){colors.ENDC}: {colors.WHITE}"
    )

    print(colors.ENDC, end="")

    if branch == "":
        return ""

    # Check that user input is a valid branch
    while branch not in branches:
        # Alert user branch name is invalid
        print(f'{colors.FAIL}"{branch}" is not a valid branch name{colors.ENDC}')

        # Check if user entered "secure" on a minified app. Suggest minified secure branch
        if (
            not repository.is_full_app
        ) and branch == git.constants.FULL_APP_SECURE_BRANCH:
            minified_secure_branches = repository.get_minified_secure_branch()
            print(
                f"\nThis app is {colors.OKCYAN}Minified{colors.ENDC}, enter the correct secure"
                f" branch: {colors.HEADER}"
            )
            for branch in minified_secure_branches:
                print(branch, end=" ")
            print(colors.ENDC)

        # Prompt user for branch again
        branch = input(f"{colors.ENDC}Enter name of branch: {colors.WHITE}")

        print(colors.ENDC, end="")

    # Disable tab completion
    readline.parse_and_bind("tab: repository-insert")

    return branch


def for_descripton_of_fix() -> str:
    prompt = f"{colors.ENDC}Enter description of fix: {colors.WHITE}"

    fix_message = __get_valid_input(prompt, "", validate.is_valid_fix_message)

    if fix_message == " ":
        fix_message = "-"

    return fix_message


def to_press_enter() -> None:
    input(
        f"{colors.UNDERLINE}{colors.OKGREEN}{colors.BOLD}\nPress [Enter] after fix{colors.ENDC}"
    )


def for_repository_name() -> str:
    prompt = "Enter repo name: "
    invalid_message = "is not a valid Git repository"

    repo_name: str = __get_valid_input(
        prompt, invalid_message, validate.is_valid_repository_name
    )

    return repo_name


def for_repository_name_or_challenge_id() -> str:
    name_or_id = input("Enter repository name or challenge id: ")
    is_challenge_id = False

    if validate.is_valid_challenge_id(name_or_id):
        is_challenge_id = True

    return name_or_id


def if_bulk_transition_is_required() -> bool:
    user_input = input(
        f"{colors.ENDC}Is bulk transition required? ({colors.BOLD}{colors.WHITE}N{colors.ENDC}/y): {colors.WHITE}"
    )
    if user_input.lower() == "y":
        return True

    return False


def to_press_enter_to_transition_request_issue(issue: ChallengeRequestIssue) -> None:
    input(
        f"\nPress {colors.OKGREEN}[Enter]{colors.ENDC} to auto transition {colors.OKCYAN}{issue.get_issue_id()}{colors.ENDC}"
    )


def to_press_enter_to_transition_creation_issues(number_of_issues: int) -> None:
    try:
        input(
            f"\nPress {colors.OKGREEN}[Enter]{colors.ENDC} to auto transition [{colors.OKBLUE}{number_of_issues}{colors.ENDC}] {colors.HEADER}CHLCs{colors.ENDC}"
        )
    except KeyboardInterrupt:
        print(f"\n{colors.FAIL}Skipped transitioning CHLCs{colors.ENDC}")


def to_select_content_verifier() -> dict[str, str]:
    verifier = {"name": "Default: Oscar", "id": constants.CONTENT_VERIFIER_ID}
    try:
        reviewer_file = open("bugfixpy/reviewers.json", encoding="utf-8")
        data = json.load(reviewer_file)
        users = data["users"]
        reviewer_file.close()
        reviewer_num = enter_reviewer_number(users)
        return users[reviewer_num]

    except Exception as err:
        print(err)

    return verifier


def enter_reviewer_number(users: list[dict[str, str]]) -> int:
    if len(users) > 0:
        for i, user in enumerate(users):
            print(f"{i}.", user["name"])

        while True:
            user_choice = input("\nEnter number of reviewer: ")

            try:
                reviewer_num = int(user_choice)
                if reviewer_num < 0 or reviewer_num >= len(users):
                    print("Invalid choice, try again")
                else:
                    return reviewer_num
            except Exception:
                print("Invalid choice, please enter a number")

    return -1


def to_confirm_application_url(application_urls: list[str]) -> int:
    print("Multiple application matches: ")

    if len(application_urls) > 0:
        for i, url in enumerate(application_urls):
            print(f"{i}.", url)

        while True:
            user_choice = input("\nEnter number of reviewer: ")

            try:
                url_num = int(user_choice)
                if url_num < 0 or url_num >= len(application_urls):
                    print("Invalid choice, try again")
                else:
                    return url_num
            except Exception:
                print("Invalid choice, please enter a number")

    return -1
