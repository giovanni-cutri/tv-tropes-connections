# TV Tropes Connections
 
Find a possible path (which may not be the shortest) between two works on [TV Tropes](https://tvtropes.org/) based on the common tropes they feature, using the depth-first search algorithm.

Inspired by [this](https://cs50.harvard.edu/ai/2020/projects/0/degrees/) CS50 Project.

# Usage

- Clone this repository to your local machine.
- Ensure that you have installed Python.
- Install the dependencies listed in *requirements.txt*.
  
  ````
  pip install -r requirements.txt
  ````
- Run *tv_tropes_connections.py*.

You will be prompted to provide the TV Tropes URL of the initial work and the final work.

Alternatively, you can provide the aforementioned information as two command-line arguments, like this:

````
python tv_tropes_connections.py [initial_work] [final_work]
````

# License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/giovanni-cutri/tv-tropes-connections/blob/main/LICENSE) file for details.
