# gbdxrun

Extension to DigitalGlobe/gbdxtools to provide local workflow execution.

## Known compatibility issues

The input port directories must be mounted to the Docker container, However string input ports are written to the parent dir `/mnt/work/input`, which cannot be mounted if the childs are already mounted. At least this was the case at the time of writing the code.

As a work around, all string input ports are provided to the Docker container as Env Vars with a prefix `gbdx-input-port-<port_name>=<port_value>`. So any task executed with gbdxrun, must be able to fetch string input ports from env vars. For example, the [GBDXTaskInterface](https://github.com/TDG-Platform/gbdx-task-interface):

```python
    def __init__(self, work_path="/mnt/work/"):

    >>> above not shown for clarity <<<

    string_input_ports = os.path.join(self.__work_path, 'input', "ports.json")
    if os.path.exists(string_input_ports):
        with open(string_input_ports, 'r') as f:
            self.__string_input_ports = self.load_json_string_inputs(f)
    else:
        self.logger.info("Input port file doesn't exist: %s, load from ENV VARS" % string_input_ports)
        self.__string_input_ports = self.load_env_string_inputs()

    @staticmethod
    def load_json_string_inputs(file_obj):
        """
        Load all string values from the json file
        Note: ENVI requires lists and dictionarys as well as literal types.
            So each value should also be parsed.

        """
        string_inputs = json.load(file_obj)

        for key, value in string_inputs.iteritems():
            try:
                # Try to load the value
                string_inputs[key] = json.loads(value)
            except (TypeError, ValueError):
                # If it fails, do nothing.
                pass

        return string_inputs

    @staticmethod
    def load_env_string_inputs():
        # Allow string ports to be stored as env vars
        env_var_ports = {}
        for key, value in os.environ.iteritems():
            if key.startswith('gbdx-input-port-'):
                try:
                    # Try to parse to JSON first, for dict and list which will be str -> json.dump'd
                    env_var_ports[key[len('gbdx-input-port-'):]] = json.loads(json.loads(value))
                except ValueError as e:
                    # If the above fails, then the value is a string (not an embedded dict or list)
                    value = json.loads(value)
                    value = True if value == 'True' else value
                    value = False if value == 'False' else value
                    env_var_ports[key[len('gbdx-input-port-'):]] = value

        return env_var_ports
```

## Usage example

Install

```
pip install git+https://github.com/michaelconnor00/gbdxrun.git
```

Run a gbdxtools script

```
from gbdxrun import gbdx

task = gbdx.Task("Mytask")

wf = gbdx.Workflow([task])

wf.savedata(
    task.outputs.envi_task_definitions,
    location='some/dir/path'
)

wf.execute()
```

Run a gbdxtools script with a local task definition

``` python
from gbdxrun import gbdx
import time
import json

# set task_definition
fp = '<FILEPATH_TO_TASK_DEFINITION.JSON>'
with open(fp) as json_data:
    defn = json.load(json_data)
keywords = {'task_definition':defn}

task = gbdx.Task("ENVI_CastRaster",**keywords)
task.inputs.input_raster = 'some/dir/path'
task.inputs.data_type = "float"
wf = gbdx.Workflow([task])

wf.savedata(task.outputs.output_raster_uri, location='some/dir/path')

print('Workflow ID: %s', wf.execute())

while not wf.complete:
    time.sleep(20)

print('Workflow Complete')
```

Then it can be executed from a terminal by running the script (below), or you can use iPython or Jupyter to run the workflow interactively.

```
> python myscript.py
```

Once the workflow is executed, you will see each task's stdout/stderr appear in you console/shell/browser.

## Development

### Contributing

Please contribute! Please make pull requests directly to master. Before making a pull request, please:

* Ensure that all new functionality is covered by unit tests.
* Verify that all unit tests are passing. `TODO use travis to run tests on PRs.`
* Ensure that all functionality is properly documented. `TODO use mkdocs or sphinx to generate docs for readthedocs.org`
* Fix all versions in setup.py
* Update the Changelog with the new features, bug fixes, etc.

### Run Tests

> TO COME ...

### Create a new version

To create a new version (after all tests have passed and PR is merged):

```
bumpversion ( major | minor | patch )
git push --tags
```

Versioning is according to [Symantic Versioning](http://semver.org/) system.
