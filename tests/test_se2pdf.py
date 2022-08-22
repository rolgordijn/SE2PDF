from SE2pdf.se2pdf  import *


def test_filename_from_path():
    pass

def test_that_fails():
    assert 1 == 5

def test_change_extension():
    output = changeFileExtensionToPDF("file.dft")
    assert output == "file.pdf"