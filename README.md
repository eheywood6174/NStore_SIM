**Welcome to NStore_SIM**

This repository contains a full set of NStore_SIM base scripts and a collection of test cases, all translated to Python (tested on version 3.11.9).
Below are a brief set of instructions to help you get started.

\
\
**What do I need to download?**

NStore_SIM requires **all** the files in _universal_functions_ and the files from at least **one case**. Cases are found in the _cases_GB_ and _cases_IE_ folders.

**NB.** the scripts assume that you're using the same file structure as the repo; when downloading file from this repo, it is important that you keep the same file structure (or else make appropriate edits to the code).

\
\
**How do I start using NStore_SIM?**

There are two key scripts within each case folder: **main** and **monitor**.

_Main_ is the script that initiates the optimisation.

_Monitor_ allows you to inspect an ongoing or previous optimisation, and can provide a full cost breakdown of an individual function evaluation. **NB.** by default _monitor_ inspects the **most recently edited** outputs file in its folder.

Run both of these scripts as you would any other Python script.

\
\
The scripts found in this repository are translations from the original MATLAB scripts. The original scripts, along with more detailed instructions and demos, can be found at the following link:

https://www.era.ac.uk/resources/nstore_sim/

While the instructions at the above link are for MATLAB, they remain broadly applicable to this repository.
