# wsgi-to-zpm
## Generate InterSystems ZPM/IPM module.xml from an existing WSGI project.

`wsgi-to-zpm` was created to help quickly create (or modify) an InterSystems [ZPM/IPM](https://github.com/intersystems/ipm/wiki) module.xml for an existing Python WSGI web application.  This allows you to easily publish/distribute WSGI apps to InterSystems IRIS instances using zpm.

### InterSystems Developer Tools Contest 2025
`wsgi-to-zpm` was originally created/published for the [InterSystems Developer Tools Contest 2025](https://community.intersystems.com/post/intersystems-developer-tools-contest-2025).

## Description

[ZPM/IPM](https://github.com/intersystems/ipm/wiki) makes it very easy to install and configure various software and packages for InterSystems IRIS instances.  The `module.xml`  file is used to configure a ZPM package for distribution (See the [ZPM Wiki](https://github.com/intersystems/ipm/wiki/03.-IPM-Manifest-(module.xml))).  `wsgi-to-zpm` can be used to either quickly generate a `module.xml` or modify an existing `module.xml` to include any Python WSGI web applications it finds in your current directory.

## Prerequisites
- IRIS 2024.1+ (for WSGI Web Application support)
- Python 3 installed on the system

## Installation

Install via pipx:
```bash
pipx install wsgi-to-zpm
```
## Usage

Assume you have a directory with the following Flask app:

```
/home/user/Projects/my-wsgi-app
├── my-webapp/
│   ├── myapp.py
│   ├── templates/
│   │   ├── hello.html
│   └── static/
│       └── style.css
└── requirements.txt
```

To generate a `module.xml`, run `wsgi-to-zpm`:

![Image: Running wsgi-to-zpm](./docs/my-wsgi-app.gif)

Depending on your responses, something like the following lines will be added to a `module.xml`:

```xml
<Export generator="Cache" version="25">
  <Document name="my-webapp.ZPM">
    <Module>
    ...
      <FileCopy Name="my-webapp/" Target="${cspDir}my-webapp"/>

      <WebApplication Url="/my-webapp"
        AutheEnabled="32"
        Description=""
        MatchRoles=":${globalsDbRole}"
        NameSpace="${ns}"
        WSGIAppLocation="${cspDir}my-webapp"
        WSGIAppName="myapp"
        WSGICallable="app"
        DispatchClass="%SYS.Python.WSGI"/>
    ...
    </Module>
  </Document>
</Export>
```

## Installing Your WSGI App Via ZPM

### Demo Setup
Note: If you would like to try out this process from a Docker image, follow these steps:

```bash
git clone https://github.com/intersystems-community/intersystems-iris-dev-template.git
cd intersystems-iris-dev-template
docker compose up -d
```
Once the Docker image is up and running, you can copy the `my-wsgi-app` directory to intersystems-iris-dev-template/ and log into the Docker container with bash.

```bash
# From intersystems-iris-dev-template directory
cp -r ~/Project/my-wsgi-app ./

# Connect to the Docker container to run ZPM
docker exec -it intersystems-iris-dev-template-iris-1 bash
```

### Running ZPM
Now that you have a `module.xml`, you are able to load this WSGI app as a zpm package.


```cls
irisowner@bea89444b155:~/dev$ iris terminal IRIS

Node: bea89444b155, Instance: IRIS

USER>zn "IRISAPP"

IRISAPP>zpm

=============================================================================
|| Welcome to the Package Manager Shell (ZPM). Version:                    ||
|| Enter q/quit to exit the shell. Enter ?/help to view available commands ||
|| Current registry https://pm.community.intersystems.com                  ||
=============================================================================
zpm:IRISAPP>load ~/dev/my-wsgi-app

[IRISAPP|my-webapp]	Reload START (/home/irisowner/dev/my-wsgi-app/)
[IRISAPP|my-webapp]	requirements.txt START
[IRISAPP|my-webapp]	requirements.txt SUCCESS
[IRISAPP|my-webapp]	Reload SUCCESS
[my-webapp]	Module object refreshed.
[IRISAPP|my-webapp]	Validate START
[IRISAPP|my-webapp]	Validate SUCCESS
[IRISAPP|my-webapp]	Compile START
[IRISAPP|my-webapp]	Compile SUCCESS
[IRISAPP|my-webapp]	Activate START
[IRISAPP|my-webapp]	Configure START
[IRISAPP|my-webapp]	Configure SUCCESS
[IRISAPP|my-webapp]	Activate SUCCESS
zpm:IRISAPP>
```

Visiting the URL **http://[host]:[port]/my-webapp/** will now serve your WSGI app:

![Image: Served WSGI App](./docs/wsgi-app.png)
