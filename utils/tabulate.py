'''
Util to format a long list into an easily readable table
'''


def tabulate(data: list[str], pad: int, line_size: int) -> list[str]:
    '''
    Turn a list into a string, format as a table with equal space between each element

    :param data: The data to format
    :type data: list[str]
    :param pad: The amount of spaces to put between each item
    :type pad: int
    :param line_size: the maximum length of a line. -1 to put each item on a new line
    :type line_size: int
    :return: A list of strings, which each represent a line
    :rtype: list[str]
    '''
    # get longest element of data
    longest = max(len(i) for i in data)

    out: list[str] = []
    line = ''

    for i in data:
        # calculate spaces needed to make cell same size as other cells
        space = longest - len(i) + pad

        # if line+cell+space is longer than line_size, start new line
        if len(line + i) + space > line_size:
            out.append(line.strip())
            line = ''

        line += i + ' ' * space

    out.append(line.strip())

    return out
