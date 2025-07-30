import sys
import traceback
from pathlib import Path
from queue import Queue
from typing import Optional, Any

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.omega_agent.napari_bridge import _get_viewer_info
from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.omega_agent.tools.generic_coding_instructions import (
    omega_generic_codegen_instructions,
)
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.python.consolidate_imports import consolidate_imports
from napari_chatgpt.utils.python.dynamic_import import execute_as_module
from napari_chatgpt.utils.python.exception_description import exception_description
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard
from napari_chatgpt.utils.python.fix_bad_fun_calls import fix_all_bad_function_calls
from napari_chatgpt.utils.python.fix_code_given_error import (
    fix_code_given_error_message,
)
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.python.missing_packages import required_packages
from napari_chatgpt.utils.python.pip_utils import pip_install
from napari_chatgpt.utils.python.required_imports import required_imports
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.system.information import system_info


class BaseNapariTool(BaseOmegaTool):
    """
    A base tool that delegates to execution to a sub-LLM and communicates with napari via queues.
    This tool is designed to generate and execute Python code in the napari environment.
    It can be used to create widgets, run code, and interact with the napari viewer.
    """

    def __init__(
        self,
        name: str = "<NAME>",
        description: str = "Enter Description Here",
        code_prefix: str = "",
        instructions: str = omega_generic_codegen_instructions,
        prompt: str = None,
        to_napari_queue: Queue = None,
        from_napari_queue: Queue = None,
        llm: LLM = None,
        return_direct: bool = False,
        save_last_generated_code: bool = True,
        fix_imports: bool = True,
        install_missing_packages: bool = True,
        fix_bad_calls: bool = False,
        verbose: bool = False,
        notebook: Optional[JupyterNotebookFile] = None,
        last_generated_code: Optional[str] = None,
        **kwargs: dict,
    ):
        """
        Initialize the tool.
        Parameters
        ----------
        name: str
            The name of the tool, must be unique.
        description: str
            The description of the tool, must be unique.
        code_prefix: str
            A prefix to prepend to the generated code, useful for imports or other necessary code.
        instructions: str
            Instructions for the sub-LLM, can be used to guide the code generation.
        prompt: str
            The prompt to use for the sub-LLM, if None, the tool will not delegate to a sub-LLM.
        to_napari_queue: Queue
            The queue to send the generated code to napari for execution.
        from_napari_queue: Queue
            The queue to receive the response from napari after executing the code.
        llm: LLM
            The LLM to use for code generation, if None, the tool will not delegate to a sub-LLM.
        return_direct: bool
            If True, the tool will return the generated code directly, otherwise it will send it to napari.
        save_last_generated_code: bool
            If True, the tool will save the last generated code for reference in future calls.
        fix_imports: bool
            If True, the tool will attempt to fix missing imports in the generated code.
        install_missing_packages: bool
            If True, the tool will attempt to install any missing packages required by the generated code.
        fix_bad_calls: bool
            If True, the tool will attempt to fix bad function calls in the generated code.
        verbose: bool
            If True, the tool will print additional information about the process.
        last_generated_code: str
            The last generated code, if any, to be used for reference in the prompt.
        kwargs: dict
            Additional keyword arguments, not used in this tool but can be used for future extensions.
        """

        super().__init__(name=name, description=description, **kwargs)

        self.code_prefix = code_prefix
        self.instructions = instructions
        self.prompt = prompt
        self.to_napari_queue = to_napari_queue
        self.from_napari_queue = from_napari_queue
        self.llm = llm
        self.return_direct = return_direct
        self.save_last_generated_code = save_last_generated_code
        self.fix_imports = fix_imports
        self.install_missing_packages = install_missing_packages
        self.fix_bad_calls = fix_bad_calls
        self.verbose = verbose
        self.last_generated_code = last_generated_code

        self.notebook = notebook

        self._installed_package_list = installed_package_list()

    def run_omega_tool(self, query: str = "") -> Any:
        """Use the tool."""

        if self.prompt:
            # Instantiate message

            if self.last_generated_code:
                last_generated_code = ("**Previously Generated Code:**\n",)
                last_generated_code += (
                    "Use this code for reference, usefull if you need to modify or fix the code. ",
                    "IMPORTANT: This code might not be relevant to the current request or task! "
                    "You should ignore it, unless you are explicitely asked to fix or modify the last generated widget!",
                    "```python\n",
                    self.last_generated_code + "\n",
                    "```\n",
                )
            else:
                last_generated_code = ""

            # Adding information about packages and Python version to instructions:
            filled_generic_instructions = omega_generic_codegen_instructions.format(
                python_version=str(sys.version.split()[0]),
                packages=", ".join(self._installed_package_list),
            )

            # Prepend generic instructions to tool specific instructions:
            instructions = filled_generic_instructions + self.instructions

            # Variable for prompt:
            variables = {
                "input": query,
                "instructions": instructions,
                "last_generated_code": last_generated_code,
                "viewer_information": "For reference, below is information about the current state of the napari viewer: \n"
                + _get_viewer_info(),
                "system_information": "For reference, below is information about the current system: \n"
                + system_info(add_python_info=False),
            }

            # call LLM:
            result = self.llm.generate(
                prompt=self.prompt,
                # system='',
                variables=variables,
            )

            # Get code from result:
            code = "\n\n".join([m.to_plain_text() for m in result])

            aprint(f"code:\n{code}")
        else:
            # No code generated because no sub-LLM delegation, delegated_function has the business logic.
            code = None

        # Update last generated code:
        if self.save_last_generated_code:
            self.last_generated_code = code

        # Setting up delegated function:
        delegated_function = lambda v: self._run_code(query, code, v)

        # Send code to napari:
        self.to_napari_queue.put(delegated_function)

        # Get response:
        response = self.from_napari_queue.get()

        if isinstance(response, ExceptionGuard):
            exception_guard = response
            # raise exception_guard.exception
            return f"Error: {exception_guard.exception_type_name} with message: '{str(exception_guard.exception)}' while using tool: {self.__class__.__name__} ."

        return response

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """
        This is the code that is executed, see implementations for details,
        must return 'Success: ...' if things went well, otherwise it is failure!
        """
        raise NotImplementedError("This method must be implemented")

    def _prepare_code(
        self,
        code: str,
        markdown: bool = True,
        do_fix_imports: bool = True,
        do_fix_bad_calls: bool = True,
        do_install_missing_packages: bool = True,
    ) -> str:

        with asection(f"NapariBaseTool: _prepare_code(markdown={markdown}) "):

            with asection(f"code to prepare:"):
                aprint(code)

            # extract code from markdown:
            if markdown:
                code = extract_code_from_markdown(code)

            # Prepend prefix:
            code = self.code_prefix + code

            # Add spaces around code:
            code = "\n\n" + code + "\n\n"

            if self.fix_imports and do_fix_imports:
                # Are there any missing imports?
                imports = required_imports(code, llm=self.llm)

                # prepend missing imports:
                code = "\n".join(imports) + "\n\n" + code

                # consolidate imports:
                code = consolidate_imports(code)

                # notify that code was modified for missing imports:
                code = "# Note: code was modified to add missing imports:\n" + code

            # Fix code, this takes care of wrong function calls and more:
            if self.fix_bad_calls and do_fix_bad_calls:
                code, fixed, _ = fix_all_bad_function_calls(code)

                if fixed:
                    # notify that code was fixed for bad calls:
                    code = (
                        "# Note: code was modified to fix bad function calls.\n" + code
                    )

            # Remove any offending lines:
            code = filter_lines(
                code,
                [
                    "napari.Viewer(",
                    "= Viewer(",
                    "gui_qt(",
                    "viewer.window.add_dock_widget(",
                ],
            )

            with asection(f"code after all preparations and fixes:"):
                aprint(code)

            if self.install_missing_packages and do_install_missing_packages:
                # Are there missing libraries that need to be installed?
                packages = required_packages(code, llm=self.llm)

                # Install them:
                pip_install(packages)

                # Notify that some packages might be missing and that Omega attempted to install them:
                code = (
                    f"# Note: some packages ({','.join(packages)}) might be missing and Omega attempted to install them.\n"
                    + code
                )

            # Return fully prepared and fixed code:
            return code

    def _run_code_catch_errors_fix_and_try_again(
        self, code, viewer, error: str = "", instructions: str = "", nb_tries: int = 3
    ) -> str:

        try:
            with asection(f"Running code:"):

                # Run the code:
                aprint(f"Code:\n{code}")
                captured_output = execute_as_module(code, viewer=viewer)

                # Call the activity callback. At this point we assume the code is correct because it ran!
                self.callbacks.on_tool_activity(self, "coding", code=code)

                # Come up with a filename:
                filename = f"generated_code_{self.__class__.__name__}.py"

                # Add the snippet to the code snippet editor:
                from napari_chatgpt.microplugin.microplugin_window import (
                    MicroPluginMainWindow,
                )

                MicroPluginMainWindow.add_snippet(filename=filename, code=code)

                # Add successfully run code to notebook:
                if self.notebook:
                    self.notebook.add_code_cell(code)
                aprint(f"This is what the code returned:\n{captured_output}")

        except Exception as e:
            if nb_tries >= 1:
                traceback.print_exc()
                description = error + "\n\n" + exception_description(e)
                description = description.strip()
                fixed_code = fix_code_given_error_message(
                    code=code,
                    error=description,
                    instructions=instructions,
                    viewer=viewer,
                    llm=self.llm,
                    verbose=self.verbose,
                )
                # We try again:
                return self._run_code_catch_errors_fix_and_try_again(
                    fixed_code, viewer=viewer, error=error, nb_tries=nb_tries - 1
                )
            else:
                # No more tries available, we give up!
                raise e

        return captured_output


def _get_delegated_code(name: str, signature: bool = False):
    with asection(f"Getting delegated code: '{name}' (signature={signature})"):
        # Get current package folder:
        current_package_folder = Path(__file__).parent

        # Get package folder:
        package_folder = Path.joinpath(current_package_folder, f"napari/delegated_code")

        # file path:
        file_path = Path.joinpath(package_folder, f"{name}.py")
        aprint(f"Filepath: {file_path}")

        # code:
        code = file_path.read_text()

        # extract signature:
        if signature:
            aprint("Extracting signature!")
            splitted_code = code.split("### SIGNATURE")
            code = splitted_code[1]

        return code
