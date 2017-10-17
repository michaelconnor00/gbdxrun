import os
import traceback
import uuid
import tempfile
import shutil
from toposort import toposort

from gbdxrun import local_task


class LocalWorkflowError(Exception):
    pass


class LocalWorkflow(object):

    def __init__(self, tasks, **kwargs):
        self.name = kwargs.get('name', str(uuid.uuid4()))
        self.id = None

        self.definition = None

        self.tasks = tasks

        # Create Temporary directory for workflow outputs
        self.temp_output_dir = os.path.realpath(tempfile.mkdtemp())

        self.verbose = False

    def execute(self):
        """
        Sort tasks based on dependencies, then execute each.
        """
        # sorted_tasks = self._sort_tasks(self.tasks)
        sorted_tasks = self.tasks

        if self.verbose:
            print('Output Root: %s' % self.temp_output_dir)

        try:
            for task in sorted_tasks:
                try:
                    task.execute(self.temp_output_dir)
                except KeyboardInterrupt:
                    task.stop()
                    break

                if not task.success:
                    print('Task failed: %s' % task.reason)
                    break
                else:
                    print('Task Status: %s' % task)
        except Exception:
            traceback.print_exc()
        finally:
            shutil.rmtree(self.temp_output_dir)

    def savedata(self, output, location):
        """
        Save the location as the ports value.
        :param output: Port object
        :param location: path where output is to be written
        """
        if location is None:
            raise LocalWorkflowError('Save data function must have a location')

        # Check if the directories exists, if not make where required.
        if self._exists(location):
            # It could be leftover from a previous execution, so remove and create new
            shutil.rmtree(location)
            os.makedirs(location)
            output.value = location
        if not self._exists(location) and self._exists(os.path.split(location)[0]):
            os.makedirs(location)
            output.value = location
        elif not self._exists(location) and not self._exists(os.path.split(location)[0]):
            raise LocalWorkflowError('Save data location for %s does not exist: %s' % (output.name, location))

    def workflow_skeleton(self):
        return {
            "tasks": [],
            "name": self.name
        }

    def generate_workflow_description(self):
        pass

    @staticmethod
    def _exists(path):
        return os.path.isabs(path) and os.path.isdir(path) \
            and not os.path.isfile(path)

    @staticmethod
    def _sort_tasks(task_list):
        """
        Take the list of tasks in any order and sort them topologically
        so the resulting list and be executed correctly.
        :param task_list: List of LocalTask objects
        :return: Sorted list of LocalTask objects
        """

        # Create a list of
        tasks_w_deps = {}
        for task in task_list:
            deps = []
            for port_name in task.inputs.portnames:
                port = task.inputs.__getattribute__(port_name)
                if isinstance(port.value, local_task.Directory):
                    if port.value.parent not in task_list:
                        raise LocalWorkflowError('Task %s is missing from workflow' % port.value.parent.type)
                    deps.append(port.value.parent)
            tasks_w_deps[task] = set(deps)

        sorted_list =[]
        for x in toposort(tasks_w_deps):
            sorted_list += list(x)

        return sorted_list
