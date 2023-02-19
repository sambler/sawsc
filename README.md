
This is **SawsC**

Pronounced "Saucy"

SawsC is Shane's AWS Configurator, which is a collection of tkinter classes that use boto3 to build a GUI based assistant for developing and maintaining AWS resources.

Each component is a subclass of ttk.Frame, it holds the settings available for its resource, adjusts the settings based on choice of development or production and knows how to query, create and update the designated resource.



Run tests
```sh
python -m unittest
```

or run test with all python versions
```sh
tox
```

View coverage report after tox
```sh
firefox htmlcov/index.html
```

install into home bin

```sh
python setup.py develop --install-dir=~/bin/pymodules
```
