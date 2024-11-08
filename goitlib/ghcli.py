#!/usr/bin/env python3

# stdlib imports
import os
import json
import logging
import functools
import subprocess
from datetime import date, datetime, timedelta

# internal imports
from .edict import Edict

# 3rd party imports
from rich.markdown import Markdown

# Global settings for cache
cache_dir = os.path.join(os.getenv("HOME"), ".cache", "goit")
cache_age = 60 * 30  # 30 minutes in seconds

os.makedirs(f"{cache_dir}/data", exist_ok=True)


def cache_results():
    global cache_dir
    global cache_age

    # Set up logging to file in the cache directory
    log_file = os.path.join(cache_dir, "cache.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Retrieve `owner` and `repo` from kwargs at runtime
            owner = kwargs.get("owner", "default")
            repo = kwargs.get("repo", "default")  # default if repo is not provided
            bypass_cache = kwargs.get("bypass_cache", False)

            if owner is None:
                error_message = (
                    f"{func.__name__}: `owner` must be provided as a keyword argument."
                )
                logger.error(error_message)
                raise ValueError(error_message)

            # Generate cache file path using owner and repo (if provided)
            cache_filename = f"{owner}_-_{repo}_-_{func.__name__}.json"
            cache_path = os.path.join(f"{cache_dir}/data", cache_filename)

            # Check if cache bypass is requested
            if not bypass_cache and os.path.exists(cache_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
                # If cache is valid, return cached data
                if datetime.now() - file_mtime < timedelta(seconds=cache_age):
                    logger.info("Cache hit for %s/%s on %s", owner, repo, func.__name__)
                    with open(cache_path, "r") as cache_file:
                        return json.load(cache_file)
                else:
                    logger.info(
                        "Cache expired for %s/%s on %s", owner, repo, func.__name__
                    )
            else:
                logger.info(
                    "Cache miss or bypass for %s/%s on %s", owner, repo, func.__name__
                )

            # Call the original function and cache the result
            result = func(*args, **kwargs)
            with open(cache_path, "w") as cache_file:
                json.dump(result, cache_file)
            logger.info("Cache updated for %s/%s on %s", owner, repo, func.__name__)

            return result

        return wrapper

    return decorator


class GitHubCLIWrapper:
    def __init__(self):
        super().__init__()

    def _cmd(self):
        return subprocess.run(
            self._cmd_s, shell=True, capture_output=True
        ).stdout.decode()

    def get_overview(self, owner=False, repo=False):
        if not owner or not repo:
            raise ValueError("Owner and repo must be provided.")
        self._cmd_s = f"gh repo view {owner}/{repo}"
        return self._cmd()

    @cache_results()
    def get_repo_info(self, owner=False, repo=False):
        fields = (
            "archivedAt",
            "assignableUsers",
            "codeOfConduct",
            "contactLinks",
            "createdAt",
            "defaultBranchRef",
            "deleteBranchOnMerge",
            "description",
            "diskUsage",
            "forkCount",
            "fundingLinks",
            "hasDiscussionsEnabled",
            "hasIssuesEnabled",
            "hasProjectsEnabled",
            "hasWikiEnabled",
            "homepageUrl",
            "id",
            "isArchived",
            "isBlankIssuesEnabled",
            "isEmpty",
            "isFork",
            "isInOrganization",
            "isMirror",
            "isPrivate",
            "isSecurityPolicyEnabled",
            "isTemplate",
            "isUserConfigurationRepository",
            "issueTemplates",
            "issues",
            "labels",
            "languages",
            "latestRelease",
            "licenseInfo",
            "mentionableUsers",
            "mergeCommitAllowed",
            "milestones",
            "mirrorUrl",
            "name",
            "nameWithOwner",
            "openGraphImageUrl",
            "owner",
            "parent",
            "primaryLanguage",
            "projects",
            "pullRequestTemplates",
            "pullRequests",
            "pushedAt",
            "rebaseMergeAllowed",
            "repositoryTopics",
            "securityPolicyUrl",
            "squashMergeAllowed",
            "sshUrl",
            "stargazerCount",
            "templateRepository",
            "updatedAt",
            "url",
            "usesCustomOpenGraphImage",
            "viewerCanAdminister",
            "viewerDefaultCommitEmail",
            "viewerDefaultMergeMethod",
            "viewerHasStarred",
            "viewerPermission",
            "viewerPossibleCommitEmails",
            "viewerSubscription",
            "visibility",
            "watchers",
        )
        self._cmd_s = f"gh repo view {owner}/{repo} --json {','.join(fields)}"
        return self._cmd()

    @cache_results()
    def get_repositories(self, owner=False, repo=False):
        if not owner or not repo:
            self._cmd_s = "gh repo list --json owner,name -L 1024"
        else:
            self._cmd_s = f"gh repo list --json name -L 1024 {owner}"
        return self._cmd()

    @cache_results()
    def get_issues(self, owner=False, repo=False):
        fields = (
            "assignees",
            "author",
            "body",
            "closed",
            "closedAt",
            "comments",
            "createdAt",
            "id",
            "isPinned",
            "labels",
            "milestone",
            "number",
            "reactionGroups",
            "state",
            "stateReason",
            "title",
            "updatedAt",
            "url",
        )
        self._cmd_s = (
            f"gh issue list -R {owner}/{repo} -L 40960 -s all --json {','.join(fields)}"
        )
        return self._cmd()

    @cache_results()
    def get_pull_requests(self, owner, repo):
        return {"pull_requests": [10, 11, 12, 13]}  # Replace with actual data fetching

    @cache_results()
    def get_actions(self, owner, repo):
        return {"actions": [1, 2, 3]}  # Replace with actual data fetching


class DataPipeline:

    _gh = GitHubCLIWrapper()

    def get_overview(self, o, r):
        data = self._gh.get_overview(owner=o, repo=r)
        # my_stuff = await asyncio.create_subprocess_shell(
        #     GH.repo_info.format(o=o, r=r),
        #     stdout=asyncio.subprocess.PIPE,
        #     shell=True,
        # )
        # stdout, _ = await my_stuff.communicate()
        # jdat = Edict(**json.loads(stdout.decode().strip()))
        jdat = Edict(**json.loads(self._gh.get_repo_info(owner=o, repo=r)))

        return (
            f"""
🕒[underline white]:[/] [cyan]{jdat.createdAt}[/]
🌐[underline white]:[/] [cyan]{jdat.url}[/]

📦[underline white]:[/] [cyan]{jdat.name}[/]
📝[underline white]:[/] [cyan]{jdat.description}[/]

🔱[underline white]:[/] [cyan]{jdat.forkCount}[/]   👀[underline white]:[/] [cyan]{jdat.watchers.totalCount}[/]   ⭐[underline white]:[/] [cyan]{jdat.stargazerCount}[/]   ❗[underline white]:[/] [cyan]{jdat.issues.totalCount}[/]   🔗[underline white]:[/] [cyan]{jdat.pullRequests.totalCount}[/]
    """,
            data,
        )

    def get_issues(self, o, r):
        data = json.loads(self._gh.get_issues(owner=o, repo=r))
        mydoc = []
        open_i = closed_i = 0

        for datum in data:
            d = Edict(**datum)
            if d.closed:
                closed_i += 1
            else:
                open_i += 1
                us = d.updatedAt if d.get("updatedAt", False) else False
                _us = (
                    datetime.fromisoformat(d.updatedAt.replace("Z", "+00:00"))
                    if us
                    else None
                )
                updated = (
                    _us.strftime("%a{c} %b %d{c} %Y {at} %I:%M%p").format(
                        c="[yellow],[/]", at="[cyan]@[/]"
                    )
                    if us
                    else ""
                )

                cs = datetime.fromisoformat(d.createdAt.replace("Z", "+00:00"))
                _cs = date(cs.year, cs.month, cs.day)

                now = datetime.now()
                _ns = date(now.year, now.month, now.day)
                age = f"[red]{(_ns - _cs).days:4d}[/] days"

                mydoc.append((d.number, d.author.name, age, updated, d.title))

        richTxt = f"🌐[underline]:[/] {len(data)}   🟢[underline]:[/] {open_i}   🔒[underline]:[/] {closed_i}\n"

        return (richTxt, mydoc)
