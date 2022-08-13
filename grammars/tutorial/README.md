Kharmas templates are based on the [YAML](https://wikipedia.org/wiki/YAML) format and are divided into different sections.

### Comments

```yaml
# This is a comment

# This is a 
# Multi-line comment
```
### Imports (optional section)

It is possible to import variables, constants and functions defined in other templates using the **imports** section.

``` yaml
imports:
    # You must specify the import name as well as the relative path of the template
    import: "import.kg"
```

### Functions (optional section)

The **function** section allows you to define python functions inside your template.

```yaml
functions:
    # Here we define the "multiply" function.
    multiply: |
                <%python (factor_1, factor_2)
                    factor_1_int = int(factor_1)
                    factor_2_int = int(factor_2)
                    product = factor_1_int*factor_2_int
                    return product
                %>
```

### Constants (optional)

The **consts** section allows to define values with only one possible value. Constants can use references to variables and vice versa.

```yaml
consts:
    const_0: "This is a constant"
    const_1: |
             Multiple lines
             constant
    const_2: "++import:int8++"
    const_3: "++variable_0++"
    const_4: "++const_0++"
    const_5: "@@element_@@"
    const_6: "[%%range%%](0, 1337)"
    const_7: "[%%regexp:[A-Za-z0-9]+%%]"
    const_8: "[%%call~multiply%%](3, 4)"
    const_9: "[##repeat:1:5:dup:##]{%looped string%}"
```

#### Variables (optional)

The **variables** section allows you to define values with several possible values.

```yaml
variables:
    # A variable can have several possible values
    variable_0: 
        - "double quoted variable"
        - 'single quoted variable'
        - "Unicode string: \u0398\u039f\u03b4"
        - "Hexadecimal string: \x49\x4a\x4b"
        - |
            variable can be written 
            on multiples
            lines !
    
    # An anchor is a reference to another variable
    variable_anchor:
        # The anchor will be replaced by one of the possibles values of the variable
        - "++variable_0++"
    
    # Variable can use references to constants
    variable_const_anchor:
        - "++const_0++"
        - "++const_1++"
        - "++const_2++"
        - "++const_3++"
        - "++const_4++"
        - "++const_5++"
        - "++const_6++"
        - "++const_7++"
        - "++const_8++"
        - "++const_9++"
    
    # You can access variables/consts defined in imported files
    variable_import_anchor:
        - "++import:int8++"
        - "++import:uint8++"
        - "++import:int16++"
        - "++import:uint16++"
        - "++import:int32++"
        - "++import:uint32++"
        - "++import:int32++"
        - "++import:uint32++"
    
    # An element has a name and a counter.
    variable_element:
        # The first time we call it, the result will be "element_0", the next time
        # "element_1", and so on
        - "@@element_@@"
    
    # Selection of a random value within the range
    variable_range:
        - "[%%range%%](0, 1337)"
        - "[%%range%%](-100, 100)"
        - "[%%range%%](-infinity, infinity)"
        
    # Generate a random valid input for the regular expression
    variable_regexp:
        - "[%%regexp:[A-Za-z0-9]+%%]"
    
    # Calls a function defined within the template and gets the return value
    variable_call:
        - "[%%call~multiply%%](3, 4)"
        - "[%%call~multiply%%](++import:int8++, ++import:int8++)"
        - "[%%call~multiply%%]([%%range%%](-100, 100), [%%range%%](-infinity, infinity))"

    # Calls a function defined in an imported template and gets the return value
    variable_import_call:
        - "[%%call~import:sum%%](3, 4)"
        - "[%%call~import:sum%%](++import:int8++, ++import:int8++)"
        - "[%%call~import:sum%%]([%%range%%](-100, 100), [%%range%%](-infinity, infinity))"

    # Loop a string
    variable_loop:
        # Repeat a string between 1 and 5 times
        - "[##repeat:1:5:dup:##]{%looped string%}"
        # Use a custom separator
        - "[##repeat:1:5:dup:, ##]{%looped string%}"
        # Repeat an anchor
        - "[##repeat:1:5:dup:##]{%++variable_anchor++%}"
        # Remove duplicates
        - "[##repeat:1:5:nodup:##]{%++variable_anchor++%}"
        # Repeat an imported anchor
        - "[##repeat:1:5:dup:##]{%++variable_import_anchor++%}"
        # Repeat an element reference
        - "[##repeat:1:5:dup:##]{%++variable_element++%}"
        # Repeat a range statement
        - "[##repeat:1:5:dup:##]{%[%%range%%](-100, 100)%}"
        # Repeat a regexp statement
        - "[##repeat:1:5:dup:##]{%++variable_regexp++%}"
        
    # It is possible to define a static variable by giving it a name starting 
    # with "static_"
    # A static variable will be evaluated only once and will take the
    # same value at each call
    static_variable:
        - "this is a static value"
        - "++import:int8++"
        - "@@element_@@"
        - "[%%range%%](0, 1337)"
        - "[%%regexp:[A-Za-z0-9]+%%]"
        - "[%%call~multiply%%](3, 4)"
        - "[##repeat:1:5:dup:##]{%looped string%}"
    
    # It is possible to use several statements/references
    several_statements_variables:
        - "++variable_0++ ++import:int8++ @@element_@@ [%%range%%](0, 1337) [%%regexp:[A-Za-z0-9]+%%] [%%call~multiply%%](3, 4) [##repeat:1:5:dup:##]{%looped string%}"
```

### Variance (optional)

The **variance** section contains the **main** variable which is the entry point of the template.

```yaml
variance:
    # Main is the entry point of the template
    # it works like a regular variable
    main:
        # Happy template generating ! ヽ(o＾▽＾o)ノ
        - "++several_statements_variables++"
```

-> The order in which the sections are defined is **not important** and all sections are **optionals**.