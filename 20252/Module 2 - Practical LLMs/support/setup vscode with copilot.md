## Setup VSCode and Copilot

### 1. Install Python

* Download and install Python from [python.org/downloads](https://www.python.org/downloads/).
* During installation, make sure to check **“Add Python to PATH”**.
* Verify installation by running in a terminal:

  ```
  python --version
  ```

---

### 2. Install Visual Studio Code

* Download and install VS Code from [code.visualstudio.com](https://code.visualstudio.com/).

---

### 3. Install Required VS Code Extensions

Open VS Code, press **Ctrl+Shift+X** (or **Cmd+Shift+X** on macOS), and install these extensions:

1. **Python** (by Microsoft)
2. **Jupyter** (by Microsoft)
3. **GitHub Copilot**
4. **GitHub Copilot Chat** (optional, but useful for in-editor chat help)

---

### 4. Install Jupyter Tools in Python

In a terminal or the VS Code terminal, run:

```
pip install notebook ipykernel jupyter
```

---

### 5. Create a GitHub Account

* Go to [github.com](https://github.com/) and create an account.
* You can use your Google account to sign up.

---

### 6. Connect VS Code to GitHub Copilot

* In VS Code, open the Command Palette (**Ctrl+Shift+P**) and run:

  ```
  GitHub: Sign in
  ```
* Follow the prompts to sign in to your GitHub account.
* Make sure your GitHub account has Copilot access (subscription or free trial).

---

### 7. Open and Run a Notebook

* Create a new file in VS Code with the extension `.ipynb`.
* When prompted, select your installed Python as the **kernel**.
* Add and run a simple test cell:

  ```python
  print("Hello from Python notebook with Copilot!")
  ```
* Press **Shift + Enter** to run the cell.

---

### 8. Enable Copilot in Notebooks

If Copilot suggestions don’t appear inside notebook cells:

* Open VS Code settings (**Ctrl+,**).
* Search for “Copilot” and make sure **Copilot: Enable for Notebooks** is turned on.

or 

* Open a Jupyter notebook (`.ipynb`) in VS Code.
* Click the **Copilot icon** in the bottom-right status bar.
* Make sure “Enable Copilot in Notebooks” is turned on.
---

### Copilot Chat

You can open the Copilot Chat panel using **Ctrl+I** or by clicking the chat icon in the sidebar.

You can ask Copilot questions such as:

* “Explain this cell.”
* “Optimize this code.”
* “Why am I getting a KeyError?”
* “Generate code to visualize null values in this dataset.”

You can also highlight a section of code, right-click, and choose:
**Ask Copilot → Explain / Fix / Optimize Selection**

---

### Generating Code from Prompts

Inside a code cell:

```python
# generate python code to train a decision tree classifier on the iris dataset
```

Press **Enter**, and Copilot will produce the full implementation.

---

### Data Science-Specific Examples

| Task                      | Example Prompt                                                                   |
| ------------------------- | -------------------------------------------------------------------------------- |
| Data Cleaning             | `# remove missing values and encode categorical columns`                         |
| Visualization             | `# plot feature importance of the trained model`                                 |
| Model Training            | `# train a logistic regression and evaluate using accuracy and confusion matrix` |
| Exploratory Data Analysis | `# summarize numerical columns and plot histograms`                              |

---

## 4. Controlling Copilot Behavior

Use the **Command Palette (Ctrl+Shift+P)** and search for:

* **Copilot: Enable/Disable**
* **Copilot: Open Chat**
* **Copilot: Explain This Code**

You can also control Copilot per language in:
`File → Preferences → Settings → GitHub Copilot`

---

## 5. Troubleshooting

| Issue                     | Solution                                                     |
| ------------------------- | ------------------------------------------------------------ |
| No suggestions appearing  | Ensure you are logged in and the extension is enabled        |
| Notebook kernel not found | Install Python and select the correct environment in VS Code |
| Chat not available        | Install the **GitHub Copilot Chat** extension                |
| High CPU usage            | Disable inline suggestions temporarily                       |

---

## 6. Example Workflow

Example of using Copilot during data analysis:

1. Type:

   ```python
   # load the Titanic dataset and preview it
   ```

   Copilot writes code using pandas.

2. Then type:

   ```python
   # visualize survival rate by gender
   ```

   Copilot writes the seaborn code.

3. Then type:

   ```python
   # train a random forest classifier and evaluate accuracy
   ```

   Copilot writes the complete model training and evaluation code.

This workflow makes it ideal for interactive teaching or guided lab sessions.

---

## 7. Recommended Settings

In your `settings.json` file (open via **Ctrl+Shift+P → Preferences: Open Settings (JSON)**):

```json
{
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": true,
    "notebook": true
  },
  "editor.inlineSuggest.enabled": true
}
```

---
