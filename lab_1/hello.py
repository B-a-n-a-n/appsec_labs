import typer

# main program loop
def main(
    # used parameters
    name: str,
    lastname: str = typer.Option("", help="Фамилия пользователя."),
    formal: bool = typer.Option(False, "--formal", "-f", help="Использовать формальное приветствие."),
):
    """
    Говорит "Привет" пользователю, опционально используя фамилию и формальный стиль.
    """
    # Check if formal greeting is needed
    if formal:
        # Give greetings with name and surname
        print(f"Добрый день, {name} {lastname}!")
    else:
        # Give greetings with name
        print(f"Привет, {name}!")

if __name__ == "__main__":
    typer.run(main)
