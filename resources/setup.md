# Setting up (VS Code)

In this guide, we will set up the tools needed to follow the course and run the provided notebooks and Python code.

The instructions below are focused on Visual Studio Code (VS Code). Other development environments, such as PyCharm, provide similar functionality, so feel free to use another editor if you are already comfortable with it.

The goal of this guide is simple: by the end, you should have:

* Git installed and configured
* the repository fork on your laptop
* a suitable version of Python installed
* an active Python virtual environment for the course

If you are already familiar with these tools, feel free to use your preferred workflow. The important thing is that you end up with a working virtual environment containing all the required dependencies.

## Git

First thing first, the tutoring material is stored in a Git repository (but it will also be uploaded in the Teams, so do not worry). Git is a tool that allows us to keep track of changes to the course material and, more importantly for you, easily download the repository and keep it up to date.

### Installing Git

If Git is not already installed on your computer , download it from the official website:

[Git Download Page](https://git-scm.com/install/)

Follow the installation instructions for your operating system. In most cases, the default installation options are perfectly fine.

### Downloading the course repository

Once Git is installed, you need to clone the course repository. Cloning means creating a local copy of the repository on your computer.

First, open the repository page in your browser and copy its URL. To help you, here the URL:

[Repository URL](https://github.com/frekkoz3/Introduction-to-Artificial-Intelligence-2026-2027)

Then open a terminal and move to the folder where you want to keep the course:

```bash
cd path/to/where/you/want
```

And then just clone the repository:

```bash
git clone https://github.com/frekkoz3/Introduction-to-Artificial-Intelligence-2026-2027.git
cd Introduction-to-Artificial-Intelligence-2026-2027
```

Open the folder from VS Code (as simple as breathing!):

1. Open VS Code
2. Select File $\to$ Open Folder $\to$ Select from the GUI the folder where you just cloned the repository

That's it! (As I said, as simple as breathing! Or as simple as [taking up a blue chair from the ground](https://www.youtube.com/watch?v=u0GPQpAbTyw))

### Getting the updates every week

The repository will be updated during the course as new weeks, notebooks, exercises, and corrections are added.

You do not need to download the repository again every week. Instead, you can update your existing local copy using Git.

First, open the folder from VS Code. Open a terminal inside the course folder. Then just pull the weekly update with

```bash
git pull
```

This downloads the latest changes from the repository and updates your local copy.

I recommend doing this before starting each new week.

> **Important**: If you have modified files inside the repository, Git may prevent the update from being applied automatically. Don't worry if this happens. We will handle that.

VS Code as a native support for Git, so once everything is installed you could use also the **Source Control Extension** that you can find in the left most control panel to handle all these things.

## Python

I assume that most of you already have Python installed.

Use **Python 3.12.x** for this course. This matches the repository's default uv environment and is supported by the pinned dependencies. Python 3.8–3.11 cannot install the full dependency set.

If you do not have Python installed, you can download it from the official Python website:

[Python Downloads](https://www.python.org/downloads/).

## Virtual Environment

If you have already followed the [uv quick start](../README.md#quick-start-with-uv-and-jupyterlab), select the existing `.venv` through **Select Another Kernel → Python Environments**. Otherwise, follow the original environment creation steps below.

Make sure the Microsoft Python and Jupyter extensions are installed in VS Code.

And now we will see how to setup a the virtual enviornment!

We will use the **native VS Code virtual environment handler**.

So, to start: go tho the `notebooks` folder, then in the `lectures` subfolder. Here open the `0_setup.ipynb` notebook. From there, just follow step-by-step this intuitive visual guide.

![Step 1](./setup%20screen/0.png)
> In the right corner select the icon (you should see "Select Interpreter" or something like that)

![Step 2](./setup%20screen/1.png)
> Select the option "Select Another Kernel..."

![Step 3](./setup%20screen/2.png)
> Select the option "Python Environments..."

![Step 4](./setup%20screen/3.png)
> Select the option "+ Create Python Environment"

![Step 5](./setup%20screen/4.png)
> Select the option "venv Manages virtual environments created using 'venv'"

![Step 6](./setup%20screen/5.png)
> Select your preferred Python Interpreter (again I suggest **Python 3.12.x**)

![Step 7](./setup%20screen/6.png)
> Enter a name for your virtual environment. Goes with ".venv" or ".env"!

![Step 8](./setup%20screen/7.png)
> Select "Install project dependencies ..."

![Step 9](./setup%20screen/8.png)
> Select the `requirements.txt` file and proceed

And that's it!

VS Code will handle everything else from now on!

When you need to open a new notebooks you just select always from the icon in the right corner the virtual environment you have created and that's it.

Now it's time to begin! Good luck and have fun!
