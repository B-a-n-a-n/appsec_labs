import typer

def main(
    user_name: str,
    user_lastname: str = typer.Option("", help="Фамилия пользователя."),
    is_formal: bool = typer.Option(False, "--formal", "-f", help="Использовать формальное приветствие."),
):
    """
    Говорит "Привет" пользователю, опционально используя фамилию и формальный стиль. (updated)
    """
    if is_formal:
        print(f"Добрый день, {user_name} {user_lastname}!")
    else:
        print(f"Привет, {user_name}!")

if __name__ == "__main__":
    typer.run(main)
