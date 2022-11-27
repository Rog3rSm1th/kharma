import re
import kharma.app.utils.regexer as regexer
import kharma.app

regexer = regexer.Regexer()
kharma = kharma.app.Kharma("./tests/test_templates/test_template.kg")  # type: ignore

# Regexer unit tests
def test_regexer_string_html_tag():
    html_tag_regexp = r"<\/?[\w\s]*>|<.+[\W]>"
    generated_string = regexer.generate_string(html_tag_regexp)
    print(re.match(re.compile(html_tag_regexp), generated_string))


def test_regexer_string_ipv4():
    ipv4_regexp = (
        r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    )
    generated_string = regexer.generate_string(ipv4_regexp)
    print(re.match(re.compile(ipv4_regexp), generated_string))


def test_regexer_string_date():
    date_regexp = r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))"
    generated_string = regexer.generate_string(date_regexp)
    print(re.match(re.compile(date_regexp), generated_string))


# Kharma core unit tests
def test_kharma_const_vanilla():
    const_vanilla = [anchor for anchor in kharma.anchors if anchor.name == "const_vanilla"][0].value
    evaluated_expression = kharma._resolve(const_vanilla)
    assert evaluated_expression == "const vanilla"


def test_kharma_variable_vanilla():
    variable_vanilla = [anchor for anchor in kharma.anchors if anchor.name == "variable_vanilla"][0].value
    evaluated_expression = kharma._resolve(variable_vanilla)
    assert evaluated_expression == "variable vanilla"


def test_kharma_variable_anchor_variable():
    variable_anchor_variable = [anchor for anchor in kharma.anchors if anchor.name == "variable_anchor_variable"][
        0
    ].value
    evaluated_expression = kharma._resolve(variable_anchor_variable)
    assert evaluated_expression == "variable vanilla"


def test_kharma_variable_element():
    variable_element = [anchor for anchor in kharma.anchors if anchor.name == "variable_element"][0].value
    evaluated_expression = kharma._resolve(variable_element)
    assert evaluated_expression == "element_0 element_1"


def test_kharma_variable_element_id():
    variable_element_id = [anchor for anchor in kharma.anchors if anchor.name == "variable_element_id"][0].value
    evaluated_expression = kharma._resolve(variable_element_id)
    assert evaluated_expression == "element_id_0 element_id_1 element_id_0 element_id_2"


def test_kharma_variable_anchor_import_constant():
    variable_anchor_import_constant = [
        anchor for anchor in kharma.anchors if anchor.name == "variable_anchor_import_constant"
    ][0].value
    evaluated_expression = kharma._resolve(variable_anchor_import_constant)
    assert evaluated_expression == "imported constant"


def test_kharma_variable_anchor_import_variable():
    variable_anchor_import_variable = [
        anchor for anchor in kharma.anchors if anchor.name == "variable_anchor_import_variable"
    ][0].value
    evaluated_expression = kharma._resolve(variable_anchor_import_variable)
    assert evaluated_expression == "imported variable"


def test_kharma_variable_anchor_import_function():
    variable_anchor_import_function = [
        anchor for anchor in kharma.anchors if anchor.name == "variable_anchor_import_function"
    ][0].value
    evaluated_expression = kharma._resolve(variable_anchor_import_function)
    assert evaluated_expression == "7"


def test_kharma_variable_function():
    variable_function = [anchor for anchor in kharma.anchors if anchor.name == "variable_function"][0].value
    evaluated_expression = kharma._resolve(variable_function)
    assert evaluated_expression == "12"


def test_kharma_variable_regexp():
    variable_regexp = [anchor for anchor in kharma.anchors if anchor.name == "variable_regexp"][0].value
    evaluated_expression = kharma._resolve(variable_regexp)
    assert re.match(re.compile("[A-Za-z0-9]+"), evaluated_expression)


def test_kharma_variable_range():
    variable_range = [anchor for anchor in kharma.anchors if anchor.name == "variable_range"][0].value
    evaluated_expression = kharma._resolve(variable_range)
    assert 42 <= int(evaluated_expression) <= 1337


def test_kharma_variable_repeat():
    variable_repeat = [anchor for anchor in kharma.anchors if anchor.name == "variable_repeat"][0].value
    evaluated_expression = kharma._resolve(variable_repeat)
    assert re.match(re.compile("(looped string){1,5}"), evaluated_expression)


def test_kharma_variable_repeat_nodup():
    variable_repeat_nodup = [anchor for anchor in kharma.anchors if anchor.name == "variable_repeat_no_dup"][0].value
    evaluated_expression = kharma._resolve(variable_repeat_nodup)
    assert re.match(re.compile("(looped string){1}"), evaluated_expression)


def test_kharma_variable_repeat_separator():
    variable_repeat_nodup = [anchor for anchor in kharma.anchors if anchor.name == "variable_repeat_no_dup"][0].value
    evaluated_expression = kharma._resolve(variable_repeat_nodup)
    assert re.match(re.compile("(looped string)(,looped string){0,4}"), evaluated_expression)


def test_main():
    main = kharma.main.value
    evaluated_expression = kharma._resolve(main)
    assert evaluated_expression == "variable vanilla"
