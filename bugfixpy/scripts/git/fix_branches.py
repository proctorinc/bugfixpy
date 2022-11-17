from git import GitCommandError

from bugfixpy.git.repository import Repository
from bugfixpy.constants import jira, colors, instructions
from bugfixpy.jira.issue import ChallengeRequestIssue
from bugfixpy.git.fix_result import FixResult
from bugfixpy.utils import prompt_user
from bugfixpy.scripts.git import cherrypick_commit_across_all_branches


def make_changes_in_repository(
    repository: Repository, challenge_request_issue: ChallengeRequestIssue
) -> FixResult:
    fix_messages = []
    repo_was_cherrypicked = False

    # Get next branch to fix
    current_branch = prompt_user.get_next_branch(repository)

    # Continue to fix branches until user is done
    while current_branch != "":

        # Allow the user to use a keyboard interrupt to stop fixing a branch at anytime
        try:
            # Fix the branch and retrieve the name and fix explanation
            fix_message = __make_fix_and_commit(
                current_branch, repository, challenge_request_issue
            )

            # Add message to list of messages
            fix_messages.append(fix_message)

            # If full app and fix was on the secure branch, cherry-pick branches
            if (
                repository.is_full_app()
                and current_branch == jira.FULL_APP_SECURE_BRANCH
            ):

                # Get the commit ID
                commit_id = repository.get_last_commit_id()

                print("\nCherry-picking Branches...")
                # Run cherry-pick method
                cherrypick_commit_across_all_branches(repository, commit_id)

                # Confirm that cherrypick occurred
                repo_was_cherrypicked = True

        # Catch keyboard interrupt to cancel fixing the current branch
        except KeyboardInterrupt:
            print(
                f'\n{colors.FAIL}Fixing branch "{current_branch}" aborted.{colors.ENDC}'
            )

        current_branch = prompt_user.get_next_branch_or_continue(repository)

        print(colors.ENDC, end="")

    return FixResult(
        fix_messages=fix_messages,
        repo_was_cherrypicked=repo_was_cherrypicked,
        is_chunk_fixing_required=True,
    )


def __make_fix_and_commit(
    branch: str, repository: Repository, challenge_request_issue: ChallengeRequestIssue
) -> str:
    """
    Checks the user out to a branch of their choice, making sure it is a valid branch.
    Opens VS Code for user to make the fix and prompts user to press ENTER when done.
    Continues process if changes were made successfully and commits with a message.
    Returns the commit message and the branch the user successfully fixed.
    """

    # Default commit to unsuccessful
    successful_commit = False

    # Checkout to branch
    repository.checkout_to_branch(branch)

    # Prompt user to make fix
    print(instructions.PROMPT_USER_TO_MAKE_FIX)

    # Open VS Code to make fix
    repository.open_code_in_editor()

    # Prompt for user to enter commit message
    fix_message = prompt_user.for_descripton_of_fix()

    # Continue until a valid commit is successful
    while not successful_commit:
        try:
            # Add files for commit
            repository.add_changes_to_branch()

            # Commit changes in branch with message and challenge request number
            repository.commit_changes_with_message(
                challenge_request_issue.get_issue_id() + ": " + fix_message
            )

        except GitCommandError as err:
            print(err)
            print(instructions.PROMPT_USER_THAT_NO_FIX_WAS_MADE)

            # Prompt user to press enter when fix is made
            prompt_user.to_press_enter()

        else:
            successful_commit = True

    return fix_message