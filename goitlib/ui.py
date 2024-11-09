# stdlib imports
import os
import copy
import json
import time
import asyncio
import logging
import functools
import subprocess
from datetime import date, datetime

# internal imports
from .edict import *
from .ghcli import *

# 3rd party imports
from rich.text import Text
from rich.markdown import Markdown
from textual.app import App
from textual.events import Key
from textual.message import Message
from textual.binding import Binding
from textual.widgets import Footer, Static, ListView
from textual.widgets import ListItem, Label, TabbedContent
from textual.widgets import TabPane, LoadingIndicator
from textual.widgets import DataTable
from textual.containers import Container, VerticalScroll
from textual.containers import ScrollableContainer


## Globals
md = """
[bold yellow]This       is         a        markdown        example[/]
:error: :error: :error:
:warning: :warning: :warning:
"""
repo_data = {}
GH = Edict(
    **{
        "repo_list": "gh repo list --json owner,name -L 1024",
        "org_list": "gh org list -L 1024 | grep -vE '(^ |Showing [0-9])'",
        "org_repos": "gh repo list --json name -L 1024 {o}",
    }
)


## Main app code
class GridApp(App):
    DP = DataPipeline()
    STAB = 0
    TABS = ["Overview", "Issues", "PullRequests", "Actions"]
    CSS = """
Screen { layout: grid; grid-size: 4 5; overflow: auto auto; }
Static { color: auto 100%; height: 100%; padding: 0 1; }
ListView { column-span: 1; row-span: 5; height: 100%; padding: 0; border: round grey; }
ListItem { padding: 0; height: auto; }
Label { width: auto; height: auto; overflow: auto auto; }
Text { width: auto; }

/* --------------------------------------- */

#orgs { row-span: 2; }
#repos { row-span: 5; height: 100%; }
.data-table-column { text-align: left; }
#main { border: round grey; height: 100%; min-width: 50%; width: 100%; row-span: 5; column-span: 4; }
"""
    BINDINGS = [
        ("O", "show_tab('overview')", "Overview"),
        ("I", "show_tab('issues')", "Issues"),
        ("P", "show_tab('pullrequests')", "PullRequests"),
        ("A", "show_tab('actions')", "Actions"),
    ]

    def _please_wait(self, name):
        if name.lower() == "overview":
            datum = (f"#{name}_md", Label)
        else:
            datum = (f"#{name}_dt", DataTable)

        self.render_tab(
            ("#main", TabbedContent),
            (f"#{name}", TabPane),
            (f"#{name}_data", Label),
            datum,
            ("[cyan]Please wait[/][underline]...[/]\n", ""),
            # get_issues(self.S_ORG, self.S_REPO),
        )

    def get_stub(self, o, r):
        return ("Stub\n", [])

    def get_overview(self, o=False, r=False):
        data = self.DP.get_overview(self.S_ORG, self.S_REPO)
        return (data[0], Markdown(data[1]))

    def action_show_tab(self, tab):
        lt = tab.lower()
        self._please_wait(tab)
        self.get_child_by_type(TabbedContent).active = tab
        datum = (f"#{lt}_dt", DataTable)

        if lt == "issues":
            cb = self.DP.get_issues
        elif lt == "pullrequests":
            cb = self.DP.get_pull_requests
        elif lt == "actions":
            cb = self.DP.get_actions
        elif lt == "overview":
            cb = self.get_overview
            datum = (f"#{lt}_md", Label)
        else:
            cb = self.get_stub

        self.render_tab(
            ("#main", TabbedContent),
            (f"#{lt}", TabPane),
            (f"#{lt}_data", Label),
            datum,
            cb(self.S_ORG, self.S_REPO),
        )

    def on_mount(self):
        orgs_l = self.query_one("#orgs", ListView)
        for org in repo_data.keys():
            orgs_l.append(ListItem(Label(org)))
        orgs_l.index = 0
        repos_l = self.query_one("#repos", ListView)
        repos_l.index = 0
        repos_t = copy.copy(repo_data[list(repo_data.keys())[0]])
        repos_t.sort()
        for repo in repos_t:
            repos_l.append(ListItem(Label(repo)))
        self.S_ORG = list(repo_data.keys())[0]
        self.S_REPO = repos_t[0]
        datas = {
            "pullrequests": ("Number", "Age", "State", "Author", "Title"),
            "issues": ("Issue", "Author", "Age", "Updated @", "Description"),
            "actions": ("Number", "Attempt", "Event", "Result", "Name"),
        }
        for tab in self.TABS:
            if tab.lower() != "overview":
                dt = self.query_one(f"#{tab.lower()}_dt", DataTable)
                dim = dt.size
                dt.add_columns(*datas[tab.lower()])
        self.post_message(Key("O", "O"))

    def on_list_view_selected(self, event):
        if event.list_view.id == "orgs":
            repos_l = self.query_one("#repos", ListView)
            repos_l.clear()
            repos_t = copy.copy(repo_data[str(event.item.query_one(Label).renderable)])
            repos_t.sort()
            self.S_ORG = str(event.item.query_one(Label).renderable)
            for repo in repos_t:
                repos_l.append(ListItem(Label(repo)))
        elif event.list_view.id == "repos":
            self.S_REPO = str(event.item.query_one(Label).renderable)
            self.post_message(Key("O", "O"))

    def render_tab(self, l1, l2, l3, l4, d):
        l1_q = self.query_one(*l1)
        l2_q = l1_q.query_one(*l2)
        l3_q = l2_q.query_one(*l3)
        l4_q = l2_q.query_one(*l4)
        l3_q.update(d[0])
        if isinstance(l4_q, Label):
            l4_q.update(d[1])
        elif isinstance(l4_q, DataTable):
            l4_q.clear()
            l4_q.add_rows(d[1])

    def compose(self):
        tabs = ["Overview", "Issues", "PullRequests", "Actions"]
        self.orgs_l = ListView(id="orgs")
        self.orgs_l.border_title = "Organizations"
        yield self.orgs_l

        with TabbedContent(*tabs, initial=tabs[0].lower(), id="main"):
            for tab in tabs:
                with TabPane(tab, id=tab.lower()):
                    yield Label(id=f"{tab.lower()}_data")
                    if tab.lower() == "overview":
                        yield VerticalScroll(
                            Label(id=f"{tab.lower()}_md"), id=f"{tab.lower()}_sc"
                        )
                    else:
                        yield VerticalScroll(
                            DataTable(
                                cursor_type="row",
                                zebra_stripes=True,
                                id=f"{tab.lower()}_dt",
                            ),
                            id=f"{tab.lower()}_sc",
                        )

        self.repos_l = ListView(id="repos")
        self.repos_l.border_title = "Repositories"
        yield self.repos_l

        yield Footer()


async def collect_data():
    retv = {}

    # run `gh repo list -L 1024`
    my_stuff = await asyncio.create_subprocess_shell(
        GH.repo_list,
        stdout=asyncio.subprocess.PIPE,
        shell=True,
    )
    stdout, _ = await my_stuff.communicate()
    for repo in json.loads(stdout.decode().strip()):
        owner = repo["owner"]["login"]
        name = repo["name"]
        if owner not in retv.keys():
            retv[owner] = []
        if name not in retv[owner]:
            retv[owner].append(name)

    # Run `gh org list` asynchronously
    orgs_process = await asyncio.create_subprocess_shell(
        GH.org_list,
        stdout=asyncio.subprocess.PIPE,
        shell=True,
    )
    stdout, _ = await orgs_process.communicate()
    orgs = stdout.decode().strip().split()

    # Loop over each organization and fetch repo data asynchronously
    for org in orgs:
        retv[org] = []

        # Run `gh repo list` asynchronously for each org
        repo_process = await asyncio.create_subprocess_shell(
            GH.org_repos.format(o=org),
            stdout=asyncio.subprocess.PIPE,
            shell=True,
        )
        repo_stdout, _ = await repo_process.communicate()

        # Parse JSON and add repository names to the result dictionary
        for r in json.loads(repo_stdout.decode().strip()):
            retv[org].append(r["name"])

    return retv


class AppSetup(App):
    def compose(self):
        yield LoadingIndicator()

    async def on_mount(self):
        asyncio.create_task(self.fetch_and_exit())

    async def fetch_and_exit(self):
        global repo_data
        repo_data = await collect_data()
        self.exit()
