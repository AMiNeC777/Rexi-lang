import Langugue

while True :
    text = input('shell >')
    tokens , error = Langugue.run('gg<stdin>' ,text)
    if error : print(error.as_string())
    else:print(tokens)




