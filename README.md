# Sample Flask application for Cloud Foundry
## About this application
This is a sample application to deploy Flask application for Cloud Foundry (CF).
The contents is based on repository [yuta-hono/flask-cloudfoundry-sample](https://github.com/yuta-hono/flask-cloudfoundry-sample).

Please see blog post ["Create simple Flask REST API using Cloud Foundry"](https://blogs.sap.com/2018/12/12/create-simple-flask-rest-api-using-cloud-foundry/) for further detail.

## Environment to run
- Cloud Foundry (Diego) or the version which Buildpack available

## How to run
1. select cf api url

```
cf api <your api URL>
```

2. login to your space
```
cf login
```

3. Push your application to CF from directory of your application on local PC
```
cf push <your application name>
```


## Files

### Files to declare runtime envinronment

#### requirements.txt
Pip requirements, this automatically satisfied by CF in a staging phase.
There is only "Flask" in the file.
You can add libraries here.

#### runtime.txt
The file specifies Python version to run this application by CF.
See more details at [Python Buildpack](https://docs.cloudfoundry.org/buildpacks/python/index.html "Python Buildpack").
Here I used "python-3.6.6", which is the latest python version of python buildpack on SAP CF as of 2018/12/12.
[Here](https://github.com/cloudfoundry/python-buildpack/releases/tag/v1.6.20) is supported python version for Python Buildpack 1.6.20.

#### manifest.yml
The file specifies about the specs of instance (memory/disk quota, etc).

#### Procfile
The file specify what commands run the application.
For more details, see at [About Procfiles](https://docs.cloudfoundry.org/buildpacks/prod-server.html#procfile).


### Web application files

#### hello.py
The simple Flask application run on CF.
Important things here are:

- App `host` requires to be set as "0.0.0.0"
  - CF routes the traffic from external in the router, and since all the component is scalable, CF can not restrict the access with source IPs 
- App `port` requires to be set with dynamic value comes from CF envinronmental value
  - Since the port is dynamic value, an application can not specify a static port number. This port number requires to be set with dynamic value also
