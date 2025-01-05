from cx_Freeze import setup, Executable


# Inclure les fichiers supplémentaires (comme reponces.txt et icone.ico)
files = ['CompilerRexi.py', 'InterpreterRexi.py' , 'parser.out' ,'parsetab.py']  # Ajouter ici les fichiers nécessaires

setup(
    name="Rexi IDE",
    version="1.0",
    description="an personnel interpreted programming langugue ",
    options={"build_exe": {"include_files": files}},
    executables=[
        Executable(
            "../ide.py",  # Remplacez par le nom de votre fichier principal
            base="Win32GUI",
            icon="logo-rexi-tr.ico"  # Spécifiez le fichier icône ici
        )
    ]
)
