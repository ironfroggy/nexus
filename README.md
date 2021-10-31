# Nexus
A casual decentralized storage solution.

## What is Nexus?
A Python library and a command-line tool for storing data in a format safe for automatically synced filesystems like Dropbox, OneDrive, and GDrive.

### Why is Nexus?
I want to solve a combination of problems that all have good solutions, and many solutions solve some subset of these problems, but no good solution exists for **all** these problems together.

Nexus could solve these problems in one solution:
* Store structured data for users without a centralized server.
* Syncronizing data between multiple computers.
* Keep a history of versions of data over time.
* Easily useable by applications without running a local server.

### What solutions aren't good enough?

Traditional databases require running resource-hogging servers for applications to connect to. These are unnecessarily expensive and antagonistic to users.

Local-file databases like SQLite or bespoke data formats avoid a server, but they're stuck on one machine. If you want to use the same data on more than one machine, you can't safely keep it in a shared drive without causing corruption. If you edit data one more than one machine around the same time, you'll get two conflicting versions of the file.

Some "NoSQL" solutons are really good at allowing multiple copies of data, like CouchDB or simliar efforts. These still require some kind of service running that regular users can't and shouldn't be expected to manage.

## How to Use

The Nexus command line currently has a small set of basic operations.
* set
* get
* find

To write data to a Nexus database, the `set` operation will write one or more key/value pairs to a record. The record will be updated or created if it is new.

### The `set` operation

```bash
nexus {File-Path} set {Record-ID} {key}={value} ...more key/value pairs... 
```

Example creating a `todo-1` record:

```bash
nexus todo.nexus set todo-1 task="Learn how to use Nexus" completed=0
```

Example updating the same `todo-1` record, specifying only the changed data:

```bash
nexus todo.nexus todo-1 completed=1
```

### The `get` operation

```bash
nexus {File-Path} get {Record-ID} {key} ...{more keys}...
```

Example checking previous "to do" database for a task's status:

```bash
> nexus todo.nexus get todo-381 completed
1
```

### The `find` operation

```bash
nexus {File-Path} set {Record-ID} {key}={value} ...more key/value pairs...
```

The `find` operation does two useful things: locate record IDs that matxh a given prefix and bulk-get values from all matching records at once.

Example reading your todo list:

```bash
> nexus todo.nexus find todo text completed
todo-1  test nexus some more    0
todo-3  Explain how Nexus works 1
```

## Data Syncing

How does Nexus sync work? Nexus itself has no server, doesn't talk to other machines, and really has no way of inter-communicated. Yet it is still capable of sync between machines.

If a Nexus database, which is just a simple directory on your harddrive, is put in a syncronized folder then multiple computers can read and write the same database and share updates. This will not cause any conflict like would happen if you saved the same file on two machines and then tried to let Dropbox sync them.

The latest change made will win.

More advanced merging rules may be added in the future.

### How Does Sync Work?

Nexus databases are just simple directories.

Inside a Nexus database exists a file for the current machine and a file for each other machine that has ever written to the database. Each computer writes to a different file, but when reading data everything is combined. In this way, Nexus can safely be synced while still appearing as one coherent storage mechanism.
