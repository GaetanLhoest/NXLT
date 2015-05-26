operations = {
    '+' : lambda x,y: x+y,
    '-' : lambda x,y: x-y,
    '*' : lambda x,y: x*y,
    '/' : lambda x,y: x/y,
    '>' : lambda x,y: x>y,
}

operations_assign = {
    '+=' : lambda x,y,assign: operations['+'](x,y)+assign,
    '-=' : lambda x,y,assign: operations['-'](x,y)+assign,
    '*=' : lambda x,y,assign: operations['*'](x,y)+assign,
    '/=' : lambda x,y,assign: operations['/'](x,y)+assign
}


