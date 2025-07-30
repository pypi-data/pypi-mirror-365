# cppast

This tool serves mainly serves the purpose of generating and experimenting with AST of C/C++ code. Additional features included in cpast --help as follows:

![](https://github.com/quarktetra23/cppast/raw/main/images/cmdhelp.png)

Functionality:

![](https://github.com/quarktetra23/cppast/raw/main/images/combined.jpeg)

The above AST and graph are for the following C++ code-

```
bool verify(int y) {
    if (y > 0) {
        if (y < 10) {
            return true;
        }
    }
    return false;
}
```

## Install through pip

Simply go with ```$ pip install cppast```.

## Install cppast through source code

Clone the github repo and to install the dependencies run:

```
$ pip install -r requirements.txt
```

Additionally, you would need ```$ brew install llvm libclang``` for some of the functions in cli.py.
