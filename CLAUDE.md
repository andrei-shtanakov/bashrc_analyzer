### Concept: "Smart Linter" for `.bashrc`

The system will consist of two main parts:
1. **Analysis Core (Rule-Based Engine):** A fast rule-based engine that identifies the most common and obvious problems.
2. **AI Assistant (LLM Layer):** A language model-based layer that analyzes the core's output, adds context, explains problems in simple language, and suggests fixes.

---

### Step 1: Defining Common Problems (Knowledge Base for the Linter)

First, we need to compile a list of "anti-patterns" that we will look for.

**Category 1: Direct Path Management**
* **Problem:** `export PATH=...` or `export LD_LIBRARY_PATH=...` instead of `export PATH=...:$PATH`. The user might overwrite system paths.
* **Detector:** Looks for `PATH=` or `LD_LIBRARY_PATH=` without `$PATH` or `$LD_LIBRARY_PATH` on the right side.
* **AI Recommendation:** "You are completely overwriting the `PATH` variable. This can break basic system commands. You probably wanted to add a new path, not replace all existing ones. Use `export PATH=/your/path:$PATH`."

**Category 2: Using `module load` in `.bashrc`**
* **Problem:** `.bashrc` is executed for *every* new shell, including non-interactive ones (e.g., in `ssh host "command"` or UGE scripts). This slows down work and can cause conflicts. Modules are better loaded in `.bash_profile` or interactively.
* **Detector:** Looks for `module load` commands or `source /etc/profile.d/modules.sh`.
* **AI Recommendation:** "We found `module load` in your `.bashrc`. This file is executed every time a shell starts, which can slow down connections and cause problems in scripts. We recommend moving these commands to the `~/.bash_profile` file, which is executed only once at login."

**Category 3: Conda Activation**
* **Problem:** `conda activate my_env` or `source .../conda.sh` in `.bashrc` — this is one of the most common causes of conflicts with system libraries and modules. Conda aggressively changes `PATH` and other variables.
* **Detector:** Looks for `conda activate` or lines added by `conda init`.
* **AI Recommendation:** "Activating a Conda environment in `.bashrc` often leads to conflicts with system modules. Libraries from Conda can be replaced by system ones, leading to segmentation faults. We recommend activating the Conda environment manually in the terminal or at the beginning of your job script, *after* loading the necessary modules."

**Category 4: Conflicting Modules**
* **Problem:** Loading modules that are built with different toolchain versions and are incompatible with each other. For example, `module load GCC/9.3.0` and `module load GCC/12.3.0`.
* **Detector:** This is more complex. Requires a knowledge base about current toolchains on your cluster. The system should:
  1. Get a list of all toolchains.
  2. Compare them with a compatibility matrix (e.g., "cannot simultaneously load `GCC/12.3.0` and `foss/2018b`").
* **AI Recommendation:** "You are trying to load modules with different toolchains simultaneously. This can lead to unpredictable errors during compilation and execution. Please choose one toolchain for your task and load only the modules corresponding to it."

**Category 5: Hardcoded Paths**
* **Problem:** `export PATH=/home/user/my_software/bin:$PATH`. This software might be built with old libraries or simply be suboptimal.
* **Detector:** Looks for `export` with paths inside `/home` or `/scratch`.
* **AI Recommendation:** "You are adding a program installed in your home directory to PATH. If a system module exists for this program (`module avail my_software`), we recommend using it. System modules are built with the correct libraries and optimized for the cluster."

---

### Step 2: Tool Selection and Implementation

#### Option A: Loadable Module (Recommended for Start)

This is the simplest and most native approach for users.

**How it will work:**
1. User logs into the cluster.
2. Executes command: `module load tools/bashrc-checker`
3. Runs the check: `check-my-bashrc` or `check-my-bashrc ~/.bashrc`
4. Gets a report in the terminal.

**Technical Implementation:**
1. **Analyzer Script:** Write a Python script. This will be the system's core.
   * **Parsing:** Use the `bashlex` library for reliable parsing of `.bashrc` into individual commands. Simple `grep` won't handle conditional constructs, functions, etc.
   * **Rules:** Implement checks from Step 1 as functions.
   * **Cluster Context:** The script can execute `module avail` on the fly and parse the output to know which modules are available. The conflict matrix can be stored in a simple JSON or YAML file.
2. **AI Integration (LLM):**
   * Choose an API for LLM access (e.g., OpenAI API, Anthropic, or locally deployed model like Llama).
   * When an analyzer rule triggers, the script forms a prompt for the LLM.
   * **Example Prompt:**
     ```
     You are a friendly AI assistant for HPC cluster users.
     The user is a scientist, not always a Linux expert.
     Explain in simple terms why the following line in .bashrc is a bad idea, and suggest a better alternative.

     Problem context: Direct overwriting of LD_LIBRARY_PATH variable. This breaks the dynamic linker.
     Problematic line: export LD_LIBRARY_PATH=/opt/my_libs/lib

     Your answer should be short, clear, and contain a corrected example.
     ```
3. **Module Creation:**
   * Write a simple `modulefile` for `tools/bashrc-checker` that adds the directory with your Python script to `PATH`.

**Python Code Example (pseudocode):**
```python
import bashlex
import subprocess
import openai # or other LLM client

# Settings
openai.api_key = '...'
CONFLICT_MATRIX = {
    "compilers": ["gcc", "intel", "pgi"],
    # ... other rules
}

def check_path_overwrite(command_node):
    if "PATH=" in command_node.word and "$PATH" not in command_node.word:
        return "Direct PATH overwrite detected. This is dangerous."
    return None

def get_ai_explanation(problem_description, code_line):
    prompt = f"""You are an AI assistant for scientists on an HPC cluster. 
    Explain the problem in simple terms and suggest a solution.
    Problem: {problem_description}
    Code line: {code_line}"""
    
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

def main(bashrc_path):
    with open(bashrc_path, 'r') as f:
        content = f.read()

    parts = bashlex.parse(content)
    for node in parts:
        if node.kind == 'command':
            # Example simple check
            problem = check_path_overwrite(node)
            if problem:
                line_text = bashlex.ast.node_to_string(node)
                explanation = get_ai_explanation(problem, line_text)
                print(f"⚠️ Potential problem found in line: {line_text}")
                print(f"🤖 AI assistant says: {explanation}\n")

if __name__ == "__main__":
    main("~/.bashrc")
```

#### Option B: Web Form

More user-friendly, but requires more infrastructure.

**Technical Implementation:**
1. **Backend:** Web server on Flask or FastAPI (Python). It will contain the same analysis logic as in Option A. The backend will accept `.bashrc` text content through an API endpoint.
2. **Frontend:** Simple HTML page with a `textarea` for pasting code and a "Check" button. JavaScript will send content to the backend and nicely display the received report (e.g., highlighting problematic lines).
3. **Cluster Context:** The backend needs access to module information. Solution: set up a cron job on the cluster that exports `module avail` and the conflict matrix to a file accessible to the web server once a day.

### Recommended Implementation Plan

1. **MVP (Minimum Viable Product):** Create a **terminal tool (Option A)**, but **without AI**. Implement 3-5 most important rules (PATH overwrite, `conda activate`, `module load` in `.bashrc`). Output — simple formatted text. This will already provide 80% of the benefit. The running script without parameter checks user's `($HOME)/.bashrc`. The script can have one parameter - path to some other `.bashrc` file (the file name included and can be different with `.bashrc`).
2. **Phase 2 (AI Integration):** Connect LLM to the terminal tool for generating explanations. This will make the tool much more user-friendly.
3. **Phase 3 (Expansion):** Add more rules, create a knowledge base about module compatibility.
4. **Phase 4 (GUI):** If there's demand from users, create a **web interface (Option B)** that will use the already debugged backend analyzer.

This approach will allow you to quickly get a working prototype and gradually build up its functionality, making life for scientists on the cluster easier and safer.

## Step 1 is done.
## Now make Step 2. Connect to Generative Model for generating explanations. This will make the tool much more user-friendly. 

**A few tips:**
* Use the API keys for Claude and Chat-GPT.
* Pass API keys to the program via environment variables.
* After displaying the results of Step 1, ask the user in the terminal which LLM to use and then transfer the file `.bashrc` and the results of the preliminary analysis.
* Also, the result can be output in two versions, either just recommendations and LLM, or output.bashrc file with highlighting of problematic lines and comments under them.


