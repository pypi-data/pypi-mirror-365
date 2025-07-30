# wbpUFO

UFO plugin for [Workbench](https://pypi.org/project/wbBase/) applications.

This plugin provides Workbench document templates for fonts in UFO source format:

As well as a document view to view and edit fonts in these formats. 


## Installation

```shell
pip install wbpUFO
```

Installing this plugin registers an entry point 
in the group "*wbbase.plugin*" named "*ufo*".

To use the plugin in your application, 
add it to your *application.yml* file as follows:
```yaml
AppName: myApp
Plugins:
- Name: ufo
```

## Documentation

For details read the [Documentation](https://workbench2.gitlab.io/workbench-plugins/wbpUFO).