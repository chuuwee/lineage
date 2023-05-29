from rich.markdown import Markdown
from rich.console import Console

console = Console()

def readme():
  with open('README.md', 'r') as f:
    content = f.read()
  md = Markdown(content)
  with console.pager():
    console.print("=============>>>>> PRESS 'Q' TO EXIT. <<<<<=============", justify='center')
    console.print(md)
    console.print("=============>>>>> PRESS 'Q' TO EXIT. <<<<<=============", justify='center')

if __name__ == "__main__":
  readme()